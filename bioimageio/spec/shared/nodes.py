from __future__ import annotations

import ast
import collections.abc
import inspect
import sys
from abc import ABC
from collections import UserString
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generic,
    Iterator,
    Literal,
    Mapping,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    get_type_hints,
)

import pydantic
from pydantic import (
    Field,
    GetCoreSchemaHandler,
    StringConstraints,
    TypeAdapter,
    ValidationInfo,
    model_validator,
)
from pydantic_core import PydanticUndefined, core_schema
from typing_extensions import Annotated, Self

from bioimageio.spec._internal._constants import IN_PACKAGE_MESSAGE
from bioimageio.spec._internal._utils import unindent
from bioimageio.spec._internal._validate import ValContext, get_validation_context, is_valid_raw_mapping
from bioimageio.spec.shared.types import NonEmpty, RawDict, RawValue

if TYPE_CHECKING:
    from pydantic.main import IncEx

K = TypeVar("K", bound=str)
V = TypeVar("V")

if sys.version_info < (3, 9):

    class FrozenDictBase(collections.abc.Mapping, Generic[K, V]):
        pass

else:
    FrozenDictBase = collections.abc.Mapping[K, V]


class Node(
    pydantic.BaseModel,
):
    """Subpart of a resource description"""

    model_config = pydantic.ConfigDict(
        extra="forbid",
        frozen=True,
        populate_by_name=True,
        revalidate_instances="always",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    """pydantic model config"""

    @classmethod
    def __pydantic_init_subclass__(
        cls, *, set_undefined_field_descriptions_from_var_docstrings: bool = False, **kwargs: Any
    ):
        super().__pydantic_init_subclass__(**kwargs)
        if set_undefined_field_descriptions_from_var_docstrings:
            cls._set_undefined_field_descriptions_from_var_docstrings()
            # cls._set_undefined_field_descriptions_from_field_name()

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

    def model_dump(
        self,
        *,
        mode: Union[Literal["json", "python"], str] = "json",  # pydantic default: "python"
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = True,  # pydantic default: False
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> Dict[str, RawValue]:
        return super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )

    def model_dump_json(
        self,
        *,
        indent: Union[int, None] = None,
        include: IncEx = None,
        exclude: IncEx = None,
        by_alias: bool = False,
        exclude_unset: bool = True,  # pydantic default: False
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        round_trip: bool = False,
        warnings: bool = True,
    ) -> str:
        return super().model_dump_json(
            indent=indent,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )


class ResourceDescriptionBase(Node):
    type: str
    format_version: str

    implemented_format_version: ClassVar[str]
    implemented_format_version_tuple: ClassVar[Tuple[int, int, int]]

    @model_validator(mode="before")
    @classmethod
    def update_context_and_data(cls, data: Union[Any, Mapping[Any, Any]], info: ValidationInfo):
        if isinstance(data, collections.abc.Mapping):
            if isinstance(data, dict):
                data_dict = data
            else:
                data_dict = dict(data)

            context = get_validation_context(**(info.context or {}))
            cls._update_context_and_data(context, data_dict)
            return data_dict
        else:
            return data

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any):
        super().__pydantic_init_subclass__(**kwargs)
        if cls.model_fields["format_version"].default is not PydanticUndefined:
            cls.implemented_format_version = cls.model_fields["format_version"].default
            cls.implemented_format_version_tuple = tuple(int(x) for x in cls.implemented_format_version.split("."))
            assert len(cls.implemented_format_version_tuple) == 3

    @classmethod
    def _update_context_and_data(cls, context: ValContext, data: Dict[Any, Any]) -> None:
        # set original format if possible
        original_format = data.get("format_version")
        if "original_format" not in context and isinstance(original_format, str) and original_format.count(".") == 2:
            data.setdefault("config", {}).setdefault("bioimageio", {})["original_format_version"] = original_format
            context["original_format"] = tuple(map(int, original_format.split(".")))

        cls.convert_from_older_format(data, context)

    @classmethod
    def convert_from_older_format(cls, data: RawDict, context: ValContext) -> None:
        """A node may `convert` it's raw data from an older format."""
        pass

    @classmethod
    def model_validate(
        cls,
        obj: Union[Any, Dict[str, Any]],
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Union[ValContext, Dict[str, Any], None] = None,
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

        context = get_validation_context(**cast(Dict[str, Any], (context or {})))
        if isinstance(obj, dict):
            assert all(isinstance(k, str) for k in obj)
            cls._update_context_and_data(context, obj)

        return super().model_validate(
            obj, strict=strict, from_attributes=from_attributes, context=cast(Dict[str, Any], context)
        )


class StringNode(UserString, ABC):
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

        setattr(self, "__setattr__", __setattr__)

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
        return core_schema.general_after_validator_function(
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


D = TypeVar("D")


class FrozenDictNode(FrozenDictBase[K, V], Node):
    def __getitem__(self, item: K) -> V:
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item) from None

    def __iter__(self) -> Iterator[K]:  # type: ignore  iterate over keys like a dict, not (key, value) tuples
        yield from self.model_fields_set  # type: ignore

    def __len__(self) -> int:
        return len(self.model_fields_set)

    def keys(self) -> Set[K]:  # type: ignore
        return set(self.model_fields_set)  # type: ignore

    def __contains__(self, key: Any):
        return key in self.model_fields_set

    def get(self, item: Any, default: D = None) -> Union[V, D]:  # type: ignore
        return getattr(self, item, default)

    @pydantic.model_validator(mode="after")
    def validate_raw_mapping(self) -> Self:
        if not is_valid_raw_mapping(self):
            raise AssertionError(f"{self} contains values unrepresentable in JSON/YAML")

        return self


class ConfigNode(FrozenDictNode[NonEmpty[str], RawValue]):
    model_config = {**Node.model_config, "extra": "allow"}


class Kwargs(FrozenDictNode[NonEmpty[str], RawValue]):
    model_config = {**Node.model_config, "extra": "allow"}
