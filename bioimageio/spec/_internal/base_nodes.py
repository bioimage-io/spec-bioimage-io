from __future__ import annotations

import ast
import collections.abc
import inspect
import os
import traceback
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import (
    Any,
    ClassVar,
    Dict,
    FrozenSet,
    List,
    Optional,
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
    ValidationInfo,
    model_validator,
)
from pydantic_core import PydanticUndefined, core_schema
from typing_extensions import Annotated, LiteralString, Self

from bioimageio.spec._internal import settings
from bioimageio.spec._internal.constants import ERROR, IN_PACKAGE_MESSAGE, INFO, VERSION
from bioimageio.spec._internal.io_utils import download, get_sha256
from bioimageio.spec._internal.types import BioimageioYamlContent, RelativeFilePath
from bioimageio.spec._internal.types import FileSource as FileSource
from bioimageio.spec._internal.types import Sha256 as Sha256
from bioimageio.spec._internal.utils import unindent
from bioimageio.spec._internal.validation_context import (
    InternalValidationContext,
    ValidationContext,
    create_internal_validation_context,
)
from bioimageio.spec.summary import ErrorEntry, ValidationSummary, WarningEntry


class Node(
    pydantic.BaseModel,
    extra="forbid",
    frozen=False,
    populate_by_name=True,
    revalidate_instances="always",
    validate_assignment=True,
    validate_default=True,
    validate_return=True,
):
    """Subpart of a resource description"""

    _internal_validation_context: InternalValidationContext = PrivateAttr(
        default_factory=create_internal_validation_context
    )
    """the validation context used to validate the node
    (reused to validate assignments)"""

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any):
        super().__pydantic_init_subclass__(**kwargs)
        if settings.set_undefined_field_descriptions_from_var_docstrings:
            cls._set_undefined_field_descriptions_from_var_docstrings()
            # cls._set_undefined_field_descriptions_from_field_name()  # todo: decide if we can remove this

    def model_post_init(
        self, __context: "ValidationContext | InternalValidationContext | Dict[str, Any] | None"
    ) -> None:
        # save the final validation context for validation upon assignment
        # (may also be used for model after validations)
        self._internal_validation_context = create_internal_validation_context(__context)
        super().model_post_init(self._internal_validation_context)

    @classmethod
    def _set_undefined_field_descriptions_from_var_docstrings(cls) -> None:
        for klass in inspect.getmro(cls):
            if issubclass(klass, Node):
                cls._set_undefined_field_descriptions_from_var_docstrings_impl(klass)

    @classmethod
    def _set_undefined_field_descriptions_from_var_docstrings_impl(cls, klass: Type[Any]):
        try:
            source = inspect.getsource(klass)
        except OSError:
            if klass.__module__ == "pydantic.main":
                # klass is probably a dynamically created pydantic Model (using pydantic.create_model)
                return
            else:
                raise

        unindented_source = unindent(source)
        module = ast.parse(unindented_source)
        assert isinstance(module, ast.Module), module
        class_def = module.body[0]
        assert isinstance(class_def, ast.ClassDef), class_def
        if len(class_def.body) < 2:
            return

        for last, node in zip(class_def.body, class_def.body[1:]):
            if not (
                isinstance(last, ast.AnnAssign) and isinstance(last.target, ast.Name) and isinstance(node, ast.Expr)
            ):
                continue

            field_name = last.target.id
            if field_name not in cls.model_fields:
                continue

            info = cls.model_fields[field_name]
            description = info.description or ""
            if description and description != IN_PACKAGE_MESSAGE:
                continue

            doc_node = node.value
            if isinstance(doc_node, ast.Constant):
                docstring = doc_node.value
            else:
                raise NotImplementedError(doc_node)

            info.description = description + docstring

    @classmethod
    def _set_undefined_field_descriptions_from_field_name(cls):
        for name, info in cls.model_fields.items():
            if info.description is None:
                info.description = name


class NodeWithExplicitlySetFields(Node):
    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset()
    """set set these fields explicitly with their default value if they are not set,
    such that they are always included even when dumping with 'exlude_unset'"""

    @model_validator(mode="before")
    @classmethod
    def set_fields_explicitly(cls, data: Union[Any, Dict[Any, Any]]) -> Union[Any, Dict[Any, Any]]:
        if isinstance(data, dict):
            for name in cls.fields_to_set_explicitly:
                if name not in data:
                    data[name] = cls.model_fields[name].get_default(call_default_factory=True)

        return data


class ResourceDescriptionBase(NodeWithExplicitlySetFields, ABC):
    """base class for all resource descriptions"""

    _validation_summaries: List[ValidationSummary] = PrivateAttr(default_factory=list)

    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset({"type", "format_version"})
    implemented_format_version: ClassVar[str]
    implemented_format_version_tuple: ClassVar[Tuple[int, int, int]]

    # type: LiteralString  # TODO: make abstract fields
    # format_version: LiteralString  # TODO: make abstract fields

    @property
    def validation_summaries(self) -> List[ValidationSummary]:
        return self._validation_summaries

    @property
    def root(self) -> Union[AnyUrl, DirectoryPath]:
        return self._internal_validation_context["root"]

    @classmethod
    @abstractmethod
    def convert_from_older_format(cls, data: BioimageioYamlContent, context: InternalValidationContext) -> None:
        # TODO: this classmethod should accept a preceeding description instance instead of raw yaml content
        ...

    @model_validator(mode="before")
    @classmethod
    def _convert_from_older_format(cls, data: BioimageioYamlContent, info: ValidationInfo):
        context = create_internal_validation_context(info.context)
        cls.convert_from_older_format(data, context)
        return data

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
    def model_validate(
        cls,
        obj: Union[Any, Dict[str, Any]],
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Union[InternalValidationContext, Dict[str, Any], None] = None,
    ) -> Self:
        """Validate a pydantic model instance.

        Args:
            obj: The object to validate.
            strict: Whether to raise an exception on invalid fields.
            from_attributes: Whether to extract data from object attributes.
            context: Additional context to pass to the validator.

        Raises:
            ValueError: If context is not a valid ValidationContext.
            ValidationError: If the object could not be validated.

        Returns:
            The validated model instance.
        """
        __tracebackhide__ = True

        context = create_internal_validation_context(context)
        if isinstance(obj, dict):
            assert all(isinstance(k, str) for k in obj), obj

        return super().model_validate(
            obj, strict=strict, from_attributes=from_attributes, context=cast(Dict[str, Any], context)
        )

    @classmethod
    def load(
        cls,
        data: BioimageioYamlContent,
        *,
        context: ValidationContext,
    ) -> Union[Self, InvalidDescription]:
        rd, errors, tb, val_warnings = cls._load_impl(
            deepcopy(data),
            create_internal_validation_context(context.model_dump(), warning_level=ERROR),
        )  # ignore any warnings using warning level 'ERROR'/'CRITICAL' on first loading attempt

        assert not val_warnings, f"already got warnings: {val_warnings}"
        _, error2, tb2, val_warnings = cls._load_impl(
            deepcopy(data), create_internal_validation_context(context.model_dump(), warning_level=INFO)
        )
        assert not error2 or isinstance(rd, InvalidDescription), f"decreasing warning level caused errors: {error2}"
        assert not tb2 or isinstance(rd, InvalidDescription), f"decreasing warning level lead to error traceback: {tb2}"
        summary = ValidationSummary(
            bioimageio_spec_version=VERSION,
            errors=errors,
            name=f"bioimageio.spec validation as {rd.type} {rd.format_version}",  # type: ignore
            source_name=str(RelativeFilePath(context.file_name).get_absolute(context.root)),
            status="failed" if errors else "passed",
            warnings=val_warnings,
            traceback=tb,
        )

        rd._validation_summaries.append(summary)
        return rd

    @classmethod
    def _load_impl(
        cls, data: BioimageioYamlContent, context: InternalValidationContext
    ) -> Tuple[Union[Self, InvalidDescription], List[ErrorEntry], List[str], List[WarningEntry]]:
        rd: Union[Self, InvalidDescription, None] = None
        val_errors: List[ErrorEntry] = []
        val_warnings: List[WarningEntry] = []
        tb: List[str] = []

        try:
            rd = cls.model_validate(data, context=dict(context))
        except pydantic.ValidationError as e:
            for ee in e.errors(include_url=False):
                if (severity := ee.get("ctx", {}).get("severity", ERROR)) < ERROR:
                    val_warnings.append(WarningEntry(loc=ee["loc"], msg=ee["msg"], type=ee["type"], severity=severity))
                else:
                    val_errors.append(ErrorEntry(loc=ee["loc"], msg=ee["msg"], type=ee["type"]))
        except Exception as e:
            val_errors.append(ErrorEntry(loc=(), msg=str(e), type=type(e).__name__))
            tb = traceback.format_tb(e.__traceback__)

        if rd is None:
            try:
                rd = InvalidDescription.model_validate(data)
            except Exception:
                resource_type = cls.model_fields["type"].default
                format_version = cls.implemented_format_version
                rd = InvalidDescription(type=resource_type, format_version=format_version)

        return rd, val_errors, tb, val_warnings


class InvalidDescription(ResourceDescriptionBase, extra="allow", title="An invalid resource description"):
    type: Any = "unknown"
    format_version: Any = "unknown"
    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset()

    @classmethod
    def convert_from_older_format(cls, data: BioimageioYamlContent, context: InternalValidationContext) -> None:
        pass


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
        return core_schema.with_info_after_validator_function(
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
    def _validate(cls, value: str, info: ValidationInfo) -> Self:
        valid_string_data = TypeAdapter(Annotated[str, StringConstraints(pattern=cls._pattern)]).validate_python(
            value, context=info.context
        )
        data = cls._get_data(valid_string_data)
        self = cls(valid_string_data)
        object.__setattr__(self, "_node", self._node_class.model_validate(data, context=info.context))
        return self

    def _serialize(self) -> str:
        return self.data


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
    source: FileSource
    """∈📦 file source"""

    sha256: Optional[Sha256] = None
    """SHA256 checksum of the source file"""

    @model_validator(mode="after")
    def validate_sha256(self) -> Self:
        context = self._internal_validation_context
        if not context["perform_io_checks"]:
            return self

        local_source = download(self.source, sha256=self.sha256, root=context["root"]).path
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
        return download(self.source, sha256=self.sha256, root=self._internal_validation_context["root"])
