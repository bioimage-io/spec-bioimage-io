import pathlib
from datetime import datetime, timezone
from typing import Any, Dict

import numpy
import pytest
from marshmallow import Schema, ValidationError
from numpy.testing import assert_equal
from pytest import raises

from bioimageio.spec.model import schema
from bioimageio.spec.shared import fields, raw_nodes


class TestArray:
    def test_unequal_nesting_depth(self):
        with raises(ValidationError):
            fields.Array(fields.Integer(strict=True)).deserialize([[1, 2], 3])

    def test_uneuqal_sublen(self):
        with raises(ValidationError):
            fields.Array(fields.Integer(strict=True)).deserialize([[1, 2], [3]])

    def test_scalar(self):
        data = 1
        expected = data
        actual = fields.Array(fields.Integer(strict=True)).deserialize(data)
        assert_equal(actual, expected)

    def test_invalid_scalar(self):
        data = "invalid"
        with raises(ValidationError):
            fields.Array(fields.Integer(strict=True)).deserialize(data)

    def test_2d(self):
        data = [[1, 2], [3, 4]]
        expected = numpy.array(data, dtype=int)
        actual = fields.Array(fields.Integer(strict=True)).deserialize(data)
        assert_equal(actual, expected)

    def test_wrong_dtype(self):
        data = [[1, 2], [3, 4.5]]
        with raises(ValidationError):
            fields.Array(fields.Integer(strict=True)).deserialize(data)


class TestDateTime:
    def test_datetime_from_str(self):
        timestamp = "2019-12-11T12:22:32+00:00"
        expected = datetime.fromisoformat(timestamp)
        actual = fields.DateTime().deserialize(timestamp)
        assert expected == actual

    def test_datetime_from_datetime(self):
        expected = datetime.now()
        assert expected == fields.DateTime().deserialize(expected)

    def test_datetime_iso_with_zulu_offset(self):
        timestamp_non_zulu = "2019-12-11T12:22:32+00:00"
        timestamp_zulu = "2019-12-11T12:22:32Z"
        expected = datetime(2019, 12, 11, 12, 22, 32, tzinfo=timezone.utc)
        actual1 = fields.DateTime().deserialize(timestamp_non_zulu)
        actual2 = fields.DateTime().deserialize(timestamp_zulu)
        assert expected == actual1
        assert expected == actual2


class TestShape:
    def test_explicit_input_shape(self):
        data = [1, 2, 3]
        expected = data
        actual = fields.ExplicitShape().deserialize(data)
        assert expected == actual

    def test_explicit_output_shape(self):
        data = [1, 2, 3]
        expected = data
        actual = schema.OutputTensor().fields["shape"].deserialize(data)
        assert expected == actual

    def test_min_step_input_shape(self):
        data = {"min": [1, 2, 3], "step": [0, 1, 3]}
        expected = raw_nodes.ParametrizedInputShape(**data)
        actual = fields.Union(
            [fields.ExplicitShape(), fields.Nested(schema.ParametrizedInputShape())], required=True
        ).deserialize(data)
        assert actual == expected

    def test_output_shape(self):
        data: Dict[str, Any] = {"reference_tensor": "in1", "scale": [1, 2, 3], "offset": [0, 1, 3]}
        expected = raw_nodes.ImplicitOutputShape(**data)
        actual = fields.Union(
            [fields.ExplicitShape(), fields.Nested(schema.ImplicitOutputShape())], required=True
        ).deserialize(data)
        assert actual == expected


class TestURI:
    def test_missing_scheme_is_invalid(self):
        # local relative paths used to be valid "uris"
        relative_path = "relative_file/path.txt"

        with pytest.raises(ValidationError):
            fields.URI().deserialize(relative_path)


class TestUnion:
    def test_error_messages(self):
        union = fields.Union([fields.String(), fields.Number()])
        try:
            union.deserialize([1])
        except ValidationError as e:
            assert isinstance(e, ValidationError)
            assert len(e.messages) == 3, e.messages

    def test_union_with_absolute_path(self):
        class DummySchema(Schema):
            source = fields.Union([fields.URI(), fields.RelativeLocalPath()])  # we use this case in a lot of places

        s = DummySchema()
        data = dict(source="C:/repos")

        with pytest.raises(ValidationError):
            s.load(data)


class TestRelativeLocalPath:
    def test_simple_file_name(self):
        fname = "unet2d.py"
        expected = pathlib.Path(fname)
        actual = fields.RelativeLocalPath().deserialize(fname)
        assert isinstance(actual, pathlib.Path)
        assert actual == expected


class TestDependencies:
    class MinimalSchema(Schema):
        dep = fields.Dependencies()

    def test_url_roundtrip(self):
        manager = "conda"
        file = "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/environment.yaml"
        dep_input = dict(dep=f"{manager}:{file}")
        s = self.MinimalSchema()

        node = s.load(dep_input)
        dep = node["dep"]
        assert isinstance(dep, raw_nodes.Dependencies)
        assert dep.manager == manager
        assert isinstance(dep.file, raw_nodes.URI)
        assert str(dep.file) == file

        dep_serialized = s.dump(node)
        assert dep_serialized == dep_input
