"""fields to be used in the versioned schemas (may return shared raw nodes on `deserialize`"""
import datetime
import distutils.version
import pathlib
import typing
from urllib.parse import urlparse
from urllib.request import url2pathname

import marshmallow_union
import numpy
from marshmallow import ValidationError, fields as marshmallow_fields

from bioimageio.spec.shared import field_validators
from . import raw_nodes


class DocumentedField:
    """base class for all fields that aids in generating a documentation"""

    def __init__(
        self,
        *super_args,
        bioimageio_description: str = "",
        bioimageio_description_order: typing.Optional[int] = None,
        bioimageio_maybe_required: bool = False,  # indicates that this field may be required, depending on other fields
        bioimageio_examples_valid: typing.Optional[
            typing.Sequence[typing.Any]
        ] = None,  # valid examples to render in documentation
        bioimageio_examples_invalid: typing.Optional[
            typing.Sequence[typing.Any]
        ] = None,  # invalid examples to render in documentation
        **super_kwargs,
    ):
        bases = [b.__name__ for b in self.__class__.__bases__ if issubclass(b, marshmallow_fields.Field)]
        if self.__class__.__name__ not in bases:
            bases.insert(0, self.__class__.__name__)

        # if bioimageio_examples_valid is not None:
        #     valid_examples =
        self.type_name = "→".join(bases)
        self.bioimageio_description = bioimageio_description
        self.bioimageio_description_order = bioimageio_description_order
        self.bioimageio_maybe_required = bioimageio_maybe_required
        super().__init__(*super_args, **super_kwargs)  # type: ignore


#################################################
# fields directly derived from marshmallow fields
#################################################


class Array(DocumentedField, marshmallow_fields.Field):
    def __init__(self, inner: marshmallow_fields.Field, **kwargs):
        self.inner = inner
        super().__init__(**kwargs)

    @property
    def dtype(self) -> typing.Union[typing.Type[int], typing.Type[float], typing.Type[str]]:
        if isinstance(self.inner, Integer):
            return int
        elif isinstance(self.inner, Float):
            return float
        elif isinstance(self.inner, String):
            return str
        else:
            raise NotImplementedError(self.inner)

    def _deserialize_inner(self, value):
        if isinstance(value, list):
            return [self._deserialize_inner(v) for v in value]
        else:
            return self.inner.deserialize(value)

    def deserialize(self, value: typing.Any, attr: str = None, data: typing.Mapping[str, typing.Any] = None, **kwargs):
        value = self._deserialize_inner(value)

        if isinstance(value, list):
            try:
                return numpy.array(value, dtype=self.dtype)
            except ValueError as e:
                raise ValidationError(str(e)) from e
        else:
            return value


class DateTime(DocumentedField, marshmallow_fields.DateTime):
    """
    Parses datetime in ISO8601 or if value already has datetime.datetime type
    returns this value
    """

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, datetime.datetime):
            return value

        return super()._deserialize(value, attr, data, **kwargs)


class Dict(DocumentedField, marshmallow_fields.Dict):
    def __init__(self, *super_args, **super_kwargs):
        super().__init__(*super_args, **super_kwargs)
        # add types of dict keys and values
        key = "Any" if self.key_field is None else self.key_field.type_name
        value = "Any" if self.value_field is None else self.value_field.type_name
        self.type_name += f"\\[{key}, {value}\\]"


class Float(DocumentedField, marshmallow_fields.Float):
    pass


class Integer(DocumentedField, marshmallow_fields.Integer):
    pass


class List(DocumentedField, marshmallow_fields.List):
    def __init__(self, *super_args, **super_kwargs):
        super().__init__(*super_args, **super_kwargs)
        self.type_name += f"\\[{self.inner.type_name}\\]"  # add type of list elements


class Number(DocumentedField, marshmallow_fields.Number):
    pass


class Nested(DocumentedField, marshmallow_fields.Nested):
    def __init__(self, *super_args, **super_kwargs):
        super().__init__(*super_args, **super_kwargs)

        self.type_name = self.schema.__class__.__name__
        if self.many:
            self.type_name = f"List\\[{self.type_name}\\]"

        if not self.bioimageio_description:
            self.bioimageio_description = self.schema.bioimageio_description

        repeat_type_name = self.type_name if self.bioimageio_description else ""
        self.bioimageio_description += f" {repeat_type_name} is a Dict with the following keys:"


class String(DocumentedField, marshmallow_fields.String):
    pass


class Tuple(DocumentedField, marshmallow_fields.Tuple):
    def _serialize(self, value, attr, obj, **kwargs) -> typing.List:
        value = super()._serialize(value, attr, obj, **kwargs)
        return list(value)  # return tuple as list

    def _jsonschema_type_mapping(self):
        import marshmallow_jsonschema

        return {
            "type": "array",
            "items": [marshmallow_jsonschema.JSONSchema()._get_schema_for_field(self, tf) for tf in self.tuple_fields],
        }


class Union(DocumentedField, marshmallow_union.Union):
    _candidate_fields: typing.Iterable[typing.Union[DocumentedField, marshmallow_fields.Field]]

    def __init__(self, *super_args, **super_kwargs):
        super().__init__(*super_args, **super_kwargs)
        self.type_name += f"\\[{' | '.join(cf.type_name for cf in self._candidate_fields)}\\]"  # add types of options


#########################
# more specialized fields
#########################


class Axes(String):
    def _deserialize(self, *args, **kwargs) -> str:
        axes_str = super()._deserialize(*args, **kwargs)
        valid_axes = self.metadata.get("valid_axes", "bitczyx")
        if any(a not in valid_axes for a in axes_str):
            raise ValidationError(f"Invalid axes! Valid axes consist of: {valid_axes}")

        return axes_str


class Dependencies(String):  # todo: check format of dependency string
    pass


class ExplicitShape(List):
    def __init__(self, **super_kwargs):
        super().__init__(Integer, **super_kwargs)


class ImportableSource(String):
    @staticmethod
    def _is_import(path):
        return ":" not in path

    @staticmethod
    def _is_filepath(path):
        return ":" in path

    def _deserialize(self, *args, **kwargs) -> typing.Any:
        source_str: str = super()._deserialize(*args, **kwargs)
        if self._is_import(source_str):
            last_dot_idx = source_str.rfind(".")

            module_name = source_str[:last_dot_idx]
            object_name = source_str[last_dot_idx + 1 :]

            if not module_name:
                raise ValidationError(
                    f"Missing module name in importable source: {source_str}. Is it just missing a dot?"
                )

            if not object_name:
                raise ValidationError(
                    f"Missing object/callable name in importable source: {source_str}. Is it just missing a dot?"
                )

            return raw_nodes.ImportableModule(callable_name=object_name, module_name=module_name)

        elif self._is_filepath(source_str):
            if source_str.startswith("/"):
                raise ValidationError("Only relative paths are allowed")

            parts = source_str.replace("::", ":").split(":")
            if len(parts) != 2:
                raise ValidationError("Incorrect source_file format, expected example.py:ClassName")

            module_uri, object_name = parts

            return raw_nodes.ImportableSourceFile(callable_name=object_name, source_file=URI().deserialize(module_uri))
        else:
            raise ValidationError(source_str)

    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[str]:
        if value is None:
            return None
        elif isinstance(value, raw_nodes.ImportableModule):
            return f"{value.module_name}.{value.callable_name}"
        elif isinstance(value, raw_nodes.ImportableSourceFile):
            return f"{value.source_file}:{value.callable_name}"
        else:
            raise TypeError(f"{value} has unexpected type {type(value)}")


class InputShape(Union):
    def __init__(self, **super_kwargs):
        from .schema import ImplicitInputShape

        super().__init__(
            fields=[
                ExplicitShape(
                    bioimageio_description="Exact shape with same length as `axes`, e.g. `shape: [1, 512, 512, 1]`"
                ),
                Nested(
                    ImplicitInputShape,
                    bioimageio_description="A sequence of valid shapes given by `shape = min + k * step for k in {0, 1, ...}`.",
                ),
            ],
            **super_kwargs,
        )


class Kwargs(Dict):
    def __init__(self, keys=String, bioimageio_description="Key word arguments.", **super_kwargs):
        super().__init__(keys, bioimageio_description=bioimageio_description, **super_kwargs)


class OutputShape(Union):
    def __init__(self, **super_kwargs):
        from .schema import ImplicitOutputShape

        super().__init__(
            fields=[
                ExplicitShape(),
                Nested(
                    ImplicitOutputShape,
                    bioimageio_description="In reference to the shape of an input tensor, the shape of the output "
                    "tensor is `shape = shape(input_tensor) * scale + 2 * offset`.",
                ),
            ],
            **super_kwargs,
        )


class Path(String):
    def _deserialize(self, *args, **kwargs):
        path_str = super()._deserialize(*args, **kwargs)
        return pathlib.Path(path_str)

    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[str]:
        return None if value is None else pathlib.Path(value).as_posix()


class RelativeLocalPath(Path):
    def __init__(
        self,
        *super_args,
        validate: typing.Optional[
            typing.Union[
                typing.Callable[[typing.Any], typing.Any], typing.Iterable[typing.Callable[[typing.Any], typing.Any]]
            ]
        ] = None,
        **super_kwargs,
    ):
        if validate is None:
            validate = []
        elif callable(validate):
            validate = [validate]
        else:
            validate = list(validate)

        super().__init__(
            *super_args,
            validate=validate
            + [
                field_validators.Predicate("is_absolute", invert_output=True, error="expected relative path."),
                field_validators.Attribute(
                    "as_posix",
                    [
                        field_validators.ContainsNoneOf(
                            ":", error="expected local, relative file path."
                        ),  # monkey patch to fail on urls
                        field_validators.Predicate(
                            "count", "..", invert_output=True, error="expected relative file path within model package."
                        ),
                    ],
                    is_getter_method=True,
                ),
                field_validators.Predicate(
                    "is_reserved", invert_output=True, error="invalid filename as it is a reserved by the OS."
                ),
            ],
            **super_kwargs,
        )

    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[str]:
        if value is not None:
            assert isinstance(value, pathlib.Path), value
            assert not value.is_absolute(), value

        return super()._serialize(value, attr, obj, **kwargs)


class ProcMode(String):
    all_modes = ("fixed", "per_dataset", "per_sample")

    def __init__(
        self,
        *,
        validate: typing.Optional[
            typing.Union[
                typing.Callable[[typing.Any], typing.Any], typing.Iterable[typing.Callable[[typing.Any], typing.Any]]
            ]
        ] = None,
        valid_modes: typing.Sequence[str] = all_modes,
        required=True,
        **kwargs,
    ) -> None:
        assert all(vm in self.all_modes for vm in valid_modes), valid_modes

        if validate is None:
            validate = []

        if isinstance(validate, typing.Iterable):
            validate = list(validate)
        else:
            validate = [validate]

        validate.append(field_validators.OneOf(self.all_modes))
        super().__init__(validate=validate, required=required, **kwargs)


class SHA256(String):
    def _deserialize(self, *args, **kwargs):
        value_str = super()._deserialize(*args, **kwargs)
        return value_str


class SpecURI(Nested):
    def _deserialize(self, value, attr, data, **kwargs):
        uri = urlparse(value)

        if uri.query:
            raise ValidationError(f"Invalid URI: {value}. We do not support query: {uri.query}")
        if uri.fragment:
            raise ValidationError(f"Invalid URI: {value}. We do not support fragment: {uri.fragment}")
        if uri.params:
            raise ValidationError(f"Invalid URI: {value}. We do not support params: {uri.params}")

        if uri.scheme == "file":
            # account for leading '/' for windows paths, e.g. '/C:/folder'
            # see https://stackoverflow.com/questions/43911052/urlparse-on-a-windows-file-scheme-uri-leaves-extra-slash-at-start
            path = url2pathname(uri.path)
        else:
            path = uri.path

        return raw_nodes.SpecURI(
            spec_schema=self.schema, scheme=uri.scheme, authority=uri.netloc, path=path, query="", fragment=""
        )


class StrictVersion(String):
    def _deserialize(
        self,
        value: typing.Any,
        attr: typing.Optional[str],
        data: typing.Optional[typing.Mapping[str, typing.Any]],
        **kwargs,
    ):
        return distutils.version.StrictVersion(str(value))


class URI(String):
    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        try:
            return raw_nodes.URI(uri_string=value)
        except Exception as e:
            raise ValidationError(value) from e
