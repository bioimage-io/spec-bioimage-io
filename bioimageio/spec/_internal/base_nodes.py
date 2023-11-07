from __future__ import annotations

import ast
import collections.abc
import inspect
import os
from abc import ABC
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

from bioimageio.spec._internal.constants import IN_PACKAGE_MESSAGE
from bioimageio.spec._internal.types import RdfContent, Version
from bioimageio.spec._internal.utils import unindent
from bioimageio.spec._internal.validation_context import InternalValidationContext, get_internal_validation_context
from bioimageio.spec.summary import ValidationSummary


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

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any):
        super().__pydantic_init_subclass__(**kwargs)
        if os.getenv("BIOIMAGEIO_SET_UNDEFINED_FIELD_DESCRIPTIONS_FROM_VAR_DOCSTRINGS", "False").lower() in (
            "1",
            "true",
        ):
            cls._set_undefined_field_descriptions_from_var_docstrings()
            # cls._set_undefined_field_descriptions_from_field_name()  # todo: decide if we can remove this

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
        assert isinstance(module, ast.Module)
        class_def = module.body[0]
        assert isinstance(class_def, ast.ClassDef)
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


class ResourceDescriptionBase(NodeWithExplicitlySetFields):
    """base class for all resource descriptions"""

    _internal_validation_context: InternalValidationContext = PrivateAttr(
        default_factory=get_internal_validation_context
    )
    _validation_summaries: List[ValidationSummary] = PrivateAttr(default_factory=list)

    fields_to_set_explicitly: ClassVar[FrozenSet[LiteralString]] = frozenset({"type", "format_version"})
    implemented_format_version: ClassVar[str]
    implemented_format_version_tuple: ClassVar[Tuple[int, int, int]]

    @property
    def validation_summaries(self) -> List[ValidationSummary]:
        return self._validation_summaries

    @property
    def root(self) -> Union[AnyUrl, DirectoryPath]:
        return self._internal_validation_context["root"]

    @classmethod
    def convert_from_older_format(cls, data: RdfContent, context: InternalValidationContext) -> None:
        pass

    @model_validator(mode="before")
    @classmethod
    def update_context_and_data(cls, data: RdfContent, info: ValidationInfo):
        context = get_internal_validation_context(info.context)
        cls._update_context(context, data)
        cls.convert_from_older_format(data, context)
        return data

    @model_validator(mode="after")
    def remember_internal_validation_context(self, info: ValidationInfo) -> Self:
        self._internal_validation_context = get_internal_validation_context(info.context)
        return self

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
            assert len(cls.implemented_format_version_tuple) == 3

    @classmethod
    def _update_context(cls, context: InternalValidationContext, data: RdfContent) -> None:
        # set original format if possible
        original_format = data.get("format_version")
        if "original_format" not in context and isinstance(original_format, str) and original_format.count(".") == 2:
            context["original_format"] = Version(original_format)

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

        context = get_internal_validation_context(context)
        if isinstance(obj, dict):
            assert all(isinstance(k, str) for k in obj)
            cls._update_context(context, obj)

        return super().model_validate(
            obj, strict=strict, from_attributes=from_attributes, context=cast(Dict[str, Any], context)
        )


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
        assert issubclass(source, StringNode)
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
