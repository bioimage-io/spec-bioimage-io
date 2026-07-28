from __future__ import annotations

from abc import ABC
from inspect import signature
from io import BytesIO
from pathlib import Path
from types import MappingProxyType
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Iterable,
    Literal,
    Mapping,
    Protocol,
    TypeVar,
)
from zipfile import ZipFile

import pydantic
from pydantic import DirectoryPath, PrivateAttr, model_validator
from pydantic_core import PydanticUndefined
from typing_extensions import ParamSpec, Self

from ..summary import (
    WARNING_LEVEL_TO_NAME,
    ErrorEntry,
    ValidationDetail,
    ValidationSummary,
    WarningEntry,
)
from .field_warning import issue_warning
from .io import (
    BioimageioYamlContent,
    FileDescr,
    IncompleteDescr,
    IncompleteDescrView,
    deepcopy_incomplete_descr,
    extract_file_descrs,
    populate_cache,
)
from .io_basics import BIOIMAGEIO_YAML, FileName
from .io_utils import write_content_to_zip
from .node import Node
from .packaging_context import PackagingContext
from .root_url import RootHttpUrl
from .type_guards import is_dict
from .utils import get_format_version_tuple
from .validation_context import ValidationContext, get_validation_context
from .warning_levels import ALERT, ERROR, INFO


class NodeWithExplicitlySetFields(Node):
    _fields_to_set_explicitly: ClassVar[Mapping[str, Any]]

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        explict_fields: dict[str, Any] = {}
        for attr in dir(cls):
            if attr.startswith("implemented_"):
                field_name = attr.replace("implemented_", "")
                if field_name not in cls.model_fields:
                    continue

                assert (
                    cls.model_fields[field_name].get_default() is PydanticUndefined
                ), field_name
                default = getattr(cls, attr)
                explict_fields[field_name] = default

        cls._fields_to_set_explicitly = MappingProxyType(explict_fields)
        return super().__pydantic_init_subclass__(**kwargs)

    @model_validator(mode="before")
    @classmethod
    def _set_fields_explicitly(
        cls, data: Any | dict[str, Any]
    ) -> Any | dict[str, Any]:
        if isinstance(data, dict):
            for name, default in cls._fields_to_set_explicitly.items():
                if name not in data:
                    data[name] = default

        return data  # pyright: ignore[reportUnknownVariableType]


if TYPE_CHECKING:

    class _ResourceDescrBaseAbstractFieldsProtocol(Protocol):
        """workaround to add "abstract" fields to ResourceDescrBase"""

        # TODO: implement as proper abstract fields of ResourceDescrBase

        type: Any  # should be LiteralString
        format_version: Any  # should be LiteralString
        implemented_type: ClassVar[Any]
        implemented_format_version: ClassVar[Any]

else:

    class _ResourceDescrBaseAbstractFieldsProtocol:
        pass


P = ParamSpec("P")
T = TypeVar("T")


class ResourceDescrBase(
    NodeWithExplicitlySetFields, ABC, _ResourceDescrBaseAbstractFieldsProtocol
):
    """base class for all resource descriptions"""

    _validation_summary: ValidationSummary | None = None

    implemented_format_version_tuple: ClassVar[tuple[int, int, int]]

    # @field_validator("format_version", mode="before", check_fields=False)
    # field_validator on "format_version" is not possible, because we want to use
    #   "format_version" in a descriminated Union higher up
    # (PydanticUserError: Cannot use a mode='before' validator in the discriminator
    #   field 'format_version' of Model 'CollectionDescr')
    @model_validator(mode="before")
    @classmethod
    def _ignore_future_patch(cls, data: Any, /) -> Any:
        if (
            cls.implemented_format_version == "unknown"
            or not is_dict(data)
            or "format_version" not in data
        ):
            return data

        value = data["format_version"]
        fv = get_format_version_tuple(value)
        if fv is None:
            return data
        if (
            fv[0] == cls.implemented_format_version_tuple[0]
            and fv[1:] > cls.implemented_format_version_tuple[1:]
        ):
            issue_warning(
                "future format_version '{value}' treated as '{implemented}'",
                value=value,
                msg_context={"implemented": cls.implemented_format_version},
                severity=ALERT,
            )
            data["format_version"] = cls.implemented_format_version

        return data

    @model_validator(mode="after")
    def _set_init_validation_summary(self) -> Self:
        context = get_validation_context()

        self._validation_summary = ValidationSummary(
            name="bioimageio format validation",
            source_name=context.source_name,
            id=getattr(self, "id", None),
            version=getattr(self, "version", None),
            type=self.type,
            format_version=self.format_version,
            status="failed" if isinstance(self, InvalidDescr) else "valid-format",
            metadata_completeness=self._get_metadata_completeness(),
            details=(
                []
                if isinstance(self, InvalidDescr)
                else [
                    ValidationDetail(
                        name=f"Successfully created `{self.__class__.__name__}` instance.",
                        status="passed",
                        context=context.summary,
                    )
                ]
            ),
        )
        return self

    @property
    def validation_summary(self) -> ValidationSummary:
        assert self._validation_summary is not None, "access only after initialization"
        return self._validation_summary

    _root: RootHttpUrl | DirectoryPath | ZipFile = PrivateAttr(
        default_factory=lambda: get_validation_context().root
    )

    _file_name: FileName | None = PrivateAttr(
        default_factory=lambda: get_validation_context().file_name
    )

    @property
    def root(self) -> RootHttpUrl | DirectoryPath | ZipFile:
        """The URL/Path prefix to resolve any relative paths with."""
        return self._root

    @property
    def file_name(self) -> FileName | None:
        """File name of the bioimageio.yaml file the description was loaded from."""
        return self._file_name

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any):
        super().__pydantic_init_subclass__(**kwargs)
        # set classvar implemented_format_version_tuple
        if "format_version" in cls.model_fields:
            if "." not in cls.implemented_format_version:
                cls.implemented_format_version_tuple = (0, 0, 0)
            else:
                fv_tuple = get_format_version_tuple(cls.implemented_format_version)
                assert fv_tuple is not None, (
                    f"failed to cast '{cls.implemented_format_version}' to tuple"
                )
                cls.implemented_format_version_tuple = fv_tuple

    @classmethod
    def load_from_kwargs(
        cls: Callable[P, T],
        context: ValidationContext | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T | InvalidDescr:
        sig = signature(cls)
        bound = sig.bind_partial(*args, **kwargs)
        return cls.load(dict(bound.arguments), context=context)  # pyright: ignore[reportFunctionMemberAccess]

    @classmethod
    def load(
        cls,
        data: IncompleteDescrView,
        context: ValidationContext | None = None,
    ) -> Self | InvalidDescr:
        """factory method to create a resource description object"""

        context = context or get_validation_context()
        if context.perform_io_checks:
            file_descrs = extract_file_descrs(data)
            populate_cache(file_descrs)  # TODO: add progress bar

        with context.replace(log_warnings=context.warning_level <= INFO):
            rd, errors, val_warnings = cls._load_impl(deepcopy_incomplete_descr(data))

        if context.warning_level > INFO:
            all_warnings_context = context.replace(
                warning_level=INFO, log_warnings=False, raise_errors=False
            )
            # raise all validation warnings by reloading
            with all_warnings_context:
                _, _, val_warnings = cls._load_impl(deepcopy_incomplete_descr(data))

        format_status = "failed" if errors else "passed"
        rd.validation_summary.add_detail(
            ValidationDetail(
                errors=errors,
                name=(
                    "bioimageio.spec format validation"
                    f" {rd.type} {cls.implemented_format_version}"
                ),
                status=format_status,
                warnings=val_warnings,
            ),
            update_status=False,  # this special validation detail needs manual format updating below
        )
        assert format_status != "failed" or isinstance(rd, InvalidDescr)

        return rd

    def _get_metadata_completeness(self) -> float:
        if isinstance(self, InvalidDescr):
            return 0.0

        given = self.model_dump(mode="json", exclude_unset=True, exclude_defaults=False)
        full = self.model_dump(mode="json", exclude_unset=False, exclude_defaults=False)

        def extract_flat_keys(d: dict[Any, Any], key: str = "") -> Iterable[str]:
            for k, v in d.items():
                if is_dict(v):
                    yield from extract_flat_keys(v, key=f"{key}.{k}" if key else k)

                yield f"{key}.{k}" if key else k

        given_keys = set(extract_flat_keys(given))
        full_keys = set(extract_flat_keys(full))
        assert len(full_keys) >= len(given_keys)
        return len(given_keys) / len(full_keys) if full_keys else 0.0

    @classmethod
    def _load_impl(
        cls, data: IncompleteDescr
    ) -> tuple[Self | InvalidDescr, list[ErrorEntry], list[WarningEntry]]:
        rd: Self | InvalidDescr | None = None
        val_errors: list[ErrorEntry] = []
        val_warnings: list[WarningEntry] = []

        context = get_validation_context()
        try:
            rd = cls.model_validate(data)
        except pydantic.ValidationError as e:
            for ee in e.errors(include_url=False):
                if (severity := ee.get("ctx", {}).get("severity", ERROR)) < ERROR:
                    val_warnings.append(
                        WarningEntry(
                            loc=ee["loc"],
                            msg=ee["msg"],
                            type=ee["type"],
                            severity=severity,
                        )
                    )
                elif context.raise_errors:
                    raise
                else:
                    val_errors.append(
                        ErrorEntry(loc=ee["loc"], msg=ee["msg"], type=ee["type"])
                    )

            if len(val_errors) == 0:  # FIXME is this reduntant?
                val_errors.append(
                    ErrorEntry(
                        loc=(),
                        msg=(
                            f"Encountered {len(val_warnings)} more severe than warning"
                            " level "
                            f"'{WARNING_LEVEL_TO_NAME[context.warning_level]}'"
                        ),
                        type="severe_warnings",
                    )
                )
        except Exception as e:
            if context.raise_errors:
                raise

            try:
                msg = str(e)
            except Exception:
                msg = e.__class__.__name__ + " encountered"

            val_errors.append(
                ErrorEntry(
                    loc=(),
                    msg=msg,
                    type=type(e).__name__,
                    with_traceback=True,
                )
            )

        if rd is None:
            try:
                rd = InvalidDescr.model_validate(data)
            except Exception:
                if context.raise_errors:
                    raise
                resource_type = cls.model_fields["type"].default
                format_version = cls.implemented_format_version
                rd = InvalidDescr(type=resource_type, format_version=format_version)
                if context.raise_errors:
                    raise ValueError(rd)

        return rd, val_errors, val_warnings

    def package(
        self,
        dest: ZipFile | IO[bytes] | Path | str | None = None,
        /,
        local_files_only: bool = False,
    ) -> ZipFile:
        """package the described resource as a zip archive

        Args:
            dest: (path/bytes stream of) destination zipfile
        """
        if dest is None:
            dest = BytesIO()

        if isinstance(dest, ZipFile):
            zip = dest
            if "r" in zip.mode:
                raise ValueError(
                    f"zip file {dest} opened in '{zip.mode}' mode,"
                    + " but write access is needed for packaging."
                )
        else:
            zip = ZipFile(dest, mode="w")

        if zip.filename is None:
            zip.filename = (
                str(getattr(self, "id", getattr(self, "name", "bioimageio"))) + ".zip"
            )

        content = self.get_package_content(local_files_only=local_files_only)
        write_content_to_zip(content, zip)
        return zip

    def get_package_content(
        self, local_files_only: bool = False
    ) -> dict[FileName, FileDescr | BioimageioYamlContent]:
        """Returns package content without creating the package."""
        content: dict[FileName, FileDescr] = {}
        with PackagingContext(
            bioimageio_yaml_file_name=BIOIMAGEIO_YAML,
            file_sources=content,
            local_files_only=local_files_only,
        ):
            rdf_content: BioimageioYamlContent = self.model_dump(
                mode="json", exclude_unset=True
            )

        _ = rdf_content.pop("rdf_source", None)

        return {**content, BIOIMAGEIO_YAML: rdf_content}


class InvalidDescr(
    ResourceDescrBase,
    extra="allow",
    title="An invalid resource description",
):
    """A representation of an invalid resource description"""

    implemented_type: ClassVar[Literal["unknown"]] = "unknown"
    if TYPE_CHECKING:  # see NodeWithExplicitlySetFields
        type: Any = "unknown"
    else:
        type: Any

    implemented_format_version: ClassVar[Literal["unknown"]] = "unknown"
    if TYPE_CHECKING:  # see NodeWithExplicitlySetFields
        format_version: Any = "unknown"
    else:
        format_version: Any

    def get_reason(self) -> str | None:
        """Get the reason why the description is invalid, if available."""
        reasons: list[str] = []
        if self.validation_summary and self.validation_summary.details:
            for detail in self.validation_summary.details:
                if detail.status == "failed" and detail.errors:
                    reasons.extend(
                        f"{loc}: {msg}"
                        for loc, msg in (
                            (
                                ".".join(map(str, error.loc)),
                                error.msg.replace("\n", " "),
                            )
                            for error in detail.errors
                        )
                    )

        return "\n- ".join(reasons) if reasons else None


class KwargsNode(Node):
    def get(self, item: str, default: Any = None) -> Any:
        return self[item] if item in self else default  # ruff: ignore[SIM401]

    def __getitem__(self, item: str) -> Any:
        if item in self.__class__.model_fields:
            return getattr(self, item)
        else:
            raise KeyError(item)

    def __contains__(self, item: str) -> bool:
        return item in self.__class__.model_fields
