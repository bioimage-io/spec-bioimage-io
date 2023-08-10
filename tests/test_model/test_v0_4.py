from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict
from unittest import TestCase

from pydantic import HttpUrl

from bioimageio.spec.generic.v0_2 import Author, CiteEntry, Maintainer
from bioimageio.spec.model.v0_4 import (
    InputTensor,
    LinkedModel,
    Model,
    ModelRdf,
    OnnxWeights,
    OutputTensor,
    Postprocessing,
    Preprocessing,
    ScaleLinearKwargs,
    Weights,
)
from bioimageio.spec.shared.types import RelativeFilePath
from bioimageio.spec.shared.validation import ValidationContext
from bioimageio.spec.utils import validate
from tests.unittest_utils import Invalid, TestBases, Valid


class TestModelRdf(TestBases.TestNode):
    default_node_class = ModelRdf
    sub_tests = [
        Valid(
            dict(rdf_source=__file__, sha256="s" * 64),
            expected_dump_raw=dict(rdf_source=__file__, sha256="s" * 64),
            expected_dump_python=dict(rdf_source=RelativeFilePath(__file__), sha256="s" * 64),
            context=ValidationContext(root=Path()),
        ),
        Valid(
            dict(uri="https://example.com", sha256="s" * 64),
            expected_dump_raw=dict(rdf_source="https://example.com/", sha256="s" * 64),
            expected_dump_python=dict(rdf_source=HttpUrl("https://example.com/"), sha256="s" * 64),
        ),
        Invalid(dict(id="lala", uri="https://example.com", sha256="s" * 64)),
        Invalid(dict(url="https://example.com", sha256="s" * 64)),
    ]


class TestLinkedModel(TestBases.TestNode):
    default_node_class = LinkedModel
    sub_tests = [
        Valid(dict(id="lala"), expected_dump_raw=dict(id="lala"), expected_dump_python=dict(id="lala")),
        Invalid(dict(id="lala", uri="https://example.com")),
        Invalid(dict(url="https://example.com")),
    ]


class TestOnnxEntry(TestBases.TestNode):
    default_node_class = OnnxWeights
    sub_tests = [
        Valid(
            dict(type="onnx", opset_version=8, source="https://example.com", sha256="s" * 64),
            expected_dump_raw=dict(opset_version=8, source="https://example.com/", sha256="s" * 64),
        ),
        Valid(
            dict(opset_version=8, source="https://example.com", sha256="s" * 64),
            expected_dump_raw=dict(opset_version=8, source="https://example.com/", sha256="s" * 64),
        ),
        Valid(
            dict(source="https://example.com", sha256="s" * 64),
            expected_dump_raw=dict(source="https://example.com/", sha256="s" * 64),
        ),
        Invalid(dict(opset_version=5, source="https://example.com", sha256="s" * 64)),
        Invalid(
            dict(source="https://example.com", sha256="s"),
        ),
    ]


VALID_PRE_AND_POSTPROCESSING = tuple(
    MappingProxyType(dict(name=name, kwargs=kwargs))
    for name, kwargs in [
        ("binarize", {"threshold": 0.5}),
        ("clip", {"min": 0.2, "max": 0.5}),
        ("scale_linear", {"gain": 2, "offset": 0.5, "axes": "xy"}),
        ("sigmoid", {}),
        ("zero_mean_unit_variance", {"mode": "fixed", "mean": 1, "std": 2, "axes": "xy"}),
        ("scale_range", {"mode": "per_sample", "axes": "xy"}),
        ("scale_range", {"mode": "per_sample", "axes": "xy", "min_percentile": 5, "max_percentile": 5}),
    ]
)
INVALID_PRE_AND_POSTPROCESSING = tuple(
    MappingProxyType(dict(name=name, kwargs=kwargs))
    for name, kwargs in [
        ("binarize", {"mode": "fixed", "threshold": 0.5}),
        ("clip", {"min": "min", "max": 0.5}),
        ("scale_linear", {"gain": 2, "offset": 0.5, "axes": "b"}),
        ("sigmoid", {"axes": "x"}),
        ("zero_mean_unit_variance", {"mode": "unknown", "mean": 1, "std": 2, "axes": "xy"}),
        ("scale_range", {"mode": "fixed", "axes": "xy"}),
        ("scale_range", {"mode": "per_sample", "axes": "xy", "min_percentile": 50, "max_percentile": 50}),
        ("scale_range", {"mode": "per_sample", "axes": "xy", "min": 0}),
    ]
)


class TestPreprocessing(TestBases.TestType):
    type_ = Preprocessing
    valid = VALID_PRE_AND_POSTPROCESSING
    invalid = INVALID_PRE_AND_POSTPROCESSING + (
        dict(
            name="scale_range",
            kwargs={"mode": "per_dataset", "axes": "xy", "reference_tensor": "some_input_tensor_name"},
        ),
    )


class TestPostprocessing(TestBases.TestType):
    type_ = Postprocessing
    valid = VALID_PRE_AND_POSTPROCESSING + (
        dict(name="scale_range", kwargs={"mode": "per_sample", "axes": "xy"}),
        dict(
            name="scale_range",
            kwargs={"mode": "per_dataset", "axes": "xy", "reference_tensor": "some_input_tensor_name"},
        ),
        dict(name="scale_mean_variance", kwargs={"mode": "per_sample", "reference_tensor": "some_tensor_name"}),
        dict(name="scale_mean_variance", kwargs={"mode": "per_dataset", "reference_tensor": "some_tensor_name"}),
    )
    invalid = INVALID_PRE_AND_POSTPROCESSING + (
        dict(name="scale_mean_variance", kwargs={"mode": "per_sample"}),
        dict(name="scale_mean_variance", kwargs={"mode": "per_dataset"}),
    )


class TestScaleLinearKwargs(TestBases.TestNode):
    default_node_class = ScaleLinearKwargs
    sub_tests = [
        Valid(dict(axes="xy", gain=2.0, offset=0.5)),
        Valid(dict(offset=2.0)),
        Valid(dict(gain=2.0)),
        Valid(dict(axes="xy", gain=[1.0, 2.0], offset=[0.5, 0.3])),
        Valid(dict(gain=2.0, offset=0.5)),
        Invalid(dict(), name="empty kwargs"),
        Invalid(dict(gain=1.0)),
        Invalid(dict(offset=0.0)),
    ]


class TestInputTensor(TestBases.TestNode):
    default_node_class = InputTensor
    sub_tests = [
        Valid(
            {
                "name": "input_1",
                "description": "Input 1",
                "data_type": "float32",
                "axes": "xyc",
                "shape": [128, 128, 3],
                "preprocessing": [
                    {
                        "name": "scale_range",
                        "kwargs": {"max_percentile": 99, "min_percentile": 5, "mode": "per_sample", "axes": "xy"},
                    }
                ],
            }
        ),
        Valid(
            {
                "name": "input_1",
                "description": "Input 1",
                "data_type": "float32",
                "axes": "xyc",
                "shape": [128, 128, 3],
            },
        ),
        Valid({"name": "tensor_1", "data_type": "float32", "axes": "xyc", "shape": [128, 128, 3]}),
    ]


class TestOutputTensor(TestBases.TestNode):
    default_node_class = OutputTensor
    sub_tests = [
        Valid(
            {
                "name": "output_1",
                "description": "Output 1",
                "data_type": "float32",
                "axes": "xyc",
                "shape": [128, 128, 3],
                "postprocessing": [
                    {
                        "name": "scale_range",
                        "kwargs": {"max_percentile": 99, "min_percentile": 5, "mode": "per_sample", "axes": "xy"},
                    }
                ],
            }
        ),
        Valid(
            {
                "name": "output_1",
                "description": "Output 1",
                "data_type": "float32",
                "axes": "xyc",
                "shape": [128, 128, 3],
            },
        ),
        Valid({"name": "tensor_1", "data_type": "float32", "axes": "xyc", "shape": [128, 128, 3]}),
    ]


class TestModel(TestCase):
    data: Dict[str, Any] = {}

    def setUp(self):
        self.data = Model(
            documentation=RelativeFilePath("docs.md"),
            license="MIT",
            git_repo="https://github.com/bioimage-io/python-bioimage-io",
            format_version="0.4.9",
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
                    data_type="float32",
                    axes="xyc",
                    shape=(128, 128, 3),
                ),
            ),
            outputs=(
                OutputTensor(
                    name="output_1",
                    description="Output 1",
                    data_type="float32",
                    axes="xyc",
                    shape=(128, 128, 3),
                ),
            ),
            name="Model",
            tags=(),
            weights=Weights(onnx=OnnxWeights(source=RelativeFilePath("weights.onnx"))),
            test_inputs=(RelativeFilePath("test_ipt.npy"),),
            test_outputs=(RelativeFilePath("test_out.npy"),),
            type="model",
        ).model_dump()

    def test_model_schema_accepts_run_mode(self):
        self.data.update({"run_mode": {"name": "special_run_mode", "kwargs": dict(marathon=True)}})
        summary = validate(self.data)
        self.assertEqual(summary["status"], "passed")

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

            summary = validate(self.data)
            self.assertEqual(summary["status"], "passed")


# def test_model_schema_raises_invalid_name(model_dict):
#     from bioimageio.spec.model.schema import Model

#     model_schema = Model()
#     model_dict["name"] = "invalid/name"
#     with pytest.raises(ValidationError):
#         model_schema.load(model_dict)


# def test_model_schema_raises_invalid_input_name(model_dict):
#     from bioimageio.spec.model.schema import Model

#     model_schema = Model()
#     model_dict["inputs"][0]["name"] = "invalid/name"
#     with pytest.raises(ValidationError):
#         model_schema.load(model_dict)


# def test_model_schema_raises_invalid_output_name(model_dict):
#     from bioimageio.spec.model.schema import Model

#     model_schema = Model()
#     model_dict["outputs"][0]["name"] = "invalid/name"
#     with pytest.raises(ValidationError):
#         model_schema.load(model_dict)


# def test_output_fixed_shape_too_small(model_dict):
#     from bioimageio.spec.model.schema import Model

#     model_dict["outputs"] = [
#         {
#             "name": "output_1",
#             "description": "Output 1",
#             "data_type": "float32",
#             "axes": "xyc",
#             "shape": [128, 128, 3],
#             "halo": [32, 128, 0],
#         }
#     ]

#     with pytest.raises(ValidationError) as e:
#         Model().load(model_dict)

#     assert e.value.messages == {
#         "_schema": ["Minimal shape [128 128   3] of output output_1 is too small for halo [32, 128, 0]."]
#     }


# def test_output_ref_shape_mismatch(model_dict):
#     from bioimageio.spec.model.schema import Model

#     model_dict["outputs"] = [
#         {
#             "name": "output_1",
#             "description": "Output 1",
#             "data_type": "float32",
#             "axes": "xyc",
#             "shape": {"reference_tensor": "input_1", "scale": [1, 2, 3, 4], "offset": [0, 0, 0, 0]},
#         }
#     ]

#     with pytest.raises(ValidationError) as e:
#         Model().load(model_dict)

#     assert e.value.messages == {
#         "_schema": [
#             "Referenced tensor input_1 with 3 dimensions does not match output tensor output_1 with 4 dimensions."
#         ]
#     }


# def test_output_ref_shape_too_small(model_dict):
#     from bioimageio.spec.model.schema import Model

#     model_dict["outputs"] = [
#         {
#             "name": "output_1",
#             "description": "Output 1",
#             "data_type": "float32",
#             "axes": "xyc",
#             "shape": {"reference_tensor": "input_1", "scale": [1, 2, 3], "offset": [0, 0, 0]},
#             "halo": [256, 128, 0],
#         }
#     ]

#     with pytest.raises(ValidationError) as e:
#         Model().load(model_dict)

#     assert e.value.messages == {
#         "_schema": ["Minimal shape [128. 256.   9.] of output output_1 is too small for halo [256, 128, 0]."]
#     }


# def test_model_has_parent_with_uri(model_dict):
#     from bioimageio.spec.model.schema import Model

#     model_dict["parent"] = dict(uri="https://doi.org/10.5281/zenodo.5744489")

#     valid_data = Model().load(model_dict)
#     assert isinstance(valid_data, raw_nodes_m04.Model)


# def test_model_has_parent_with_id(model_dict):
#     from bioimageio.spec.model.schema import Model

#     model_dict["parent"] = dict(id="10.5281/zenodo.5764892")

#     valid_data = Model().load(model_dict)
#     assert isinstance(valid_data, raw_nodes_m04.Model)


# def test_model_with_expanded_output(model_dict):
#     from bioimageio.spec.model.schema import Model

#     model_dict["outputs"] = [
#         {
#             "name": "output_1",
#             "description": "Output 1",
#             "data_type": "float32",
#             "axes": "xyzc",
#             "shape": dict(
#                 scale=[1, 1, None, 1],
#                 offset=[0, 0, 7, 0],
#                 reference_tensor="input_1",
#             ),
#         }
#     ]

#     model = Model().load(model_dict)
#     assert isinstance(model, raw_nodes_m04.Model)
#     out0_shape = model.outputs[0].shape
#     assert isinstance(out0_shape, raw_nodes_m04.ImplicitOutputShape)
#     assert out0_shape.scale == [1, 1, None, 1]
