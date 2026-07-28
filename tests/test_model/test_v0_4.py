from datetime import datetime, timezone
from typing import Any, Dict, Union

import pytest
from pydantic import ValidationError

from bioimageio.spec._description import validate_format
from bioimageio.spec._internal.root_url import RootHttpUrl
from bioimageio.spec._internal.validation_context import ValidationContext
from bioimageio.spec.model.v0_4 import (
    Author,
    CiteEntry,
    Datetime,
    InputTensorDescr,
    LinkedModel,
    Maintainer,
    ModelDescr,
    OnnxWeightsDescr,
    OutputTensorDescr,
    PostprocessingDescr,
    PreprocessingDescr,
    ScaleLinearKwargs,
    ScaleMeanVarianceDescr,
    ScaleRangeDescr,
    ScaleRangeKwargs,
    TensorName,
    WeightsDescr,
)
from tests.conftest import UNET2D_ROOT
from tests.utils import check_node, check_type, unset


def test_linked_model_lala():
    check_node(
        LinkedModel,
        {"id": "lala"},
        expected_dump_json={"id": "lala"},
        expected_dump_python={"id": "lala"},
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"url": "https://example.com"},
        {"id": "lala", "uri": "https://example.com"},
    ],
)
def test_linked_model_invalid(kwargs: Dict[str, Any]):
    check_node(LinkedModel, kwargs, is_invalid=True)


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        (
            {"source": UNET2D_ROOT / "weights.onnx", "sha256": "s" * 64},
            {"source": UNET2D_ROOT / "weights.onnx", "sha256": "s" * 64},
        ),
        (
            {
                "opset_version": 5,
                "source": UNET2D_ROOT / "weights.onnx",
                "sha256": "s" * 64,
            },
            ValidationError,
        ),
        (
            {"source": UNET2D_ROOT / "weights.onnx", "sha256": "s"},
            ValidationError,
        ),
    ],
)
def test_onnx_entry(kwargs: Dict[str, Any], expected: Union[Dict[str, Any], bool]):
    check_node(
        OnnxWeightsDescr,
        kwargs,
        expected_dump_json=expected if isinstance(expected, dict) else unset,
        is_invalid=expected is ValidationError,
        context=ValidationContext(perform_io_checks=False),
    )


VALID_PRE_AND_POSTPROCESSING = [
    {"name": "binarize", "kwargs": {"threshold": 0.5}},
    {"name": "clip", "kwargs": {"min": 0.2, "max": 0.5}},
    {"name": "scale_linear", "kwargs": {"gain": 2.0, "offset": 0.5, "axes": "xy"}},
    {"name": "sigmoid"},
    {
        "name": "zero_mean_unit_variance",
        "kwargs": {"mode": "fixed", "mean": 1.0, "std": 2.0, "axes": "xy"},
    },
    {"name": "scale_range", "kwargs": {"mode": "per_sample", "axes": "xy"}},
    {
        "name": "scale_range",
        "kwargs": {
            "mode": "per_sample",
            "axes": "xy",
            "min_percentile": 5,
            "max_percentile": 50,
        },
    },
]

INVALID_PRE_AND_POSTPROCESSING = [
    {"kwargs": {"threshold": 0.5}},
    {"name": "binarize", "kwargs": {"mode": "fixed", "threshold": 0.5}},
    {"name": "clip", "kwargs": {"min": "min", "max": 0.5}},
    {"name": "scale_linear", "kwargs": {"gain": 2.0, "offset": 0.5, "axes": "b"}},
    {"name": "sigmoid", "kwargs": {"axes": "x"}},
    {
        "name": "zero_mean_unit_variance",
        "kwargs": {"mode": "unknown", "mean": 1.0, "std": 2.0, "axes": "xy"},
    },
    {"name": "scale_range", "kwargs": {"mode": "fixed", "axes": "xy"}},
    {
        "name": "scale_range",
        "kwargs": {
            "mode": "per_sample",
            "axes": "xy",
            "min_percentile": 50,
            "max_percentile": 50,
        },
    },
    {"name": "scale_range", "kwargs": {"mode": "per_sample", "axes": "xy", "min": 0}},
]


@pytest.mark.parametrize(
    "kwargs",
    VALID_PRE_AND_POSTPROCESSING
    + [
        {
            "name": "scale_range",
            "kwargs": {
                "mode": "per_dataset",
                "axes": "xy",
                "reference_tensor": "some_input_tensor_name",
            },
        },
    ],
)
def test_preprocessing(kwargs: Dict[str, Any]):
    check_type(PreprocessingDescr, kwargs, expected_deserialized=kwargs)


@pytest.mark.parametrize("kwargs", INVALID_PRE_AND_POSTPROCESSING)
def test_invalid_preprocessing(kwargs: Dict[str, Any]):
    check_type(PreprocessingDescr, kwargs, is_invalid=True)


@pytest.mark.parametrize(
    "kwargs",
    VALID_PRE_AND_POSTPROCESSING
    + [
        {"name": "scale_range", "kwargs": {"mode": "per_sample", "axes": "xy"}},
        {
            "name": "scale_range",
            "kwargs": {
                "mode": "per_dataset",
                "axes": "xy",
                "reference_tensor": "some_input_tensor_name",
            },
        },
        {
            "name": "scale_mean_variance",
            "kwargs": {"mode": "per_sample", "reference_tensor": "some_tensor_name"},
        },
        {
            "name": "scale_mean_variance",
            "kwargs": {"mode": "per_dataset", "reference_tensor": "some_tensor_name"},
        },
    ],
)
def test_postprocessing(kwargs: Dict[str, Any]):
    check_type(PostprocessingDescr, kwargs, expected_deserialized=kwargs)


@pytest.mark.parametrize(
    "node,expected",
    [
        (
            ScaleRangeDescr(kwargs=ScaleRangeKwargs(mode="per_sample", axes="xy")),
            {"name": "scale_range", "kwargs": {"mode": "per_sample", "axes": "xy"}},
        ),
        (
            ScaleMeanVarianceDescr(
                kwargs={"mode": "per_dataset", "reference_tensor": "some_tensor_name"}  # type: ignore
            ),
            {
                "name": "scale_mean_variance",
                "kwargs": {
                    "mode": "per_dataset",
                    "reference_tensor": "some_tensor_name",
                },
            },
        ),
    ],
)
def test_postprocessing_node_input(node: Any, expected: Dict[str, Any]):
    check_type(PostprocessingDescr, node, expected_deserialized=expected)


@pytest.mark.parametrize(
    "kwargs",
    INVALID_PRE_AND_POSTPROCESSING
    + [
        {"name": "scale_mean_variance", "kwargs": {"mode": "per_sample"}},
        {"name": "scale_mean_variance", "kwargs": {"mode": "per_dataset"}},
    ],
)
def test_invalid_postprocessing(kwargs: Dict[str, Any]):
    check_type(PostprocessingDescr, kwargs, is_invalid=True)


@pytest.mark.parametrize(
    "kwargs,valid",
    [
        ({"axes": "xy", "gain": 2.0, "offset": 0.5}, True),
        ({"offset": 2.0}, True),
        ({"gain": 2.0}, True),
        ({"axes": "xy", "gain": [1.0, 2.0], "offset": [0.5, 0.3]}, True),
        ({"gain": 2.0, "offset": 0.5}, True),
        ({}, False),
        ({"gain": 1.0}, False),
        ({"offset": 0.0}, False),
    ],
)
def test_scale_linear_kwargs(kwargs: Dict[str, Any], valid: bool):
    check_node(ScaleLinearKwargs, kwargs, is_invalid=not valid)


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "name": "input_1",
            "description": "Input 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": [128, 128, 3],
            "preprocessing": [
                {
                    "name": "scale_range",
                    "kwargs": {
                        "max_percentile": 99,
                        "min_percentile": 5,
                        "mode": "per_sample",
                        "axes": "xy",
                    },
                }
            ],
        },
        {
            "name": "input_1",
            "description": "Input 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": [128, 128, 3],
        },
        {
            "name": "tensor_1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": [128, 128, 3],
        },
    ],
)
def test_input_tensor(kwargs: Dict[str, Any]):
    check_node(InputTensorDescr, kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "name": "output_1",
            "description": "Output 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": [128, 128, 3],
            "postprocessing": [
                {
                    "name": "scale_range",
                    "kwargs": {
                        "max_percentile": 99,
                        "min_percentile": 5,
                        "mode": "per_sample",
                        "axes": "xy",
                    },
                }
            ],
        },
        {
            "name": "output_1",
            "description": "Output 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": [128, 128, 3],
        },
        {
            "name": "tensor_1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": [128, 128, 3],
        },
    ],
)
def test_output_tensor(kwargs: Dict[str, Any]):
    check_node(OutputTensorDescr, kwargs)


@pytest.fixture
def model_data():
    with ValidationContext(perform_io_checks=False):
        return ModelDescr(
            documentation=UNET2D_ROOT / "README.md",
            license="MIT",
            git_repo="https://github.com/bioimage-io/core-bioimage-io-python",
            description="description",
            authors=[
                Author(name="Author 1", affiliation="Affiliation 1"),
                Author(name="Author 2"),
            ],
            maintainers=[
                Maintainer(
                    name="Maintainer 1",
                    affiliation="Affiliation 1",
                    github_user="fynnbe",
                ),
                Maintainer(github_user="constantinpape"),
            ],
            timestamp=Datetime(datetime.now(timezone.utc)),
            cite=[CiteEntry(text="Paper title", url="https://example.com/")],
            inputs=[
                InputTensorDescr(
                    name=TensorName("input_1"),
                    description="Input 1",
                    data_type="float32",
                    axes="xyc",
                    shape=[128, 128, 3],
                ),
            ],
            outputs=[
                OutputTensorDescr(
                    name=TensorName("output_1"),
                    description="Output 1",
                    data_type="float32",
                    axes="xyc",
                    shape=[128, 128, 3],
                ),
            ],
            name="Model",
            tags=[],
            weights=WeightsDescr(
                onnx=OnnxWeightsDescr(source=UNET2D_ROOT / "weights.onnx")
            ),
            test_inputs=[UNET2D_ROOT / "test_input.npy"],
            test_outputs=[UNET2D_ROOT / "test_output.npy"],
            type="model",
        ).model_dump(mode="json")


@pytest.mark.parametrize(
    "update",
    [
        {"run_mode": {"name": "special_run_mode", "kwargs": {"marathon": True}}},
        {"name": "µ-unicode-model!"},
        {"weights": {"torchscript": {"source": "local_weights"}}},
        {"weights": {"keras_hdf5": {"source": "local_weights"}}},
        {"weights": {"tensorflow_js": {"source": "local_weights"}}},
        {"weights": {"tensorflow_saved_model_bundle": {"source": "local_weights"}}},
        {"weights": {"onnx": {"source": "local_weights"}}},
        {
            "weights": {
                "pytorch_state_dict": {
                    "source": "local_weights",
                    "architecture": "file.py:Model",
                    "architecture_sha256": "0" * 64,
                }
            }
        },
    ],
)
def test_model(model_data: Dict[str, Any], update: Dict[str, Any]):
    model_data.update(update)
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert summary.status == "valid-format", summary.display()


def test_warn_long_name(model_data: Dict[str, Any]):
    model_data["name"] = (
        "veeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeery loooooooooooooooong name"
    )
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert summary.status == "valid-format", summary.display()
    assert summary.details[1].warnings[0].loc == ("name",), summary.display()
    assert summary.details[1].warnings[0].msg == "Name longer than 64 characters."


def test_model_schema_raises_invalid_input_name(model_data: Dict[str, Any]):
    model_data["inputs"][0]["name"] = "invalid/name"
    summary = validate_format(
        model_data,
        context=ValidationContext(
            root=RootHttpUrl("http://example.com/"), perform_io_checks=False
        ),
    )
    assert summary.status == "failed", summary.display()


def test_output_fixed_shape_too_small(model_data: Dict[str, Any]):
    model_data["outputs"] = [
        {
            "name": "output_1",
            "description": "Output 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": [128, 128, 3],
            "halo": [32, 128, 0],
        }
    ]

    summary = validate_format(
        model_data,
        context=ValidationContext(
            root=RootHttpUrl("http://example.com/"), perform_io_checks=False
        ),
    )
    assert summary.status == "failed", summary.display()


def test_output_ref_shape_mismatch(model_data: Dict[str, Any]):
    model_data["outputs"] = [
        {
            "name": "output_1",
            "description": "Output 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": {
                "reference_tensor": "input_1",
                "scale": [1, 2, 3, 4],
                "offset": [0, 0, 0, 0],
            },
        }
    ]

    summary = validate_format(
        model_data,
        context=ValidationContext(
            root=RootHttpUrl("http://example.com/"), perform_io_checks=False
        ),
    )
    assert summary.status == "failed", summary.display()


def test_output_ref_shape_too_small(model_data: Dict[str, Any]):
    model_data["outputs"] = [
        {
            "name": "output_1",
            "description": "Output 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": {
                "reference_tensor": "input_1",
                "scale": [1, 2, 3],
                "offset": [0, 0, 0],
            },
            "halo": [256, 128, 0],
        }
    ]
    summary = validate_format(
        model_data,
        context=ValidationContext(
            root=RootHttpUrl("http://example.com/"), perform_io_checks=False
        ),
    )
    assert summary.status == "failed", summary.display()


def test_model_has_parent_with_id(model_data: Dict[str, Any]):
    model_data["parent"] = {"id": "10.5281/zenodo.5764892"}
    summary = validate_format(
        model_data,
        context=ValidationContext(
            root=RootHttpUrl("http://example.com/"), perform_io_checks=False
        ),
    )
    assert summary.status == "valid-format", summary.display()


def test_model_with_expanded_output(model_data: Dict[str, Any]):
    model_data["outputs"] = [
        {
            "name": "output_1",
            "description": "Output 1",
            "data_type": "float32",
            "axes": "xyzc",
            "shape": {
                "scale": [1, 1, None, 1],
                "offset": [0, 0, 7, 0],
                "reference_tensor": "input_1",
            },
        }
    ]

    summary = validate_format(
        model_data,
        context=ValidationContext(
            root=RootHttpUrl("http://example.com/"), perform_io_checks=False
        ),
    )
    assert summary.status == "valid-format", summary.display()


def test_model_rdf_is_valid_general_rdf(model_data: Dict[str, Any]):
    model_data["type"] = "model_as_generic"
    model_data["format_version"] = "0.2.4"
    summary = validate_format(
        model_data,
        context=ValidationContext(
            root=RootHttpUrl("http://example.com/"), perform_io_checks=False
        ),
    )
    assert summary.status == "valid-format", summary.display()


def test_model_does_not_accept_unknown_fields(model_data: Dict[str, Any]):
    model_data["unknown_additional_field"] = "shouldn't be here"
    summary = validate_format(
        model_data,
        context=ValidationContext(
            root=RootHttpUrl("http://example.com/"), perform_io_checks=False
        ),
    )
    assert summary.status == "failed", summary.display()
