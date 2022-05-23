"""fields to be used in the versioned schemas (may return shared raw nodes on `deserialize`"""
import datetime
import packaging.version
import logging
import pathlib
import typing

import marshmallow_union
import numpy
from marshmallow import Schema, ValidationError, fields as marshmallow_fields, missing

from . import field_validators, raw_nodes
from .utils._docs import resolve_bioimageio_descrcription

logger = logging.getLogger(__name__)


class DocumentedField:
    """base class for all fields that aids in generating a documentation"""

    def __init__(
        self,
        *super_args,
        short_bioimageio_description: typing.Union[str, typing.Callable[[], str]] = "",
        bioimageio_description: typing.Union[str, typing.Callable[[], str]] = "",
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

        # todo: support examples for documentation
        # if bioimageio_examples_valid is not None:
        #     valid_examples =
        self.type_name = "→".join(bases)
        self.short_bioimageio_description = short_bioimageio_description
        self.bioimageio_description = bioimageio_description
        self.bioimageio_description_order = bioimageio_description_order
        self.bioimageio_maybe_required = bioimageio_maybe_required
        super().__init__(*super_args, **super_kwargs)  # type: ignore


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
    def __init__(
        self,
        keys: typing.Optional[DocumentedField] = None,
        values: typing.Optional[DocumentedField] = None,
        *super_args,
        **super_kwargs,
    ):
        assert keys is None or isinstance(keys, DocumentedField)
        assert values is None or isinstance(values, DocumentedField)
        super().__init__(keys, values, *super_args, **super_kwargs)
        # add types of dict keys and values
        key = "Any" if self.key_field is None else self.key_field.type_name
        value = "Any" if self.value_field is None else self.value_field.type_name
        self.type_name += f"\\[{key}, {value}\\]"


class YamlDict(Dict):
    """yaml friendly dict"""

    @staticmethod
    def _make_yaml_friendly(obj):
        if isinstance(obj, (list, tuple)):
            return [YamlDict._make_yaml_friendly(ob) for ob in obj if ob is not missing]
        elif isinstance(obj, dict):
            return {
                YamlDict._make_yaml_friendly(k): YamlDict._make_yaml_friendly(v)
                for k, v in obj.items()
                if v is not missing
            }
        elif obj is None or isinstance(obj, (float, int, str, bool)):
            return obj
        elif isinstance(obj, pathlib.PurePath):
            return obj.as_posix()
        elif isinstance(obj, raw_nodes.URI):
            return str(obj)
        elif isinstance(obj, (datetime.datetime, datetime.time)):
            return obj.isoformat()
        elif obj is missing:
            return missing
        else:
            raise TypeError(f"Encountered YAML unfriendly type: {type(obj)}")

    def _serialize(self, value, attr, obj, **kwargs):
        value = self._make_yaml_friendly(value)
        return super()._serialize(value, attr, obj, **kwargs)


class RDF_Update(YamlDict):
    def __init__(
        self,
        keys: typing.Optional[DocumentedField] = None,
        values: typing.Optional[DocumentedField] = None,
        *args,
        **kwargs,
    ):
        if keys is None:
            keys = String(bioimageio_description="RDF field names to overwrite")

        super().__init__(keys, values, *args, **kwargs)


class Email(DocumentedField, marshmallow_fields.Email):
    pass


class Float(DocumentedField, marshmallow_fields.Float):
    pass


class Integer(DocumentedField, marshmallow_fields.Integer):
    pass


class List(DocumentedField, marshmallow_fields.List):
    def __init__(self, instance: DocumentedField, *super_args, **super_kwargs):
        assert isinstance(instance, DocumentedField), "classes not allowd to avoid trouble"
        super().__init__(instance, *super_args, **super_kwargs)
        self.type_name += f"\\[{self.inner.type_name}\\]"  # add type of list elements


class Number(DocumentedField, marshmallow_fields.Number):
    pass


class Nested(DocumentedField, marshmallow_fields.Nested):
    def __init__(self, nested: Schema, *super_args, many: bool = False, **super_kwargs):
        assert isinstance(nested, Schema)  # schema classes cause all sorts of trouble (so we enforce instance)
        assert not many, (
            "Use List(Nested(...)) or Nested(Schema(many=True)) instead! "
            "see also https://github.com/marshmallow-code/marshmallow/issues/779"
            "We only don't allow this to be more consistent and avoid bugs."
        )
        super().__init__(nested, *super_args, **super_kwargs)

        self.type_name = self.schema.__class__.__name__
        if self.many:
            self.type_name = f"List\\[{self.type_name}\\]"

        if not self.bioimageio_description:
            self.bioimageio_description = self.schema.bioimageio_description

        if not self.short_bioimageio_description:
            self.short_bioimageio_description = self.schema.short_bioimageio_description

        repeat_type_name = self.type_name if self.bioimageio_description else ""
        add_to_descr = f" {repeat_type_name} is a Dict with the following keys:"
        bioimageio_description_part = self.bioimageio_description
        self.bioimageio_description = (
            lambda: resolve_bioimageio_descrcription(bioimageio_description_part) + add_to_descr
        )

    def _deserialize(self, value, attr, data, partial=None, **kwargs):
        if not isinstance(value, dict):
            raise ValidationError(f"Expected dictionary, but got {type(value).__name__}.")

        return super()._deserialize(value, attr, data, partial, **kwargs)


class Raw(DocumentedField, marshmallow_fields.Raw):
    pass


class String(DocumentedField, marshmallow_fields.String):
    pass


class Name(String):
    def __init__(
        self,
        *,
        validate: typing.Optional[
            typing.Union[
                typing.Callable[[typing.Any], typing.Any], typing.Iterable[typing.Callable[[typing.Any], typing.Any]]
            ]
        ] = None,
        **kwargs,
    ) -> None:
        if validate is None:
            validate = []

        if isinstance(validate, typing.Iterable):
            validate = list(validate)
        else:
            validate = [validate]

        validate.append(
            field_validators.Predicate("__contains__", "/", invert_output=True, error="may not contain '/'")
        )
        validate.append(
            field_validators.Predicate("__contains__", "\\", invert_output=True, error="may not contain '\\'")
        )
        super().__init__(validate=validate, **kwargs)


class DOI(String):
    pass


class Tuple(DocumentedField, marshmallow_fields.Tuple):
    def __init__(self, tuple_fields: typing.Sequence[DocumentedField], *args, **kwargs):
        assert all(isinstance(tf, DocumentedField) for tf in tuple_fields)
        super().__init__(tuple_fields, *args, **kwargs)

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

    def __init__(self, fields_, *super_args, **super_kwargs):
        assert all(isinstance(f, DocumentedField) for f in fields_), "only DocumentedField instances (no classes)!"
        super().__init__(fields_, *super_args, **super_kwargs)
        self.type_name += f"\\[{' | '.join(cf.type_name for cf in self._candidate_fields)}\\]"  # add types of options

    def _deserialize(self, value, attr=None, data=None, **kwargs):
        try:
            return super()._deserialize(value, attr=attr, data=data, **kwargs)
        except ValidationError as e:
            errors = sorted(e.messages, key=lambda msg: len(msg))
            messages = ["Errors in all options for this field. Fix any of the following errors:"] + errors
            raise ValidationError(message=messages, field_name=attr) from e


class Axes(String):
    def _deserialize(self, *args, **kwargs) -> str:
        axes_str = super()._deserialize(*args, **kwargs)
        valid_axes = self.metadata.get("valid_axes", "bitczyx")
        if any(a not in valid_axes for a in axes_str):
            raise ValidationError(f"Invalid axes! Valid axes consist of: {valid_axes}")

        return axes_str


class Dependencies(String):  # todo: check format of dependency string
    def _deserialize(self, *args, **kwargs) -> raw_nodes.Dependencies:
        from . import schema

        dep_str = super()._deserialize(*args, **kwargs)
        try:
            manager, *file_parts = dep_str.split(":")
            data = dict(manager=manager, file=":".join(file_parts))
            ret = schema.Dependencies().load(data)
        except Exception as e:
            raise ValidationError(f"Invalid dependency: {dep_str} ({e})")

        return ret


class ExplicitShape(List):
    def __init__(self, **super_kwargs):
        super().__init__(Integer(), **super_kwargs)


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
            *module_uri_parts, object_name = source_str.split(":")
            module_uri = ":".join(module_uri_parts).strip(":")

            source_file_field = Union(
                [
                    URL(),
                    Path(
                        validate=field_validators.Attribute(
                            "suffix",
                            field_validators.Equal(
                                ".py", error="{!r} is invalid; expected python source file with '.py' extension."
                            ),
                        )
                    ),
                ]
            )
            return raw_nodes.ImportableSourceFile(
                callable_name=object_name, source_file=source_file_field.deserialize(module_uri)
            )
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


class Kwargs(Dict):
    def __init__(
        self,
        keys: String = String(),
        values: typing.Optional[DocumentedField] = None,
        bioimageio_description="Key word arguments.",
        **super_kwargs,
    ):
        super().__init__(keys, values, bioimageio_description=bioimageio_description, **super_kwargs)


class Path(String):
    def _deserialize(self, *args, **kwargs):
        path_str = super()._deserialize(*args, **kwargs)
        return pathlib.Path(path_str)

    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[str]:
        if isinstance(value, pathlib.PurePath):
            value = value.as_posix()

        return super()._serialize(value, attr, obj, **kwargs)


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
                    "is_reserved", invert_output=True, error="invalid filename as it is reserved by the OS."
                ),
            ],
            **super_kwargs,
        )

    def _serialize(self, value, attr, obj, **kwargs) -> typing.Optional[str]:
        if value is not None and (not isinstance(value, pathlib.Path) or value.is_absolute()):
            logger.warning(f"invalid local relative path: {value}")

        return super()._serialize(value, attr, obj, **kwargs)


class BioImageIO_ID(String):
    def __init__(
        self,
        *super_args,
        bioimageio_description: typing.Union[
            str, typing.Callable[[], str]
        ] = "ID as shown on resource card on bioimage.io",
        resource_type: typing.Optional[str] = None,
        validate: typing.Optional[
            typing.Union[
                typing.Callable[[typing.Any], typing.Any], typing.Iterable[typing.Callable[[typing.Any], typing.Any]]
            ]
        ] = None,
        **super_kwargs,
    ):
        from ._resolve_source import BIOIMAGEIO_COLLECTION_ENTRIES

        if validate is None:
            validate = []

        if isinstance(validate, typing.Iterable):
            validate = list(validate)
        else:
            validate = [validate]

        if BIOIMAGEIO_COLLECTION_ENTRIES is not None:
            error_msg = "'{input}' is not a valid BioImage.IO ID"
            if resource_type is not None:
                error_msg += f" of type {resource_type}"

            validate.append(
                field_validators.OneOf(
                    {
                        k
                        for k, (v_type, _) in BIOIMAGEIO_COLLECTION_ENTRIES.items()
                        if resource_type is None or resource_type == v_type
                    },
                    error=error_msg,
                )
            )

        super().__init__(*super_args, bioimageio_description=bioimageio_description, **super_kwargs)


class ProcMode(String):
    all_modes = ("fixed", "per_dataset", "per_sample")
    explanations = {
        "fixed": "fixed values for mean and variance",
        "per_dataset": "mean and variance are computed for the entire dataset",
        "per_sample": "mean and variance are computed for each sample individually",
    }

    def __init__(
        self,
        *,
        validate: typing.Optional[
            typing.Union[
                typing.Callable[[typing.Any], typing.Any], typing.Iterable[typing.Callable[[typing.Any], typing.Any]]
            ]
        ] = None,
        valid_modes: typing.Sequence[str] = all_modes,
        required: bool = True,
        bioimageio_description: str = "",
        **kwargs,
    ) -> None:
        assert all(vm in self.all_modes for vm in valid_modes), valid_modes
        self.valid_modes = valid_modes  # used in doc generation script 'generate_processing_docs.py'
        if validate is None:
            validate = []

        if isinstance(validate, typing.Iterable):
            validate = list(validate)
        else:
            validate = [validate]

        validate.append(field_validators.OneOf(valid_modes))
        if not bioimageio_description:
            bioimageio_description = f"One of {', '.join([f'{vm} ({self.explanations[vm]})' for vm in valid_modes])}"
        super().__init__(validate=validate, required=required, bioimageio_description=bioimageio_description, **kwargs)


class SHA256(String):
    def _deserialize(self, *args, **kwargs):
        value_str = super()._deserialize(*args, **kwargs)
        return value_str


class Version(String):
    def _deserialize(
        self,
        value: typing.Any,
        attr: typing.Optional[str],
        data: typing.Optional[typing.Mapping[str, typing.Any]],
        **kwargs,
    ):
        return packaging.version.Version(str(value))


class URI(String):
    def _deserialize(self, value, attr, data, **kwargs) -> typing.Any:
        try:
            return raw_nodes.URI(uri_string=value)
        except Exception as e:
            raise ValidationError(str(e)) from e


class URL(URI):
    def __init__(self, *, validate: typing.Sequence[field_validators.Validator] = tuple(), **kwargs):
        validate = list(validate) + [field_validators.URL(schemes=["http", "https"])]
        super().__init__(validate=validate, **kwargs)
