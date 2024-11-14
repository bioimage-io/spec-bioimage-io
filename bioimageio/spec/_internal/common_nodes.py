from __future__ import annotations

import collections.abc
import traceback
from abc import ABC, abstractmethod
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from typing import (
    IO,
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    Generic,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    Union,
    cast,
    get_type_hints,
)
from zipfile import ZipFile

import pydantic
from pydantic import (
    DirectoryPath,
    Field,
    GetCoreSchemaHandler,
    PrivateAttr,
    StringConstraints,
    TypeAdapter,
    model_validator,
)
from pydantic_core import PydanticUndefined, core_schema
from typing_extensions import (
    Annotated,
    LiteralString,
    Self,
    TypeVar,
    TypeVarTuple,
    Unpack,
)

from ..summary import (
    WARNING_LEVEL_TO_NAME,
    ErrorEntry,
    ValidationContextSummary,
    ValidationDetail,
    ValidationSummary,
    WarningEntry,
)
from .field_warning import issue_warning
from .io import BioimageioYamlContent
from .io_basics import BIOIMAGEIO_YAML, AbsoluteFilePath, FileName, ZipPath
from .io_utils import write_content_to_zip
from .node import Node
from .packaging_context import PackagingContext
from .url import HttpUrl
from .utils import (
    assert_all_params_set_explicitly,
    get_format_version_tuple,
)
from .validation_context import (
    ValidationContext,
    validation_context_var,
)
from .warning_levels import ALERT, ERROR, INFO


class StringNode(collections.UserString, ABC):
    """deprecated! don't use for new spec fields!"""

    _pattern: ClassVar[str]
    _node_class: Type[Node]
    _node: Optional[Node] = None

    def __init__(self, seq: object) -> None:
        super().__init__(seq)
        type_hints = {
            fn: t
            for fn, t in get_type_hints(self.__class__).items()
            if not fn.startswith("_")
        }
        defaults = {fn: getattr(self.__class__, fn, Field()) for fn in type_hints}
        field_definitions: Dict[str, Any] = {
            fn: (t, defaults[fn]) for fn, t in type_hints.items()
        }
        self._node_class = pydantic.create_model(
            self.__class__.__name__,
            __base__=Node,
            __module__=self.__module__,
            **field_definitions,
        )

        # freeze after initialization
        def __setattr__(self: Self, __name: str, __value: Any):  # type: ignore
            raise AttributeError(f"{self} is immutable.")

        self.__setattr__ = __setattr__  # type: ignore

    @property
    def model_fields(self):
        return self._node_class.model_fields

    def __getattr__(self, name: str):
        if name in self._node_class.model_fields:
            if self._node is None:
                raise AttributeError(f"{name} only available after validation")

            return getattr(self._node, name)

        raise AttributeError(name)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        assert issubclass(source, StringNode), source
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(pattern=cls._pattern),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def _get_data(cls, valid_string_data: str) -> Dict[str, Any]:
        raise NotImplementedError(f"{cls.__name__}._get_data()")

    @classmethod
    def _validate(cls, value: str) -> Self:
        constrained_str_type = Annotated[str, StringConstraints(pattern=cls._pattern)]
        constrained_str_adapter: TypeAdapter[str] = TypeAdapter(constrained_str_type)
        valid_string_data = constrained_str_adapter.validate_python(value)
        data = cls._get_data(valid_string_data)
        self = cls(valid_string_data)
        object.__setattr__(self, "_node", self._node_class.model_validate(data))
        return self

    def _serialize(self) -> str:
        # serialize inner node to call _package when needed
        if self._node is not None:
            _ = self._node.model_dump(mode="json")

        return self.data


SRC = TypeVar("SRC", bound=Union[Node, StringNode])
TGT = TypeVar("TGT", bound=Node)


# converter without any additional args or kwargs:
# class Converter(Generic[SRC, TGT], ABC):
#     # src: ClassVar[Type[SRC]]
#     # tgt: ClassVar[Type[TGT]]
#     # note: the above is not yet possible, see https://github.com/python/typing/discussions/1424
#     # we therefore use an instance
#     def __init__(self, src: Type[SRC], tgt: Type[TGT], /):
#         super().__init__()
#         self.src: Final[Type[SRC]] = src
#         self.tgt: Final[Type[TGT]] = tgt

#     @abstractmethod
#     def _convert(self, src: SRC, tgt: "type[TGT | dict[str, Any]] ", /) -> "TGT | dict[str, Any]":
#         ...

#     def convert(self, source: SRC, /) -> TGT:
#         """convert `source` node

#         Args:
#             source: A bioimageio description node

#         Raises:
#             ValidationError: conversion failed
#         """
#         data = self.convert_as_dict(source)
#         return assert_all_params_set_explicitly(self.tgt)(**data)

#     def convert_as_dict(self, source: SRC) -> Dict[str, Any]:
#         return cast(Dict[str, Any], self._convert(source, dict))


# A TypeVar bound to a TypedDict seemed like a good way to add converter kwargs:
# ```
# class ConverterKwargs(TypedDict):
#     pass
# KW = TypeVar("KW", bound=ConverterKwargs, default=ConverterKwargs)
# ```
# sadly we cannot use a TypeVar bound to TypedDict and then unpack it in the Converter methods,
# see https://github.com/python/typing/issues/1399
# Therefore we use a TypeVarTuple and positional only args instead
# (We are avoiding ParamSpec for its ambiguity 'args vs kwargs')
CArgs = TypeVarTuple("CArgs")


class Converter(Generic[SRC, TGT, Unpack[CArgs]], ABC):
    # src: ClassVar[Type[SRC]]
    # tgt: ClassVar[Type[TGT]]
    # note: the above is not yet possible, see https://github.com/python/typing/discussions/1424
    # we therefore use an instance
    def __init__(self, src: Type[SRC], tgt: Type[TGT], /):
        super().__init__()
        self.src: Final[Type[SRC]] = src
        self.tgt: Final[Type[TGT]] = tgt

    @abstractmethod
    def _convert(
        self, src: SRC, tgt: "type[TGT | dict[str, Any]]", /, *args: Unpack[CArgs]
    ) -> "TGT | dict[str, Any]": ...

    # note: the following is not (yet) allowed, see https://github.com/python/typing/issues/1399
    #       we therefore use `kwargs` (and not `**kwargs`)
    # def convert(self, source: SRC, /, **kwargs: Unpack[KW]) -> TGT:
    def convert(self, source: SRC, /, *args: Unpack[CArgs]) -> TGT:
        """convert `source` node

        Args:
            source: A bioimageio description node

        Raises:
            ValidationError: conversion failed
        """
        data = self.convert_as_dict(source, *args)
        return assert_all_params_set_explicitly(self.tgt)(**data)

    def convert_as_dict(self, source: SRC, /, *args: Unpack[CArgs]) -> Dict[str, Any]:
        return cast(Dict[str, Any], self._convert(source, dict, *args))


class NodeWithExplicitlySetFields(Node):
    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset()
    """set set these fields explicitly with their default value if they are not set,
    such that they are always included even when dumping with 'exlude_unset'"""

    @model_validator(mode="before")
    @classmethod
    def set_fields_explicitly(
        cls, data: Union[Any, Dict[str, Any]]
    ) -> Union[Any, Dict[str, Any]]:
        if isinstance(data, dict):
            for name in cls.fields_to_set_explicitly:
                if name not in data:
                    data[name] = cls.model_fields[name].get_default(
                        call_default_factory=True
                    )

        return data  # pyright: ignore[reportUnknownVariableType]


if TYPE_CHECKING:

    class _ResourceDescrBaseAbstractFieldsProtocol(Protocol):
        """workaround to add abstract fields to ResourceDescrBase"""

        # TODO: implement as proper abstract fields of ResourceDescrBase

        type: Any  # should be LiteralString
        format_version: Any  # should be LiteralString

else:

    class _ResourceDescrBaseAbstractFieldsProtocol:
        pass


class ResourceDescrBase(
    NodeWithExplicitlySetFields, ABC, _ResourceDescrBaseAbstractFieldsProtocol
):
    """base class for all resource descriptions"""

    _validation_summary: Optional[ValidationSummary] = None

    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset(
        {"type", "format_version"}
    )
    implemented_format_version: ClassVar[str]
    implemented_format_version_tuple: ClassVar[Tuple[int, int, int]]

    # @field_validator("format_version", mode="before", check_fields=False)
    # field_validator on "format_version" is not possible, because we want to use
    #   "format_version" in a descriminated Union higher up
    # (PydanticUserError: Cannot use a mode='before' validator in the discriminator
    #   field 'format_version' of Model 'CollectionDescr')
    @model_validator(mode="before")
    @classmethod
    def _ignore_future_patch(cls, data: Union[Dict[Any, Any], Any], /) -> Any:
        if (
            cls.implemented_format_version == "unknown"
            or not isinstance(data, dict)
            or "format_version" not in data
        ):
            return data  # pyright: ignore[reportUnknownVariableType]

        value: Any = data["format_version"]
        fv = get_format_version_tuple(value)
        if fv is None:
            return data  # pyright: ignore[reportUnknownVariableType]

        if (
            fv[0] == cls.implemented_format_version_tuple[0]
            and fv[1:] > cls.implemented_format_version_tuple[1:]
        ):
            issue_warning(
                "future format_version '{value}' treated as '{implemented}'",
                value=value,
                msg_context=dict(implemented=cls.implemented_format_version),
                severity=ALERT,
            )
            data["format_version"] = cls.implemented_format_version

        return data  # pyright: ignore[reportUnknownVariableType]

    @model_validator(mode="after")
    def _set_init_validation_summary(self) -> Self:
        context = validation_context_var.get()
        self._validation_summary = ValidationSummary(
            name="bioimageio format validation",
            source_name=context.source_name,
            type=self.type,
            format_version=self.format_version,
            status="failed" if isinstance(self, InvalidDescr) else "passed",
            details=[
                ValidationDetail(
                    name=f"initialized {self.__class__.__name__} to describe {self.type} {self.implemented_format_version}",
                    status="passed",
                    context=None,  # context for format validation detail is identical
                )
            ],
        )
        return self

    @property
    def validation_summary(self) -> ValidationSummary:
        assert self._validation_summary is not None, "access only after initialization"
        return self._validation_summary

    _root: Union[HttpUrl, DirectoryPath] = PrivateAttr(
        default_factory=lambda: validation_context_var.get().root
    )

    @property
    def root(self) -> Union[HttpUrl, DirectoryPath]:
        return self._root

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any):
        super().__pydantic_init_subclass__(**kwargs)
        if (
            "format_version" in cls.model_fields
            and cls.model_fields["format_version"].default is not PydanticUndefined
        ):
            cls.implemented_format_version = cls.model_fields["format_version"].default
            if "." not in cls.implemented_format_version:
                cls.implemented_format_version_tuple = (0, 0, 0)
            else:
                fv_tuple = get_format_version_tuple(cls.implemented_format_version)
                assert (
                    fv_tuple is not None
                ), f"failed to cast '{cls.implemented_format_version}' to tuple"
                cls.implemented_format_version_tuple = fv_tuple

    @classmethod
    def load(
        cls, data: BioimageioYamlContent, context: Optional[ValidationContext] = None
    ) -> Union[Self, InvalidDescr]:
        context = context or validation_context_var.get()
        assert isinstance(data, dict)
        with context.replace(log_warnings=False):  # don't log warnings to console
            rd, errors, val_warnings = cls._load_impl(deepcopy(data))

        if context.warning_level > INFO:
            all_warnings_context = context.replace(warning_level=INFO)
            # raise all validation warnings by reloading
            with all_warnings_context:
                _, _, val_warnings = cls._load_impl(deepcopy(data))

        rd.validation_summary.add_detail(
            ValidationDetail(
                errors=errors,
                name=(
                    "bioimageio.spec format validation"
                    f" {rd.type} {cls.implemented_format_version}"
                ),
                status="failed" if errors else "passed",
                warnings=val_warnings,
                context=ValidationContextSummary(
                    perform_io_checks=context.perform_io_checks,
                    known_files=context.known_files,
                    root=str(context.root),
                    warning_level=WARNING_LEVEL_TO_NAME[context.warning_level],
                ),
            )
        )

        return rd

    @classmethod
    def _load_impl(
        cls, data: BioimageioYamlContent
    ) -> Tuple[Union[Self, InvalidDescr], List[ErrorEntry], List[WarningEntry]]:
        rd: Union[Self, InvalidDescr, None] = None
        val_errors: List[ErrorEntry] = []
        val_warnings: List[WarningEntry] = []

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
                else:
                    val_errors.append(
                        ErrorEntry(loc=ee["loc"], msg=ee["msg"], type=ee["type"])
                    )

            if len(val_errors) == 0:
                val_errors.append(
                    ErrorEntry(
                        loc=(),
                        msg=(
                            f"Encountered {len(val_warnings)} more severe than warning"
                            " level "
                            f"'{WARNING_LEVEL_TO_NAME[validation_context_var.get().warning_level]}'"
                        ),
                        type="severe_warnings",
                    )
                )
        except Exception as e:
            val_errors.append(
                ErrorEntry(
                    loc=(),
                    msg=str(e),
                    type=type(e).__name__,
                    traceback=traceback.format_tb(e.__traceback__),
                )
            )

        if rd is None:
            try:
                rd = InvalidDescr.model_validate(data)
            except Exception:
                resource_type = cls.model_fields["type"].default
                format_version = cls.implemented_format_version
                rd = InvalidDescr(type=resource_type, format_version=format_version)

        return rd, val_errors, val_warnings

    def package(
        self, dest: Optional[Union[ZipFile, IO[bytes], Path, str]] = None, /
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

        content = self.get_package_content()
        write_content_to_zip(content, zip)
        return zip

    def get_package_content(
        self,
    ) -> Dict[
        FileName, Union[HttpUrl, AbsoluteFilePath, BioimageioYamlContent, ZipPath]
    ]:
        """Returns package content without creating the package."""
        content: Dict[FileName, Union[HttpUrl, AbsoluteFilePath, ZipPath]] = {}
        with PackagingContext(
            bioimageio_yaml_file_name=BIOIMAGEIO_YAML,
            file_sources=content,
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

    type: Any = "unknown"
    format_version: Any = "unknown"
    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset()


class KwargsNode(Node):
    def get(self, item: str, default: Any = None) -> Any:
        return self[item] if item in self else default

    def __getitem__(self, item: str) -> Any:
        if item in self.model_fields:
            return getattr(self, item)
        else:
            raise KeyError(item)

    def __contains__(self, item: str) -> int:
        return item in self.model_fields
