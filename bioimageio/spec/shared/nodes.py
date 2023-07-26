from __future__ import annotations
from abc import ABC

import ast
import collections.abc
import inspect
import sys
from collections import UserString
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    ClassVar,
    Dict,
    Generic,
    Iterator,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

import pydantic
from pydantic import (
    BaseModel,
    Field,
    GetCoreSchemaHandler,
    TypeAdapter,
    ValidationInfo,
    field_validator,
    model_serializer,
    model_validator,
)
from pydantic.config import ConfigDict
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing_extensions import Self, Unpack

from bioimageio.spec._internal._validate import is_valid_raw_mapping
from bioimageio.spec.shared.types import RawDict, RawValue
from bioimageio.spec.shared.validation import ValidationContext, validation_context_var

if TYPE_CHECKING:
    from pydantic.main import IncEx, Model

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
        validate_default=True,
        validate_return=True,
    )
    """pydantic model config"""

    def model_post_init(self, __context: Any):
        super().model_post_init(__context)
        self._set_undefined_field_descriptions_from_var_docstrings()
        self._set_defaults_for_undefined_field_descriptions()

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

    def _set_undefined_field_descriptions_from_var_docstrings(self) -> None:
        module = ast.parse(inspect.getsource(self.__class__))
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
            if field_name not in self.model_fields:
                continue

            info = self.model_fields[field_name]
            if info.description is not None:
                continue

            doc_node = node.value
            if isinstance(doc_node, ast.Constant):
                docstring = doc_node.value  # 'regular' variable doc string
            # elif isinstance(doc_node, (ast.JoinedStr, ast.FormattedValue)):
            #     docstring = eval(ast.unparse(doc_node))  # evaluate f-string
            else:
                raise NotImplementedError(doc_node)

            info.description = docstring

    def _set_defaults_for_undefined_field_descriptions(self):
        for name, info in self.model_fields.items():
            if info.description is None:
                info.description = name

    # @classmethod
    # def generate_documentation(cls: Type[Node], lvl: int = 0):
    #     cls.__na
    # doc = f"{'#'*lvl} {cls.__name__}"
    # doc = ""
    # doc += f"# {cls.__name__}\n\n"
    # doc += f"{cls.Doc.short_description}\n\n"
    # doc += f"{cls.Doc.long_description}\n\n"
    # doc += "## Fields\n\n"
    # for name, field in cls.__fields__.items():
    #     field_info: pd.fields.FieldInfo = field.field_info
    #     doc += f"### {name}\n\n"
    #     doc += f"{field_info.description}\n\n"
    #     for constraint in field_info.get_constraints():
    #         doc += f"* constraint : `{constraint} = {getattr(field_info, constraint)}`\n\n"


class ResourceDescriptionBase(Node):
    def __init__(self, **data: Any) -> None:
        __tracebackhide__ = True
        context = self._get_context_and_update_data(data)
        self.__pydantic_validator__.validate_python(
            data,
            self_instance=self,
            context=dict(context),
        )

    @classmethod
    def _get_context_and_update_data(
        cls, data: Dict[str, Any], context: Optional[ValidationContext] = None
    ) -> ValidationContext:
        if context is None:
            context = validation_context_var.get()

        if context.root:
            if "root" in cls.model_fields:
                data["root"] = context.root
        elif "root" in data:
            context = ValidationContext(**{**dict(context), "root": data["root"]})

        original_format = data.get("format_version")
        if isinstance(original_format, str) and original_format.count(".") == 2:
            context = context.model_copy(update=dict(original_format=tuple(map(int, original_format.split(".")))))

        cls.convert_from_older_format(data)
        return context

    @classmethod
    def convert_from_older_format(cls, data: RawDict) -> None:
        """A node may `convert` it's raw data from an older format."""
        pass

    @classmethod
    def model_validate(
        cls: type[Model],
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: dict[str, Any] | None | ValidationContext = None,
    ) -> Model:
        """Validate a pydantic model instance.

        Args:
            obj: The object to validate.
            strict: Whether to raise an exception on invalid fields.
            from_attributes: Whether to extract data from object attributes.
            context: Additional context to pass to the validator.

        Raises:
            ValidationError: If the object could not be validated.

        Returns:
            The validated model instance.
        """
        __tracebackhide__ = True
        if isinstance(context, dict):
            context = ValidationContext(**context)

        if isinstance(obj, pydantic.BaseModel):
            data: Dict[str, Any] = obj.model_dump()
        elif isinstance(obj, dict):
            assert all(isinstance(k, str) for k in obj)  # type: ignore
            data = obj
        else:
            raise TypeError(type(obj))

        new_context = cls._get_context_and_update_data(data, context)

        return super().model_validate(data, strict=strict, from_attributes=from_attributes, context=dict(new_context))


class StringNode(UserString, ABC):
    _pattern: ClassVar[str]
    _node_class: Type[Node]
    _node: Node

    def __init__(self, seq: object) -> None:
        super().__init__(seq)
        type_hints = {fn: t for fn, t in get_type_hints(self.__class__).items() if not fn.startswith("_")}
        defaults = {fn: getattr(self.__class__, fn, Field()) for fn in type_hints}
        field_definitions: Dict[str, Any] = {fn: (t, defaults[fn]) for fn, t in type_hints.items()}
        self._node_class = pydantic.create_model(
            self.__class__.__name__, __base__=Node, __module__=self.__module__, **field_definitions
        )
        context = dict(validation_context_var.get())
        valid_string_data = TypeAdapter(Annotated[str, Field(pattern=self._pattern)]).validate_python(
            self.data, context=context
        )
        data = self._get_data(valid_string_data)
        self._node = self._node_class.model_validate(data, context=context)
        for fn, value in self._node:
            setattr(self, fn, value)

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
        with ValidationContext(**(info.context or {})):
            return cls(value)

    def _serialize(self) -> str:
        return self.data


D = TypeVar("D")


class FrozenDictNode(FrozenDictBase[K, V], Node):
    model_config = {**Node.model_config, "extra": "allow"}

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
    def validate_raw_mapping(self):
        if not is_valid_raw_mapping(self):
            raise AssertionError(f"{self} contains values unrepresentable in JSON/YAML")

        return self


class Kwargs(FrozenDictNode[str, Any]):
    pass
