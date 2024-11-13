import datetime
import inspect
import json
import types
import typing
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import (
    Any,
    ClassVar,
    Dict,
    Final,
    ForwardRef,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
    cast,
    final,
)
from xml.etree import ElementTree as et

import pydantic
import typing_extensions
import yaml
from annotated_types import Predicate
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined, PydanticUndefinedType
from typing_extensions import List, TypeAlias, TypeAliasType, assert_never

from bioimageio.spec._internal.io import YamlValue, is_yaml_leaf_value, is_yaml_value
from bioimageio.spec._internal.validated_string import ValidatedString


def eprint(message: str):
    import sys

    print(message, file=sys.stderr)


class Unrecognized:
    raw_hint: Any

    def __init__(self, raw_hint: Any):
        self.raw_hint = raw_hint
        super().__init__()

    def __str__(self) -> str:
        return f"Unrecognized type hint: {self.raw_hint}"

    def with_context(self, message: str) -> "ParsingError":
        return ParsingError(message=message, cause=self)


class ParsingError(Exception):
    def __init__(
        self, message: str, cause: "ParsingError | Unrecognized | None" = None
    ) -> None:
        self.message = message
        self.cause = cause
        super().__init__()

    def _display(self, level: int) -> str:
        base_message = "  " * level + self.message
        if isinstance(self.cause, ParsingError):
            return base_message + ":\n" + self.cause._display(level + 1)
        elif isinstance(self.cause, Unrecognized):
            return base_message + ":\n" + ("  " * (level + 1)) + str(self.cause)
        elif self.cause is None:
            return base_message
        else:
            assert_never(self.cause)

    def __str__(self) -> str:
        return self._display(level=0)

    def with_context(self, message: str) -> "ParsingError":
        return ParsingError(message=message, cause=self)


def any_is_subclass(child: Any, parent: Type[Any]) -> bool:
    return inspect.isclass(child) and issubclass(child, parent)


@dataclass
class Example:
    value: YamlValue

    @classmethod
    def try_from_value(cls, val: Any) -> "Example | Exception":
        if is_yaml_value(val):
            return Example(value=val)
        if isinstance(val, BaseModel):
            yaml_value: YamlValue = cast(YamlValue, val.model_dump(mode="json"))
            return Example(value=yaml_value)
        try:
            # FIXME: stricter typing here?
            val_type: Any = type(val)
            adapter: Any = pydantic.TypeAdapter(val_type)
            dumped_value = json.loads(adapter.dump_json(val))
            return Example(value=dumped_value)
        except Exception as e:
            return Exception(f"Value {val} is not Json-serializable: {e}")

    def to_yaml_str(self) -> str:
        out = yaml.dump(self.value)
        yaml_end_of_file = (
            "\n...\n"  # FIXME: can't we just dump without the end-of-file marker?
        )
        if out.endswith(yaml_end_of_file):
            return out[: -len(yaml_end_of_file)]
        else:
            return out

    def to_json_str(self) -> str:
        return json.dumps(self.value, indent=4)


def get_field_annotation(field_info: FieldInfo) -> Any:
    if field_info.metadata:
        inner_annotation: Any = field_info.annotation  # FIXME?
        # FIXME: thisrequired python 3.11
        # return typing_extensions.Annotated[inner_annotation, *field_info.metadata]
        out = typing_extensions.Annotated[inner_annotation, "placeholder"]
        out.__metadata__ = (  # pyright: ignore [reportAttributeAccessIssue]
            field_info.metadata
        )
        return out
    else:
        return field_info.annotation


def field_has_default_value(info: FieldInfo) -> bool:
    return not isinstance(info.default, PydanticUndefinedType)


class Hint(ABC):
    @staticmethod
    def get_subclasses() -> Sequence[Type["Hint"]]:
        return [
            YamlValueHint,
            RecursionHint,
            StringNodeHint,
            RootModelHint,
            AnnotatedHint,
            TypeAliasHint,
            DatetimeHint,
            DateHint,
            PathHint,
            EmailHint,
            UrlHint,
            MappingHint,
            LiteralHint,
            ModelHint,
            PrimitiveHint,
            NTuple,
            VarLenTuple,
            ListHint,
            UnionHint,
        ]

    @final
    @classmethod
    def parse(
        cls,
        *,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        # if raw_hint in cls.hint_cache:
        # return cls.hint_cache[raw_hint] #FIXME: maybe move this into the individual do_parse impls?
        hint: "Hint | Unrecognized | Exception" = Unrecognized(raw_hint=raw_hint)
        for subclass in Hint.get_subclasses():
            hint = subclass.do_parse(
                raw_hint, parent_raw_hints=parent_raw_hints, discriminator=discriminator
            )
            if isinstance(hint, ParsingError):
                return hint
            if isinstance(hint, Unrecognized):
                continue
            # cls.hint_cache[raw_hint] = hint
            break
        return hint

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    @abstractmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        raise NotImplementedError

    @abstractmethod
    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        raise NotImplementedError

    @abstractmethod
    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        raise NotImplementedError

    @abstractmethod
    def get_example(self) -> "Example | Exception":
        raise NotImplementedError


class YamlValueHint(Hint):
    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        # FIXME: since the spec is yaml, "Any" mostly translates to YamlValue.... but is this always true?
        if raw_hint == typing.Any:
            return YamlValueHint()
        if raw_hint == "YamlValue":
            return YamlValueHint()
        if isinstance(raw_hint, ForwardRef) and raw_hint.__forward_arg__ == "YamlValue":
            return YamlValueHint()
        if inspect.isclass(raw_hint) and raw_hint.__name__ == "YamlValue":
            return YamlValueHint()
        if isinstance(raw_hint, TypeAliasType) and str(raw_hint) == "YamlValue":
            return YamlValueHint()
        return Unrecognized(raw_hint=raw_hint)

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", css_classes=[FieldsWidget.FIELD_TYPE_CSS_CLASS], children=[
            InlinePre(text="YamlValue"),
            *extra
        ])
        # fmt: on

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        return self.short_description(extra=extra_summary)

    def get_example(self) -> "Example | Exception":
        return Example({"some_key": "some_value", "another_key": [123, 456]})


class RecursionHint(Hint):
    def __init__(self, raw_hint: Any) -> None:
        self.raw_hint = raw_hint
        super().__init__()

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        if raw_hint not in parent_raw_hints:
            return Unrecognized(raw_hint=raw_hint)
        return RecursionHint(raw_hint=raw_hint)

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text=f"(Recursion to {self.raw_hint})"),
            *extra
        ])
        # fmt: on

    def get_example(self) -> "Example | Exception":
        return Example("... RECURSE ...")

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        # fmt: off
        return Widget("span", css_classes=[FieldsWidget.FIELD_TYPE_CSS_CLASS], children=[
            self.short_description(extra=extra_summary)
        ])
        # fmt: on


class StringNodeHint(Hint):
    def __init__(self, pattern: str) -> None:
        super().__init__()

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        if not inspect.isclass(raw_hint) or not any(
            klass.__name__ == "StringNode" for klass in raw_hint.__mro__
        ):
            return Unrecognized(raw_hint=raw_hint)
        return StringNodeHint(
            pattern=getattr(raw_hint, "_pattern")
        )  # FIXME: use types from spec

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text="ISO 8601 datetime"),
            *extra
        ])
        # fmt: on

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        return self.short_description(extra=extra_summary)

    def get_example(self) -> "Example | Exception":
        return Example(
            "*NO EXAMPLE PROVIDED*"
        )  # FIXME: maybe have a type just for absent examples


class RootModelHint(Hint):
    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        from pydantic import RootModel

        if not inspect.isclass(raw_hint):
            return Unrecognized(raw_hint=raw_hint)
        if issubclass(raw_hint, RootModel):
            inner = raw_hint.model_fields["root"]
            inner_hint = get_field_annotation(inner)
        elif issubclass(raw_hint, ValidatedString):
            inner_hint = raw_hint.root_model
        else:
            return Unrecognized(raw_hint=raw_hint)
        # FIXME: this misses the extra restrictions that might be defined in `raw_hint`
        return Hint.parse(raw_hint=inner_hint, parent_raw_hints=parent_raw_hints)


class AnnotatedHint(Hint):
    CSS_CLASS: ClassVar[str] = "annotated_type"
    RESTRICTION_CSS_CLASS: ClassVar[str] = "typing_annotated_annotation"

    inner_hint: Hint
    restrictions: Sequence[Any]

    def __init__(self, inner_hint: Hint, restrictions: List[str]) -> None:
        self.inner_hint = inner_hint
        self.restrictions = restrictions
        super().__init__()

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        if raw_hint.__class__ != typing_extensions.Annotated[int, None].__class__:
            return Unrecognized(raw_hint)

        inner_hint: "Hint | Unrecognized | ParsingError"
        discri: Optional[pydantic.Discriminator] = discriminator
        for md in raw_hint.__metadata__:
            if not isinstance(md, pydantic.Discriminator):
                continue
            discri = md
            break
        inner_hint = Hint.parse(
            raw_hint=raw_hint.__args__[0],
            parent_raw_hints=[*parent_raw_hints, raw_hint],
            discriminator=discri,
        )
        if isinstance(inner_hint, (ParsingError, Unrecognized)):
            return inner_hint.with_context(f"Could not parse inner hint for {raw_hint}")
        if len(raw_hint.__metadata__) == 1 and isinstance(
            raw_hint.__metadata__[0], pydantic.Discriminator
        ):
            return inner_hint  # "discriminator" is onl helpful for the parser, not for the user
        metadata: List[str] = []
        for md in raw_hint.__metadata__:
            # pydantic.Discriminator and pydantic.PlainSerializer are not useful for consumers.
            # A FieldInfo can appear if in types like Annotated[int, pydantic.Field(...)]. It usually has nothing useful
            if isinstance(
                md,
                (
                    pydantic.Discriminator,
                    pydantic.PlainSerializer,
                    pydantic.fields.FieldInfo,
                ),
            ):
                continue
            # FIXME: use isinstance, maybe render it somehow?
            if type(md).__name__ == "AfterWarner":
                continue
            if "PydanticGeneralMetadata" in type(md).__name__:
                continue
            if isinstance(md, Predicate):
                if isinstance(md.func, types.LambdaType):
                    try:
                        metadata.append(inspect.getsource(md.func).strip())
                    except OSError:
                        eprint("WARNING: could not get lambda source")
                    continue
                metadata_str = md.func.__name__
                if md.func.__doc__:
                    metadata_str += f": {md.func.__doc__}"
                else:
                    eprint(
                        f"WARNING: no predicated docstring in {parent_raw_hints}.{raw_hint}"
                    )
                metadata.append(metadata_str)
                continue
            metadata.append(str(md))
        if metadata.__len__() == 0:
            return inner_hint
        if isinstance(inner_hint, AnnotatedHint):
            return AnnotatedHint(
                inner_hint=inner_hint.inner_hint,
                restrictions=metadata + list(inner_hint.restrictions),
            )
        return AnnotatedHint(inner_hint=inner_hint, restrictions=metadata)

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        return self.inner_hint.short_description(
            extra=[
                WarningIconWidget(title="This field has further restrictions"),
                *extra,
            ]
        )

    def get_example(self) -> "Example | Exception":
        eprint("WARNING: Annotated type without a manually provided example")
        return self.inner_hint.get_example()

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        inner_widget = self.inner_hint.to_type_widget(
            path=path,
            extra_summary=[
                WarningIconWidget(title="This field has further restrictions"),
                *extra_summary,
            ],
        )

        # fmt: off
        restrictions_widget = Widget("div", children=[
            Widget("p", text="Restrictions:"),
            Widget("ul", css_classes=[self.RESTRICTION_CSS_CLASS], children=[
                Widget("li", text=str(annotation))
                for annotation in self.restrictions
            ]),
        ])
        # fmt: on

        if inner_widget.tag == "details":
            inner_widget.appendChildren([restrictions_widget])
            return inner_widget
        else:
            # fmt: off
            return Widget("details", children=[
                Widget("summary", children=[inner_widget]),
                restrictions_widget,
            ])
            # fmt: on


class TypeAliasHint(Hint):
    def __init__(self, name: str, inner: Hint) -> None:
        self.name = name
        self.inner = inner
        super().__init__()

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        if not isinstance(raw_hint, TypeAliasType):
            return Unrecognized(raw_hint=raw_hint)
        inner = Hint.parse(
            raw_hint=raw_hint.__value__,
            parent_raw_hints=[*parent_raw_hints, raw_hint],
            discriminator=discriminator,
        )
        if isinstance(inner, (Unrecognized, ParsingError)):
            return inner.with_context(
                f"Could not parse definition of alias {raw_hint.__name__}"
            )
        return TypeAliasHint(name=raw_hint.__name__, inner=inner)

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text=f"{self.name}"),
            Widget("span", text=" (Alias)", style="font-style: italic; opacity: 0.6"),
            *extra
        ])
        # fmt: on

    def get_example(self) -> "Example | Exception":
        inner_example = self.inner.get_example()
        if isinstance(inner_example, Exception):
            return Exception(f"Could not get example for {self.name}: {inner_example}")
        return inner_example

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        # fmt: off
        return Widget("details", children=[
            Widget("summary", children=[
                self.short_description(extra=extra_summary)
            ]),
            self.inner.to_type_widget(path=path, extra_summary=[
                Widget("span", text=" (Aliased)", style="font-style: italic; opacity: 0.6"),
            ])
        ])
        # fmt: on


class DatetimeHint(Hint):
    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        if raw_hint != datetime.datetime:
            return Unrecognized(raw_hint=raw_hint)
        return DatetimeHint()

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text="ISO 8601 datetime"),
            *extra
        ])
        # fmt: on

    def get_example(self) -> "Example | Exception":
        return Example(datetime.datetime.now().isoformat())

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        return self.short_description(extra=extra_summary)


class DateHint(Hint):
    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        if raw_hint != datetime.date:
            return Unrecognized(raw_hint=raw_hint)
        return DateHint()

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text="date (YYYY-MM-DD)"),
            *extra
        ])
        # fmt: on

    def get_example(self) -> "Example | Exception":
        return Example("2024-12-31")

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        return self.short_description(extra=extra_summary)


class PathHint(Hint):
    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        from pathlib import Path, PurePath

        if raw_hint != Path and raw_hint != PurePath:
            return Unrecognized(raw_hint=raw_hint)
        return PathHint()

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text="Path"),
            *extra
        ])
        # fmt: on

    def get_example(self) -> "Example | Exception":
        return Example("/some/path")

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        return self.short_description(extra=extra_summary)


class EmailHint(Hint):
    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        from pydantic.networks import EmailStr

        if raw_hint != EmailStr:
            return Unrecognized(raw_hint=raw_hint)
        return EmailHint()

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text="EmailStr"),
            *extra
        ])
        # fmt: on

    def get_example(self) -> "Example | Exception":
        return Example("john.doe@example.com")

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        return self.short_description(extra=extra_summary)


class UrlHint(Hint):
    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        from pydantic import AnyUrl

        if not inspect.isclass(raw_hint) or not issubclass(raw_hint, AnyUrl):
            return Unrecognized(raw_hint=raw_hint)
        return UrlHint()

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text="HttpUrl"),
            *extra
        ])
        # fmt: on

    def get_example(self) -> "Example | Exception":
        return Example("https://example.com/some/path")

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        return self.short_description(extra=extra_summary)


class MappingHint(Hint):
    value_hint: Hint
    value_example: Example

    def __init__(self, value_hint: Hint, value_example: Example):
        self.value_hint = value_hint
        self.value_example = value_example
        super().__init__()

    @staticmethod
    def is_mapping_hint(
        hint: Any,
    ) -> bool:  # Can't use TypeGuard[typing.GenericAlias] in py 3.8
        if inspect.isclass(hint):
            return issubclass(hint, Mapping)
        if issubclass(type(hint), type(typing.Mapping[int, str])):
            return any_is_subclass(hint.__origin__, Mapping)
        return False

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "MappingHint | Unrecognized | ParsingError":
        if not cls.is_mapping_hint(raw_hint):
            return Unrecognized(raw_hint)
        type_args: Tuple[Type[Any], Type[Any]] = getattr(raw_hint, "__args__")
        key_type = type_args[0]
        if (
            key_type is not str
            and key_type is not int
            and key_type != typing.Union[int, str]
        ):
            return ParsingError(
                f"Mappings with keys that are not ints or strings is not supported yet: {raw_hint}"
            )
        value_hint = Hint.parse(
            raw_hint=raw_hint.__args__[1],
            parent_raw_hints=[*parent_raw_hints, raw_hint],
        )
        if isinstance(value_hint, (Unrecognized, ParsingError)):
            return value_hint.with_context(f"Could not parse value type of {raw_hint}")
        value_example = value_hint.get_example()
        if isinstance(value_example, Exception):
            return ParsingError(
                f"Could not get example for {value_hint}: {value_example}"
            )
        return MappingHint(value_hint=value_hint, value_example=value_example)

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text="{ str: "),
            self.value_hint.short_description(),
            InlinePre(text="}"),
            *extra,
        ])
        # fmt: on

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        field_name = "[...]"  # FIXME: clearer key type?
        return FieldsWidget(
            base_path=path,
            short_description=self.short_description(extra=extra_summary),
            fields=[
                FieldData(
                    name=field_name,
                    description=None,
                    type_widget=self.value_hint.to_type_widget(
                        path=[*path, field_name]
                    ),
                    example=self.value_example,
                )
            ],
        )

    def get_example(self) -> "Example":
        return Example({"some_key": self.value_example.value})


def literal_value_to_code(lit_value: "int | bool | float | str | None") -> str:
    return f"'{lit_value}'" if isinstance(lit_value, str) else str(lit_value)


class LiteralHint(Hint):
    LIMIT = 10

    def __init__(self, values: Sequence["int | float | bool | str | None"]):
        self.values = values
        super().__init__()

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "LiteralHint | Unrecognized | ParsingError":
        some_dummy_literal_hint = Literal["a"]
        if raw_hint.__class__ != some_dummy_literal_hint.__class__:
            return Unrecognized(raw_hint)
        assert all(
            isinstance(val, (int, float, str, type(None), bool))
            for val in raw_hint.__args__
        )
        return LiteralHint(values=raw_hint.__args__)

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        widgets: List[Widget] = []

        if len(self.values) > LiteralHint.LIMIT:
            for part in self.values[0 : LiteralHint.LIMIT]:
                widgets.append(LiteralWidget(value=part))
                widgets.append(InlinePre(text=", "))
            widgets.append(
                InlinePre(text=f"({len(self.values) - LiteralHint.LIMIT} more)")
            )
            widgets.append(InlinePre(text=", "))
            widgets.append(LiteralWidget(value=self.values[-1]))
        else:
            for part_index, part in enumerate(self.values):
                widgets.append(LiteralWidget(value=part))
                if part_index < len(self.values) - 1:
                    widgets.append(InlinePre(text=", "))
        return Widget("span", children=[*widgets, *extra])

    def get_example(self) -> "Example | Exception":
        return Example(self.values[0])

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        if len(self.values) <= LiteralHint.LIMIT:
            # fmt: off
            return Widget("span", css_classes=[FieldsWidget.FIELD_TYPE_CSS_CLASS], children=[
                self.short_description(extra=extra_summary)
            ])
            # fmt: on

        # fmt: off
        return Widget("details", children=[
            Widget("summary", children=[
                self.short_description(extra=extra_summary)
            ]),
            Widget("table", children=[
                Widget("tbody", children=[
                    Widget("tr", children=[
                        Widget("td", css_classes=[FieldsWidget.FIELD_TYPE_CSS_CLASS], children=[
                            LiteralWidget(value=val)
                        ])
                    ])
                    for val in self.values
                ])
            ])
        ])
        # fmt: on


class ModelHint(Hint):
    def __init__(
        self,
        model: Type["BaseModel"],
        fields: Mapping[str, Tuple[Hint, Example]],
        discriminator: Optional[pydantic.Discriminator],
    ):
        self.model = model
        self.fields = fields
        self.discriminator = discriminator
        super().__init__()

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "Hint | Unrecognized | ParsingError":
        if not inspect.isclass(raw_hint) or not issubclass(raw_hint, BaseModel):
            return Unrecognized(raw_hint)

        fields: Dict[str, Tuple[Hint, Example]] = {}

        required_fields_first = sorted(
            raw_hint.model_fields.items(),
            key=lambda item: field_has_default_value(item[1]),
        )

        for field_name, field_info in required_fields_first:
            field_descriptor = f"{raw_hint.__name__}.{field_name}"
            field_hint = Hint.parse(
                raw_hint=get_field_annotation(field_info),
                # raw_hint=typing.get_type_hints(raw_hint, include_extras=True)[field_name],
                parent_raw_hints=[*parent_raw_hints, raw_hint],
                discriminator=None,  # discard discriminator as it only applies to the current ModelHint
            )

            if isinstance(field_hint, (ParsingError, Unrecognized)):
                return field_hint.with_context(
                    f"Could not parse type of field {field_descriptor}"
                )

            if field_info.examples is None or len(field_info.examples) == 0:
                raw_field_example = field_hint.get_example()
                if isinstance(raw_field_example, Exception):
                    return ParsingError(
                        f"Could not get example for {field_descriptor}: {raw_field_example}"
                    )
                raw_field_example = raw_field_example.value
            else:
                raw_field_example = field_info.examples[0]

            field_example = Example.try_from_value(raw_field_example)
            if isinstance(field_example, Exception):
                return ParsingError(
                    f"Could not get example for {field_descriptor}: {field_example}"
                )

            fields[field_name] = (field_hint, field_example)

        return ModelHint(model=raw_hint, fields=fields, discriminator=discriminator)

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text=self.model.__module__ + "." + self.model.__qualname__),
            *extra
        ])
        # fmt: on

    def get_example(self) -> "Example | Exception":
        return Example(
            {
                field_name: field_example.value
                for field_name, (_, field_example) in self.fields.items()
            }
        )

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        fields: List[FieldData] = []
        for field_name, (hint, example) in self.fields.items():
            field_info = self.model.model_fields[field_name]
            field_default = field_info.default
            if not isinstance(field_default, PydanticUndefinedType):
                field_default = Example.try_from_value(field_default)
                assert not isinstance(field_default, Exception)
            if self.discriminator and self.discriminator.discriminator == field_name:
                field_default = PydanticUndefined
            fields.append(
                FieldData(
                    name=field_name,
                    description=field_info.description,
                    example=example,
                    type_widget=hint.to_type_widget(path=[*path, field_name]),
                    default=field_default,
                )
            )

        return FieldsWidget(
            base_path=path,
            short_description=self.short_description(extra=extra_summary),
            fields=fields,
        )


PrimitiveType: TypeAlias = Union[
    Type[int], Type[float], Type[bool], Type[str], Type[None]
]


class PrimitiveHint(Hint):
    def __init__(self, hint_type: PrimitiveType):
        self.hint_type = hint_type
        super().__init__()

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "PrimitiveHint | Unrecognized | ParsingError":
        if raw_hint is None:
            raw_hint = type(None)
        if not inspect.isclass(raw_hint) or not issubclass(
            raw_hint, (int, float, bool, str, type(None))
        ):
            return Unrecognized(raw_hint=raw_hint)
        return PrimitiveHint(hint_type=raw_hint)

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text="null" if self.hint_type is type(None) else self.hint_type.__name__),
            *extra
        ])
        # fmt: on

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        return self.short_description(extra=extra_summary)

    def get_example(self) -> Example:
        hint_type = self.hint_type
        if hint_type is int:
            return Example(123456)
        if hint_type is float:
            return Example(3.14)
        if hint_type is bool:
            return Example(True)
        if hint_type is str:
            return Example("some free-format string")
        if hint_type is type(None):
            return Example(None)
        return Example("--- NO EXAMPLES PROVIDED ---")


def is_tuple_hint(
    hint: Any,
) -> bool:  # FIXME: can't use TypeGuard[types.GenericAlias] in py 3.8
    if inspect.isclass(hint) and hint.__name__ == "tuple":
        return True
    if issubclass(type(hint), type(typing.Tuple[int, str])):
        return any_is_subclass(hint.__origin__, tuple)
    return False


class NTuple(Hint):
    """Represents tuple a type-hint with all items defined, like Tuple[int, str]"""

    def __init__(
        self,
        generic_args: Sequence[Tuple[Hint, Example]],
    ):
        self.generic_args = generic_args
        super().__init__()

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "NTuple | Unrecognized | ParsingError":
        if not is_tuple_hint(raw_hint) or (... in raw_hint.__args__):
            return Unrecognized(raw_hint)
        generic_args: List[Tuple[Hint, Example]] = []
        for arg_inx, arg in enumerate(raw_hint.__args__):
            hint = Hint.parse(
                raw_hint=arg, parent_raw_hints=[*parent_raw_hints, raw_hint]
            )
            if isinstance(hint, (Unrecognized, ParsingError)):
                return hint.with_context(
                    f"Could not parse {arg_inx}-th NTuple type argument"
                )
            example = hint.get_example()
            if isinstance(example, Exception):
                return ParsingError(
                    f"Could not get example for {arg_inx}-th NTuple type argument: {example}"
                )
            generic_args.append((hint, example))
        return NTuple(generic_args=generic_args)

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        children: List[Widget] = []
        for arg_idx, (arg, _example) in enumerate(self.generic_args):
            children.append(arg.short_description())
            if arg_idx < len(self.generic_args) - 1:
                children.append(InlinePre(text=", "))

        # fmt: off
        return Widget("span", children=[
            InlinePre(text="("),
            *children,
            InlinePre(text=")"),
            *extra,
        ])
        # fmt: on

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        return FieldsWidget(
            base_path=path,
            short_description=self.short_description(extra=extra_summary),
            fields=[
                FieldData(
                    name=str(idx),
                    description=None,
                    type_widget=hint.to_type_widget(path=[*path, str(idx)]),
                    example=example,
                )
                for idx, (hint, example) in enumerate(self.generic_args)
            ],
        )

    def get_example(self) -> "Example | Exception":
        return Example(list(arg[1].value for arg in self.generic_args))


class VarLenTuple(Hint):
    """Represents a type-hint like Tuple[T, ...]"""

    def __init__(self, element_type: Hint, element_example: Example):
        self.element_type = element_type
        self.element_example = element_example
        super().__init__()

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "VarLenTuple | Unrecognized | ParsingError":
        if not is_tuple_hint(raw_hint):
            return Unrecognized(raw_hint=raw_hint)
        if len(raw_hint.__args__) != 2:
            return Unrecognized(raw_hint=raw_hint)
        last_type_arg = raw_hint.__args__[-1]
        if last_type_arg.__name__ != "ellipsis":
            return Unrecognized(raw_hint=raw_hint)
        element_hint = Hint.parse(
            raw_hint=raw_hint.__args__[0],
            parent_raw_hints=[*parent_raw_hints, raw_hint],
        )
        if isinstance(element_hint, (Unrecognized, Exception)):
            return element_hint.with_context(
                f"Could not parse VarLenTuple element type: {element_hint}"
            )
        element_example = element_hint.get_example()
        if isinstance(element_example, Exception):
            return ParsingError(
                f"Could not get example for element type: {element_example}"
            )
        return VarLenTuple(element_type=element_hint, element_example=element_example)

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        field_name = "[...]"
        return FieldsWidget(
            base_path=path,
            fields=[
                FieldData(
                    name=field_name,
                    description=None,
                    type_widget=self.element_type.to_type_widget(
                        path=[*path, field_name]
                    ),
                    example=self.element_example,
                )
            ],
            short_description=self.short_description(extra=extra_summary),
        )

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text="("),
            self.element_type.short_description(),
            InlinePre(text=", ...)"),
            *extra,
        ])
        # fmt: on

    def get_example(self) -> "Example | Exception":
        return Example([self.element_example.value])


class ListHint(Hint):
    """Represents a list-hint like List[T]"""

    def __init__(self, element_type: Hint, element_example: Example):
        self.element_type = element_type
        self.element_example = element_example
        super().__init__()

    @staticmethod
    def is_list_hint(
        hint: Any,
    ) -> bool:  # FIXME: can't use TypeGuard[types.GenericAlias] in py 3.8:
        if inspect.isclass(hint):
            return issubclass(hint, Sequence)
        if issubclass(type(hint), type(typing.Sequence[int])):
            return any_is_subclass(hint.__origin__, Sequence)
        return False

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "ListHint | Unrecognized | ParsingError":
        if not cls.is_list_hint(raw_hint):
            return Unrecognized(raw_hint=raw_hint)
        element_hint = Hint.parse(
            raw_hint=raw_hint.__args__[0],
            parent_raw_hints=[*parent_raw_hints, raw_hint],
        )
        if isinstance(element_hint, (Unrecognized, ParsingError)):
            return element_hint.with_context("Could not parse List element type")
        element_example = element_hint.get_example()
        if isinstance(element_example, Exception):
            return ParsingError(
                f"Could not get example for List element type: {element_example}"
            )
        return ListHint(element_type=element_hint, element_example=element_example)

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        field_name = "[...]"
        return FieldsWidget(
            base_path=path,
            fields=[
                FieldData(
                    name=field_name,
                    description=None,
                    type_widget=self.element_type.to_type_widget(
                        path=[*path, field_name]
                    ),
                    example=self.element_example,
                )
            ],
            short_description=self.short_description(extra=extra_summary),
        )

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        # fmt: off
        return Widget("span", children=[
            InlinePre(text="List["),
            self.element_type.short_description(),
            InlinePre(text="]"),
            *extra,
        ])
        # fmt: on

    def get_example(self) -> "Example | Exception":
        return Example([self.element_example.value])


class UnionHint(Hint):
    def __init__(self, args: Sequence[Tuple[Hint, Example]]):
        self.variant_hints = args
        super().__init__()

    @classmethod
    def do_parse(
        cls,
        raw_hint: Any,
        parent_raw_hints: Sequence[Any],
        discriminator: Optional[pydantic.Discriminator] = None,
    ) -> "UnionHint | Unrecognized | ParsingError":
        some_dummy_union = Union[int, str]
        if raw_hint.__class__ != some_dummy_union.__class__:
            return Unrecognized(raw_hint=raw_hint)

        union_args: List[Tuple[Hint, Example]] = []
        for arg_idx, arg in enumerate(raw_hint.__args__):
            hint = Hint.parse(
                raw_hint=arg,
                parent_raw_hints=[*parent_raw_hints, raw_hint],
                discriminator=discriminator,
            )
            if isinstance(hint, (Unrecognized, ParsingError)):
                return hint.with_context(
                    f"Could not parse Union arg #{arg_idx} in {raw_hint}"
                )
            if isinstance(hint, UnionHint):
                union_args += list(hint.variant_hints)
            else:
                example = hint.get_example()
                if isinstance(example, Exception):
                    return ParsingError(
                        f"Could not get example for variant {hint}: {example}"
                    )
                union_args.append((hint, example))
        return UnionHint(args=union_args)

    def to_type_widget(
        self, path: List[str], extra_summary: Sequence["Widget"] = ()
    ) -> "Widget":
        variant_widgets: List[Widget] = []
        for variant_index, (variant_hint, variant_example) in enumerate(
            self.variant_hints
        ):
            variant_path = [
                *path,
                f"VARIANT_{variant_index}",
            ]  # FIXME: maybe variant name?
            variant_type_widget = variant_hint.to_type_widget(path=variant_path)

            # fmt: off
            variant_widgets.append(Widget("tr", children=[
                Widget("td", css_classes=[FieldsWidget.FIELD_TYPE_CSS_CLASS], children=[
                    variant_type_widget
                ]),
                Widget("td", css_classes=[FieldsWidget.EXAMPLE_FIELD_CSS_CLASS], children=[ExampleWidget(variant_example)])
            ]))
            # fmt: on

        # fmt: off
        variants_table = Widget("table", children=[
            Widget("thead", children=[
                Widget("tr", children=[
                    Widget("th", text="variant type", css_classes=[FieldsWidget.TYPE_TABLE_HEADER]),
                    Widget("th", text="example yaml", css_classes=[FieldsWidget.EXAMPLE_TABLE_HEADER]),
                ])
            ]),
            Widget("tbody", children=variant_widgets)
        ])
        #fmt: on


        #fmt: off
        return Widget("details", children=[
            Widget("summary", children=[
                self.short_description(extra=extra_summary),
                ColumnControls(root_element_id=variants_table.element_id),
            ]),
            variants_table
        ])
        # fmt: on

    def short_description(self, extra: Sequence["Widget"] = ()) -> "Widget":
        children: List[Widget] = []
        if len(extra) > 0:
            children.append(InlinePre(text="("))
        for arg_idx, (arg_hint, _) in enumerate(self.variant_hints):
            children.append(arg_hint.short_description())
            if arg_idx < len(self.variant_hints) - 1:
                children.append(InlinePre(text=" | "))
        if len(extra) > 0:
            children.append(InlinePre(text=")"))
        return Widget("span", children=[*children, *extra])

    def get_example(self) -> "Example":
        return self.variant_hints[0][1]


class Widget:
    id_counter: ClassVar[int] = 0

    tag: Final[str]
    element: Final[et.Element]
    subclasses: ClassVar[List[Type["Widget"]]] = []

    def __init__(
        self,
        tag: str,
        *,
        text: Optional[str] = None,
        children: Sequence["Widget"] = (),
        css_classes: Optional[List[str]] = None,
        title: str = "",
        style: str = "",
        element_id: str = "",
        attribs: Mapping[str, str] = {},
    ):
        self.tag = tag
        self.element = et.Element(tag)
        self.element_id = element_id or f"autoid_{Widget.id_counter}"
        Widget.id_counter += 1

        if text is not None:
            self.element.text = text
        if css_classes and len(css_classes) > 0:
            self.element.set("class", " ".join(css_classes))
        if title:
            self.element.set("title", title)
        if style:
            self.element.set("style", style)
        for key, val in attribs.items():
            self.element.set(key, val)
        self.element.set("id", self.element_id)
        super().__init__()

        self.appendChildren(children)

    def appendChildren(self, children: Sequence["Widget"]):
        for child in children:
            self.element.append(child.element)

    def create_child(self, tag: str, children: Sequence["Widget"] = ()) -> "Widget":
        out = Widget(tag=tag, children=children)
        self.appendChildren([out])
        return out

    def to_html(self) -> str:
        return et.tostring(self.element, method="html", encoding="unicode")

    @classmethod
    def get_css(cls) -> str:
        if cls != Widget:
            return ""

        theme_border = "solid 1px black"
        theme_spacing = "0.2em"
        theme_color_warning = "yellow"

        subclasses_css = "\n".join(klass.get_css() for klass in Widget.subclasses)

        return f"""
            {subclasses_css}

            table{{
                border: {theme_border};
                border-collapse: collapse;
            }}
            th{{
                background-color: #312f46;
                color: white;
            }}
            .{AnnotatedHint.RESTRICTION_CSS_CLASS}{{
                background-color: {theme_color_warning};
            }}
            td{{
                vertical-align: top;
            }}

            /*border*/
            td, th{{
                border: {theme_border};
                border-collapse: collapse;
            }}

            th{{
                padding: {theme_spacing};
            }}
            td{{
                padding: 0;
            }}
            td:has(> table){{
                padding: 0;
            }}

            details{{
                padding: 0;
            }}
            details > table{{
                margin-left: 1em;
            }}
        """

    @classmethod
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        Widget.subclasses.append(cls)


class LiteralWidget(Widget):
    CSS_CLASS: ClassVar[str] = "literal_widget"

    @classmethod
    def get_css(cls) -> str:
        return f"""
            .{LiteralWidget.CSS_CLASS}{{
                color: #254604;
                font-family: monospace, monospace;
            }}
        """

    def __init__(self, *, value: "str | int | None | float"):
        super().__init__(
            "span", text=json.dumps(value), css_classes=[LiteralWidget.CSS_CLASS]
        )


class ExampleWidget(Widget):
    CSS_CLASS: ClassVar[str] = "example_widget"

    @classmethod
    def get_css(cls) -> str:
        return f"""
            .{ExampleWidget.CSS_CLASS}{{
                margin: 0;
            }}
        """

    def __init__(self, example: Example) -> None:
        text = example.to_yaml_str()
        if is_yaml_leaf_value(example.value):
            super().__init__(
                "pre",
                css_classes=[self.CSS_CLASS],
                children=[Widget("code", text=text, css_classes=["language-yaml"])],
            )
        else:
            super().__init__(
                "details",
                children=[
                    Widget("summary", text="example yaml"),
                    Widget(
                        "pre",
                        css_classes=[self.CSS_CLASS],
                        children=[
                            Widget("code", text=text, css_classes=["language-yaml"])
                        ],
                    ),
                ],
            )


class InlinePre(Widget):
    def __init__(
        self,
        *,
        text: Optional[str] = None,
        children: Sequence["Widget"] = (),
        css_classes: Optional[List[str]] = None,
    ):
        super().__init__(
            "span",
            text=text,
            children=children,
            css_classes=css_classes,
            style="font-family: monospace, monospace;",
        )


class WarningIconWidget(Widget):
    def __init__(self, title: str) -> None:
        super().__init__(
            "span",
            text="!",
            style="background-color: yellow; margin-right: 0.2em; margin-left: 0.2em; font-weight: bold;",
            title=title,
        )


class InfoIconWidget(Widget):
    CSS_CLASS: ClassVar[str] = "info_icon_widget"

    @classmethod
    def get_css(cls) -> str:
        return f"""
            .{InfoIconWidget.CSS_CLASS}{{
                opacity: 0.8;
                outline: solid 1px black;
                float: right;
                cursor: default;
            }}
        """

    def __init__(self, title: str) -> None:
        super().__init__(
            "span", text="?", css_classes=[InfoIconWidget.CSS_CLASS], title=title
        )


class OptMarkerWidget(Widget):
    CSS_CLASS: ClassVar[str] = "opt_marker_widget"

    @classmethod
    def get_css(cls) -> str:
        return f"""
            .{OptMarkerWidget.CSS_CLASS}{{
                background-color: yellow;
                color: black;
                font-weight: bold;
                padding: 1px;
                cursor: pointer;
                margin-right: 0.1em;
            }}
        """

    def __init__(self, default_value: Example):
        super().__init__(
            "span",
            text="opt",
            title=f"This field is optional and defaults to {default_value.to_json_str()}",
            css_classes=[OptMarkerWidget.CSS_CLASS],
        )


class CheckboxWidget(Widget):
    def __init__(
        self,
        *,
        text: Optional[str] = None,
        children: Sequence["Widget"] = (),
        on_click: str = "",
        css_classes: Optional[List[str]] = None,
        title: str = "",
        style: str = "",
    ):
        super().__init__("span")
        self._checkbox = Widget(
            "input",
            text=text,
            children=children,
            css_classes=css_classes,
            title=title,
            style=style,
        )
        self._checkbox.element.set("type", "checkbox")
        self._checkbox.element.set("checked", "checked")
        self.appendChildren([self._checkbox])
        if on_click:
            self.appendChildren(
                [
                    Widget(
                        "script",
                        text=f"""
                    document.getElementById("{self._checkbox.element_id}").addEventListener("click", (ev) => {{
                        {on_click}
                    }});
                """,
                    )
                ]
            )


class FragmentAnchorWidget(Widget):
    CSS_CLASS: Final[str] = "fragment_anchor_widget"

    @classmethod
    def get_css(cls) -> str:
        return f"""
            .{cls.CSS_CLASS}{{
                color: black;
                text-decoration: none;
                cursor: pointer;
            }}
            .{cls.CSS_CLASS}:hover{{
                text-decoration: underline;
            }}
        """

    def __init__(
        self,
        *,
        text: str = "",
        children: Sequence["Widget"] = (),
        path: List[str],
    ):
        fragment_contents = ".".join(path)
        super().__init__(
            "a",
            text=text,
            children=children,
            css_classes=[self.CSS_CLASS],
            title=fragment_contents,
            element_id=fragment_contents,
            attribs={"href": f"#{fragment_contents}"},
        )


class ColumnControls(Widget):
    CSS_CLASS: ClassVar[str] = "column_controls_widget"
    TYPES_CHECKBOX_CSS_CLASS: Final[str] = "types_checkbox"
    EXAMPLES_CHECKBOX_CSS_CLASS: Final[str] = "examples_checkbox"

    @classmethod
    def get_css(cls) -> str:
        return f"""
            .{ColumnControls.CSS_CLASS}{{
                font-weight: normal;
                background-color: rgba(0,0,0, 0.1);
            }}
        """

    def __init__(
        self, root_element_id: str, style: str = "float: right; margin-left: 4em;"
    ):
        # fmt: off
        super().__init__(
            "span",
            style=style,
            css_classes=[ColumnControls.CSS_CLASS],
            children=[
                CheckboxWidget(
                    text="Ty",
                    css_classes=[self.TYPES_CHECKBOX_CSS_CLASS],
                    on_click=f"""
                        const table = document.querySelector("#{root_element_id}");
                        for(const ex of table.querySelectorAll(".{FieldsWidget.FIELD_TYPE_CSS_CLASS}, .{FieldsWidget.TYPE_TABLE_HEADER}")){{
                            ex.style.display = ev.target.checked ? "" : "none"
                        }}
                        for(const cb of table.querySelectorAll(".{self.TYPES_CHECKBOX_CSS_CLASS}")){{
                            cb.checked = ev.target.checked
                        }}
                    """,
                ),
                CheckboxWidget(
                    text="e.g.",
                    css_classes=[self.EXAMPLES_CHECKBOX_CSS_CLASS],
                    on_click=f"""
                        const table = document.querySelector("#{root_element_id}");
                        for(const ex of table.querySelectorAll(".{FieldsWidget.EXAMPLE_FIELD_CSS_CLASS}, .{FieldsWidget.EXAMPLE_TABLE_HEADER}")){{
                            ex.style.display = ev.target.checked ? "" : "none"
                        }}
                        for(const cb of table.querySelectorAll(".{self.EXAMPLES_CHECKBOX_CSS_CLASS}")){{
                            cb.checked = ev.target.checked
                        }}
                    """,
                ),
            ],
        )
        # fmt: on


@dataclass
class FieldData:
    name: str
    description: Optional[str]
    type_widget: Widget
    example: Optional[Example]
    default: "Example | PydanticUndefinedType" = PydanticUndefined


class FieldsWidget(Widget):
    FIELD_NAME_CSS_CLASS: ClassVar[str] = "field_name"
    FIELD_TYPE_CSS_CLASS: ClassVar[str] = "field_type"
    TYPE_TABLE_HEADER: ClassVar[str] = "type_header"
    EXAMPLE_TABLE_HEADER: ClassVar[str] = "example_header"
    EXAMPLE_FIELD_CSS_CLASS: ClassVar[str] = "example_field"
    TYPES_CHECKBOX_CSS_CLASS: ClassVar[str] = "types_checkbox"
    EXAMPLES_CHECKBOX_CSS_CLASS: ClassVar[str] = "examples_checkbox"

    @classmethod
    def get_css(cls) -> str:
        return f"""
            .{cls.FIELD_NAME_CSS_CLASS}{{
                background-color: white;
                font-weight: normal;
                padding: 0.3em;
            }}
            .{cls.FIELD_TYPE_CSS_CLASS}{{
                background-color: #84b4dd;
                font-weight: bold;
                padding: 0.3em;
            }}
            .{cls.EXAMPLE_FIELD_CSS_CLASS}{{
                background-color: #f6f5b2;
                font-weight: normal;
            }}
            .{cls.EXAMPLE_TABLE_HEADER}{{

            }}
        """

    def __init__(
        self,
        base_path: List[str],
        short_description: Widget,
        fields: Sequence[FieldData],
    ) -> None:
        # fmt: off
        fields_table = Widget("table", children=[
            Widget("thead", children=[
                Widget("tr", children=[
                    Widget("th", text="field name"),
                    Widget("th", text="field type", css_classes=[self.TYPE_TABLE_HEADER]),
                    Widget("th", text="example yaml", css_classes=[self.EXAMPLE_TABLE_HEADER]),
                ])
            ]),
            Widget("tbody", children=[
                Widget("tr", children=[
                    Widget("td", css_classes=[self.FIELD_NAME_CSS_CLASS], children=[
                        FragmentAnchorWidget(text=field.name, path=[*base_path, field.name]),
                        *([OptMarkerWidget(default_value=field.default)] if not isinstance(field.default, PydanticUndefinedType) else []),
                        *([InfoIconWidget(title=field.description)] if field.description else [])
                    ]),
                    Widget("td", css_classes=[self.FIELD_TYPE_CSS_CLASS], children=[field.type_widget]),
                    Widget("td", css_classes=[self.EXAMPLE_FIELD_CSS_CLASS], children=[
                        ExampleWidget(example=field.example) if field.example is not None else Widget("span", text="NO EXAMPLE")
                    ])
                ])
                for field in fields
                    ],
                ),
            ],
        )
        # fmt: on

        # fmt: off
        super().__init__("details", children=[
            Widget("summary", children=[
                FragmentAnchorWidget(children=[short_description], path=base_path),
                ColumnControls(root_element_id=fields_table.element_id)
            ]),
            fields_table,
        ])
        # fmt: on
