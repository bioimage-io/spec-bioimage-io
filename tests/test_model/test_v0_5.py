from datetime import datetime
from typing import Any, Dict
from unittest import TestCase

from pydantic import HttpUrl

from bioimageio.spec._internal.constants import INFO
from bioimageio.spec.description import load_description, validate_format
from bioimageio.spec.generic.v0_2 import Author, Maintainer
from bioimageio.spec.model.v0_5 import (
    BatchAxis,
    ChannelAxis,
    CiteEntry,
    InputAxis,
    InputTensor,
    IntervalOrRatioData,
    Model,
    ModelRdf,
    OnnxWeights,
    OutputTensor,
    SpaceInputAxis,
    SpaceOutputAxis,
    TensorBase,
    Weights,
)
from bioimageio.spec.types import RelativeFilePath, ValidationContext
from tests.unittest_utils import Invalid, TestBases, Valid


class TestModelRdf(TestBases.TestNode):
    default_node_class = ModelRdf
    sub_tests = [
        Valid(
            dict(rdf_source=__file__, sha256="s" * 64),
            expected_dump_json=dict(rdf_source=__file__, sha256="s" * 64),
            expected_dump_python=dict(rdf_source=RelativeFilePath(__file__), sha256="s" * 64),
        ),
        Invalid(dict(uri="https://example.com", sha256="s" * 64)),
        Invalid(dict(id="lala", uri="https://example.com", sha256="s" * 64)),
        Invalid(dict(url="https://example.com", sha256="s" * 64)),
    ]


class TestTensorBase(TestBases.TestNode):
    default_node_class = TensorBase
    sub_tests = [
        Valid(
            dict(
                name="t1",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data={"values": ["cat", "dog", "parrot"]},
            )
        ),
        Valid(
            dict(
                name="t2",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["cat", "dog", "parrot"]},
                    {"values": ["mouse", "zebra", "elephant"]},
                ],
            )
        ),
        Valid(
            dict(
                name="t3",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": [1, 2, 3]},
                    {"type": "uint8"},
                ],
            )
        ),
        Valid(
            dict(
                name="t4",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["mouse", "zebra", "elephant"]},
                    {"type": "uint8"},
                ],
            ),
            name="string values and uint data type",
        ),
        Invalid(
            dict(
                name="t4",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["mouse", "zebra", "elephant"]},
                    {"type": "int8"},
                ],
            ),
            name="string values and int data type",
        ),
        Invalid(
            dict(
                name="t5",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["cat", "dog", "parrot"]},
                    {"values": [1.1, 2.2, 3.3]},
                ],
            ),
            name="str and float values",
        ),
        Invalid(
            dict(
                name="t6",
                axes=[{"type": "channel", "channel_names": ["a", "b", "c"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["cat", "dog", "parrot"]},
                    {"values": ["mouse", "zebra", "elephant"]},
                ],
            ),
            name="channel mismatch",
        ),
    ]


class TestInputTensor(TestBases.TestNode):
    default_node_class = InputTensor
    sub_tests = [
        Valid(
            {
                "name": "input_1",
                "description": "Input 1",
                "data": {"type": "float32"},
                "axes": [
                    dict(type="space", name="x", size=10),
                    dict(type="space", name="y", size=11),
                    dict(type="channel", channel_names=tuple("abc")),
                ],
                "preprocessing": [
                    {
                        "name": "scale_range",
                        "kwargs": {"max_percentile": 99, "min_percentile": 5, "mode": "per_sample", "axes": ("x", "y")},
                    }
                ],
                "test_tensor": "https://example.com/test.npy",
            }
        ),
    ]


class TestBatchAxis(TestBases.TestNode):
    default_node_class = BatchAxis
    sub_tests = [
        Valid({}, expected_dump_python={"type": "batch"}),
        Valid({"type": "batch"}, expected_dump_python={"type": "batch"}),
    ]


class TestSpaceInputAxis(TestBases.TestNode):
    default_node_class = SpaceInputAxis
    sub_tests = [
        Valid({"name": "x", "size": 10}, expected_dump_python={"type": "space", "name": "x", "size": 10}),
        Valid(
            {"type": "space", "name": "x", "size": 10}, expected_dump_python={"type": "space", "name": "x", "size": 10}
        ),
    ]


class TestInputAxis(TestBases.TestType):
    type_ = InputAxis
    valid = [{"type": "space", "name": "x", "size": 10}, SpaceInputAxis(name="x", size=10)]


class TestModel(TestCase):
    data: Dict[str, Any] = {}

    def setUp(self):
        self.data = Model(
            documentation=RelativeFilePath("docs.md"),
            license="MIT",
            git_repo="https://github.com/bioimage-io/python-bioimage-io",
            format_version="0.5.0",
            description="description",
            authors=(
                Author(name="Author 1", affiliation="Affiliation 1"),
                Author(name="Author 2"),
            ),
            maintainers=(
                Maintainer(name="Maintainer 1", affiliation="Affiliation 1", github_user="githubuser1"),
                Maintainer(github_user="githubuser2"),
            ),
            timestamp=datetime.now(),
            cite=(CiteEntry(text="Paper title", url="https://example.com/"),),
            inputs=(
                InputTensor(
                    name="input_1",
                    description="Input 1",
                    data=IntervalOrRatioData(type="float32"),
                    axes=(SpaceInputAxis(name="x", size=10), SpaceInputAxis(name="y", size=20), ChannelAxis(size=3)),
                    test_tensor=RelativeFilePath("test_ipt.npy"),
                ),
            ),
            outputs=(
                OutputTensor(
                    name="output_1",
                    description="Output 1",
                    axes=(SpaceOutputAxis(name="x", size=15), SpaceOutputAxis(name="y", size=25), ChannelAxis(size=6)),
                    test_tensor=RelativeFilePath("test_out.npy"),
                ),
            ),
            name="Model",
            tags=(),
            weights=Weights(onnx=OnnxWeights(source=RelativeFilePath("weights.onnx"))),
            type="model",
        ).model_dump()

    def test_model_schema_accepts_run_mode(self):
        self.data.update({"run_mode": {"name": "special_run_mode", "kwargs": dict(marathon=True)}})
        summary = validate_format(self.data, context=ValidationContext(root=HttpUrl("https://example.com/")))
        self.assertEqual(summary.status, "passed", summary.format())

    def test_model_name(self):
        self.data.update(dict(name="µ-unicode-model/name!"))
        summary = validate_format(self.data, context=ValidationContext(root=HttpUrl("https://example.com/")))
        self.assertEqual(summary.status, "passed", summary.format())

    def test_model_schema_accepts_valid_weight_formats(self):
        for format in [
            "torchscript",
            "keras_hdf5",
            "tensorflow_js",
            "tensorflow_saved_model_bundle",
            "onnx",
            "pytorch_state_dict",
        ]:
            with self.subTest(format):
                self.data.update({"weights": {format: {"source": "local_weights"}}})
                if format == "pytorch_state_dict":
                    self.data["weights"][format]["architecture"] = "file.py:Model"
                    self.data["weights"][format]["architecture_sha256"] = "0" * 64  # dummy sha256

                summary = validate_format(self.data, context=ValidationContext(root=HttpUrl("https://example.com/")))
                self.assertEqual(summary.status, "passed", summary.format())

    def test_warn_long_name(self):
        self.data["name"] = "veeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeery loooooooooooooooong name"
        summary = validate_format(
            self.data, context=ValidationContext(root=HttpUrl("https://example.com/"), warning_level=INFO)
        )
        self.assertEqual(summary.status, "passed", summary.format())
        self.assertEqual(summary.warnings[0].loc, ("name",), summary.format())
        self.assertIn(
            summary.warnings[0].msg,
            [
                "'veeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeery loooooooooooooooong name' incompatible with "
                f"{typing_module}.Annotated[typing.Any, Len(min_length=5, max_length=64)]"
                for typing_module in ("typing", "typing_extensions")
            ],
            summary.format(),
        )

    def test_model_schema_raises_invalid_input_name(self):
        self.data["inputs"][0]["name"] = "invalid/name"
        summary = validate_format(self.data)
        self.assertEqual(summary.status, "failed", summary.format())

    def test_output_fixed_shape_too_small(self):
        self.data["outputs"] = [
            {
                "name": "output_1",
                "description": "Output 1",
                "data_type": "float32",
                "axes": "xyc",
                "shape": [128, 128, 3],
                "halo": [32, 128, 0],
            }
        ]

        summary = validate_format(self.data)
        self.assertEqual(summary.status, "failed", summary.format())

    def test_output_ref_shape_mismatch(self):
        self.data["outputs"] = [
            {
                "name": "output_1",
                "description": "Output 1",
                "data_type": "float32",
                "axes": "xyc",
                "shape": {"reference_tensor": "input_1", "scale": [1, 2, 3, 4], "offset": [0, 0, 0, 0]},
            }
        ]

        summary = validate_format(self.data)
        self.assertEqual(summary.status, "failed", summary.format())

    def test_output_ref_shape_too_small(self):
        self.data["outputs"] = [
            {
                "name": "output_1",
                "description": "Output 1",
                "data_type": "float32",
                "axes": "xyc",
                "shape": {"reference_tensor": "input_1", "scale": [1, 2, 3], "offset": [0, 0, 0]},
                "halo": [256, 128, 0],
            }
        ]
        summary = validate_format(self.data)
        self.assertEqual(summary.status, "failed", summary.format())

    def test_model_has_parent_with_uri(self):
        uri = "https://doi.org/10.5281/zenodo.5744489"
        self.data["parent"] = dict(uri=uri, sha256="s" * 64)

        model, summary = load_description(self.data, context=ValidationContext(root=HttpUrl("https://example.com/")))
        self.assertEqual(summary.status, "passed", summary.format())

        self.assertIsInstance(model, Model)
        self.assertEqual(str(model.parent.rdf_source), uri)  # type: ignore

    def test_model_has_parent_with_id(self):
        self.data["parent"] = dict(id="10.5281/zenodo.5764892")
        summary = validate_format(self.data, context=ValidationContext(root=HttpUrl("https://example.com/")))
        self.assertEqual(summary.status, "passed", summary.format())

    def test_model_with_expanded_output(self):
        self.data["outputs"] = [
            {
                "name": "output_1",
                "description": "Output 1",
                "data_type": "float32",
                "axes": "xyzc",
                "shape": dict(
                    scale=[1, 1, None, 1],
                    offset=[0, 0, 7, 0],
                    reference_tensor="input_1",
                ),
            }
        ]

        summary = validate_format(self.data, context=ValidationContext(root=HttpUrl("https://example.com/")))
        self.assertEqual(summary.status, "passed", summary.format())

    def test_model_rdf_is_valid_general_rdf(self):
        self.data["type"] = "model_as_generic"
        summary = validate_format(self.data, context=ValidationContext(root=HttpUrl("https://example.com/")))
        self.assertEqual(summary.status, "passed", summary.format())

    def test_model_does_not_accept_unknown_fields(self):
        self.data["unknown_additional_field"] = "shouldn't be here"
        summary = validate_format(self.data, context=ValidationContext(root=HttpUrl("https://example.com/")))
        self.assertEqual(summary.status, "failed", summary.format())
