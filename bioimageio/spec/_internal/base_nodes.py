from __future__ import annotations

import collections.abc
import traceback
from abc import ABC, abstractmethod
from copy import deepcopy
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
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

import pydantic
from pydantic import (
    AnyUrl,
    DirectoryPath,
    Field,
    GetCoreSchemaHandler,
    PrivateAttr,
    StringConstraints,
    TypeAdapter,
    field_validator,
    model_serializer,
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

from bioimageio.spec._internal.constants import (
    ALERT,
    ALL_BIOIMAGEIO_YAML_NAMES,
    ERROR,
    IN_PACKAGE_MESSAGE,
    INFO,
    VERSION,
    WARNING_LEVEL_TO_NAME,
)
from bioimageio.spec._internal.field_warning import issue_warning
from bioimageio.spec._internal.io_utils import download, get_sha256
from bioimageio.spec._internal.packaging_context import packaging_context_var
from bioimageio.spec._internal.types import BioimageioYamlContent, RelativeFilePath
from bioimageio.spec._internal.types import FileSource as FileSource
from bioimageio.spec._internal.types import Sha256 as Sha256
from bioimageio.spec._internal.types._file_source import extract_file_name
from bioimageio.spec._internal.utils import assert_all_params_set_explicitly
from bioimageio.spec._internal.validation_context import (
    ValidationContext,
    validation_context_var,
)
from bioimageio.spec.summary import ErrorEntry, ValidationSummary, ValidationSummaryDetail, WarningEntry


class Node(
    pydantic.BaseModel,
    extra="forbid",
    frozen=False,
    populate_by_name=True,
    revalidate_instances="always",
    validate_assignment=True,
    validate_default=False,
    validate_return=True,
    # use_attribute_docstrings=True,  TODO: use this from future pydantic 2.7
    # see https://github.com/pydantic/pydantic/issues/5656
):
    """Subpart of a resource description"""

    @classmethod
    def model_validate(
        cls,
        obj: Union[Any, Dict[str, Any]],
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Union[ValidationContext, Dict[str, Any], None] = None,
    ) -> Self:
        """Validate a pydantic model instance.

        Args:
            obj: The object to validate.
            strict: Whether to raise an exception on invalid fields.
            from_attributes: Whether to extract data from object attributes.
            context: Additional context to pass to the validator.

        Raises:
            ValidationError: If the object failed validation.

        Returns:
            The validated description instance.
        """
        __tracebackhide__ = True

        if context is None:
            context = validation_context_var.get()
        elif isinstance(context, dict):
            context = ValidationContext(**context)

        if isinstance(obj, dict):
            assert all(isinstance(k, str) for k in obj), obj

        with context:
            # use validation context as context manager for equal behavior of __init__ and model_validate
            return super().model_validate(obj, strict=strict, from_attributes=from_attributes)

    @model_serializer(mode="wrap")
    def _package(self, nxt: Callable[[Self], Dict[str, Any]]) -> Dict[str, Any]:
        ret = nxt(self)
        if (packaging_context := packaging_context_var.get()) is None:
            return ret

        fsrcs = packaging_context.file_sources
        for field_name, field_value in self:
            if not (self.model_fields[field_name].description or "").startswith(IN_PACKAGE_MESSAGE):
                continue

            if isinstance(field_value, RelativeFilePath):
                src = field_value.absolute
            elif isinstance(field_value, AnyUrl):
                src = field_value
            elif isinstance(field_value, Path):
                src = field_value.resolve()
            else:
                raise NotImplementedError(f"Package field of type {type(field_value)} not implemented.")

            fname = extract_file_name(src)
            assert not any(fname.endswith(special) for special in ALL_BIOIMAGEIO_YAML_NAMES), fname
            if fname in fsrcs and fsrcs[fname] != src:
                for i in range(2, 20):
                    fn, *ext = fname.split(".")
                    alternative_file_name = ".".join([f"{fn}_{i}", *ext])
                    if alternative_file_name not in fsrcs or fsrcs[alternative_file_name] == src:
                        fname = alternative_file_name
                        break
                else:
                    raise RuntimeError(f"Too many file name clashes for {fname}")

            fsrcs[fname] = src
            ret[field_name] = fname

        return ret


class StringNode(collections.UserString, ABC):
    """deprecated! don't use for new spec fields!"""

    _pattern: ClassVar[str]
    _node_class: Type[Node]
    _node: Optional[Node] = None

    def __init__(self: Self, seq: object) -> None:
        super().__init__(seq)
        type_hints = {fn: t for fn, t in get_type_hints(self.__class__).items() if not fn.startswith("_")}
        defaults = {fn: getattr(self.__class__, fn, Field()) for fn in type_hints}
        field_definitions: Dict[str, Any] = {fn: (t, defaults[fn]) for fn, t in type_hints.items()}
        self._node_class = pydantic.create_model(
            self.__class__.__name__,
            __base__=Node,
            __module__=self.__module__,
            **field_definitions,
        )

        # freeze after initialization
        def __setattr__(self: Self, __name: str, __value: Any):
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
    def __get_pydantic_core_schema__(cls, source: Type[Any], handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
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
        contrained_str_type = Annotated[str, StringConstraints(pattern=cls._pattern)]
        contrained_str_adapter = TypeAdapter(cast(str, contrained_str_type))
        valid_string_data = contrained_str_adapter.validate_python(value)
        data = cls._get_data(valid_string_data)
        self = cls(valid_string_data)
        object.__setattr__(self, "_node", self._node_class.model_validate(data))
        return self

    def _serialize(self) -> str:
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
    def _convert(self, src: SRC, tgt: "type[TGT | dict[str, Any]]", /, *args: Unpack[CArgs]) -> "TGT | dict[str, Any]":
        ...

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
    def set_fields_explicitly(cls, data: Union[Any, Dict[str, Any]]) -> Union[Any, Dict[str, Any]]:
        if isinstance(data, dict):
            for name in cls.fields_to_set_explicitly:
                if name not in data:
                    data[name] = cls.model_fields[name].get_default(call_default_factory=True)

        return data


if TYPE_CHECKING:

    class _ResourceDescriptionBaseAbstractFieldsProtocol(Protocol):
        """workaround to add abstract fields to ResourceDescriptionBase"""

        # TODO: implement as proper abstract fields of ResourceDescriptionBase

        type: Any  # should be LiteralString
        format_version: Any  # should be LiteralString

else:

    class _ResourceDescriptionBaseAbstractFieldsProtocol:
        pass


class ResourceDescriptionBase(NodeWithExplicitlySetFields, ABC, _ResourceDescriptionBaseAbstractFieldsProtocol):
    """base class for all resource descriptions"""

    _validation_summary: Optional[ValidationSummary] = PrivateAttr(None)

    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset({"type", "format_version"})
    implemented_format_version: ClassVar[str]
    implemented_format_version_tuple: ClassVar[Tuple[int, int, int]]

    @field_validator("format_version", mode="before", check_fields=False)
    @classmethod
    def _ignore_future_patch(cls, value: Any, /) -> Any:
        def get_maj(v: str):
            parts = v.split(".")
            if parts and (p := parts[0]).isdecimal():
                return int(p)
            else:
                return 0

        def get_min_patch(v: str):
            parts = v.split(".")
            if len(parts) == 3:
                _, m, p = parts
                if m.isdecimal() and p.isdecimal():
                    return int(m), int(p)

            return (0, 0)

        if (
            cls.implemented_format_version != "unknown"
            and value != cls.implemented_format_version
            and isinstance(value, str)
            and value.count(".") == 2
            and get_maj(value) == cls.implemented_format_version_tuple[0]
            and get_min_patch(value) > cls.implemented_format_version_tuple[1:]
        ):
            issue_warning(
                "future format_version '{value}' treated as '{implemented}'",
                value=value,
                msg_context=dict(implemented=cls.implemented_format_version),
                severity=ALERT,
            )
            return cls.implemented_format_version
        else:
            return value

    @property
    def validation_summary(self) -> Optional[ValidationSummary]:
        return self._validation_summary

    _root: Union[AnyUrl, DirectoryPath] = PrivateAttr(default_factory=lambda: validation_context_var.get().root)

    @property
    def root(self) -> Union[AnyUrl, DirectoryPath]:
        return self._root

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any):
        super().__pydantic_init_subclass__(**kwargs)
        if "format_version" in cls.model_fields and cls.model_fields["format_version"].default is not PydanticUndefined:
            cls.implemented_format_version = cls.model_fields["format_version"].default
            if "." not in cls.implemented_format_version:
                cls.implemented_format_version_tuple = (0, 0, 0)
            else:
                cls.implemented_format_version_tuple = cast(
                    Tuple[int, int, int], tuple(int(x) for x in cls.implemented_format_version.split("."))
                )
            assert len(cls.implemented_format_version_tuple) == 3, cls.implemented_format_version_tuple

    @classmethod
    def load(
        cls, data: BioimageioYamlContent, context: Optional[ValidationContext] = None
    ) -> Union[Self, InvalidDescription]:
        context = context or validation_context_var.get()
        assert isinstance(data, dict)
        with context:
            rd, errors, val_warnings = cls._load_impl(deepcopy(data))

        if context.warning_level > INFO:
            all_warnings_context = context.replace(warning_level=INFO)
            # get validation warnings by reloading
            with all_warnings_context:
                _, _, val_warnings = cls._load_impl(deepcopy(data))

        rd._validation_summary = ValidationSummary(
            name="bioimageio.spec validation",
            source_name=str(RelativeFilePath(context.file_name).get_absolute(context.root)),
            status="failed" if errors else "passed",
            details=[
                ValidationSummaryDetail(
                    bioimageio_spec_version=VERSION,
                    errors=errors,
                    name=f"bioimageio.spec validation as {rd.type} {rd.format_version}",
                    status="failed" if errors else "passed",
                    warnings=val_warnings,
                )
            ],
        )

        return rd

    @classmethod
    def _load_impl(
        cls, data: BioimageioYamlContent
    ) -> Tuple[Union[Self, InvalidDescription], List[ErrorEntry], List[WarningEntry]]:
        rd: Union[Self, InvalidDescription, None] = None
        val_errors: List[ErrorEntry] = []
        val_warnings: List[WarningEntry] = []

        try:
            rd = cls.model_validate(data)
        except pydantic.ValidationError as e:
            for ee in e.errors(include_url=False):
                if (severity := ee.get("ctx", {}).get("severity", ERROR)) < ERROR:
                    val_warnings.append(WarningEntry(loc=ee["loc"], msg=ee["msg"], type=ee["type"], severity=severity))
                else:
                    val_errors.append(ErrorEntry(loc=ee["loc"], msg=ee["msg"], type=ee["type"]))

            if len(val_errors) == 0:
                val_errors.append(
                    ErrorEntry(
                        loc=(),
                        msg=(
                            f"Encountered {len(val_warnings)} more severe than warning level "
                            f"'{WARNING_LEVEL_TO_NAME[validation_context_var.get().warning_level]}'"
                        ),
                        type="severe_warnings",
                    )
                )
        except Exception as e:
            val_errors.append(
                ErrorEntry(loc=(), msg=str(e), type=type(e).__name__, traceback=traceback.format_tb(e.__traceback__))
            )

        if rd is None:
            try:
                rd = InvalidDescription.model_validate(data)
            except Exception:
                resource_type = cls.model_fields["type"].default
                format_version = cls.implemented_format_version
                rd = InvalidDescription(type=resource_type, format_version=format_version)

        return rd, val_errors, val_warnings


class InvalidDescription(
    ResourceDescriptionBase,
    extra="allow",
    title="An invalid resource description",
):
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


class FileDescr(Node):
    source: Annotated[FileSource, Field(description="∈📦 file source")]
    """∈📦 file source"""

    sha256: Optional[Sha256] = None
    """SHA256 checksum of the source file"""

    @model_validator(mode="after")
    def validate_sha256(self) -> Self:
        context = validation_context_var.get()
        if not context.perform_io_checks:
            return self

        local_source = download(self.source, sha256=self.sha256).path
        actual_sha = get_sha256(local_source)
        if self.sha256 is None:
            self.sha256 = actual_sha
        elif self.sha256 != actual_sha:
            raise ValueError(
                f"Sha256 mismatch for {self.source}. Expected {self.sha256}, got {actual_sha}. "
                "Update expected `sha256` or point to the matching file."
            )

        return self

    def download(self):
        return download(self.source, sha256=self.sha256)
