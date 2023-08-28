from datetime import datetime
from typing import Any, Dict, Union

import pytest
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
from tests.utils import check_node


def test_model_rdf_file_ref():
    check_node(
        ModelRdf,
        dict(rdf_source=__file__, sha256="s" * 64),
        expected_dump_json=dict(rdf_source=__file__, sha256="s" * 64),
        expected_dump_python=dict(rdf_source=RelativeFilePath(__file__), sha256="s" * 64),
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(uri="https://example.com", sha256="s" * 64),
        dict(id="lala", uri="https://example.com", sha256="s" * 64),
        dict(url="https://example.com", sha256="s" * 64),
    ],
)
def test_model_rdf_invalid(kwargs: Dict[str, Any]):
    check_node(ModelRdf, kwargs, is_invalid=True)


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            name="t1",
            axes=[{"type": "channel", "channel_names": ["a", "b"]}],
            test_tensor="https://example.com/test.npy",
            data={"values": ["cat", "dog", "parrot"]},
        ),
        dict(
            name="t2",
            axes=[{"type": "channel", "channel_names": ["a", "b"]}],
            test_tensor="https://example.com/test.npy",
            data=[
                {"values": ["cat", "dog", "parrot"]},
                {"values": ["mouse", "zebra", "elephant"]},
            ],
        ),
        dict(
            name="t3",
            axes=[{"type": "channel", "channel_names": ["a", "b"]}],
            test_tensor="https://example.com/test.npy",
            data=[
                {"values": [1, 2, 3]},
                {"type": "uint8"},
            ],
        ),
        pytest.param(
            dict(
                name="t4",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["mouse", "zebra", "elephant"]},
                    {"type": "uint8"},
                ],
            ),
            id="string values and uint data type",
        ),
        pytest.param(
            dict(
                name="t4",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["mouse", "zebra", "elephant"]},
                    {"type": "int8"},
                ],
            ),
            id="string values and int data type",
        ),
    ],
)
def test_tensor_base(kwargs: Dict[str, Any]):
    check_node(TensorBase, kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param(
            dict(
                name="t5",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["cat", "dog", "parrot"]},
                    {"values": [1.1, 2.2, 3.3]},
                ],
            ),
            id="str and float values",
        ),
        pytest.param(
            dict(
                name="t6",
                axes=[{"type": "channel", "channel_names": ["a", "b", "c"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["cat", "dog", "parrot"]},
                    {"values": ["mouse", "zebra", "elephant"]},
                ],
            ),
            id="channel mismatch",
        ),
    ],
)
def test_tensor_base_invalid(kwargs: Dict[str, Any]):
    check_node(TensorBase, kwargs, is_invalid=True)


@pytest.mark.parametrize(
    "kwargs",
    [
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
    ],
)
def test_input_tensor(kwargs: Dict[str, Any]):
    check_node(InputTensor, kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [{}, {"type": "batch"}],
)
def test_batch_axis(kwargs: Dict[str, Any]):
    check_node(
        BatchAxis, kwargs, expected_dump_python={"type": "batch", "name": "batch", "description": "", "size": None}
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"type": "space", "name": "x", "size": 10},
        SpaceInputAxis(name="x", size=10),
        {"type": "batch"},
    ],
)
def test_input_axis(kwargs: Union[Dict[str, Any], SpaceInputAxis]):
    check_node(InputAxis, kwargs)


@pytest.fixture
def model_data():
    return Model(
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


@pytest.mark.parametrize(
    "update",
    [
        pytest.param(dict(name="µ-unicode-model/name!"), id="unicode name"),
        dict(run_mode={"name": "special_run_mode", "kwargs": dict(marathon=True)}),
        dict(weights={"torchscript": {"source": "local_weights"}}),
        dict(weights={"keras_hdf5": {"source": "local_weights"}}),
        dict(weights={"tensorflow_js": {"source": "local_weights"}}),
        dict(weights={"tensorflow_saved_model_bundle": {"source": "local_weights"}}),
        dict(weights={"onnx": {"source": "local_weights"}}),
        dict(
            weights={
                "pytorch_state_dict": {"source": "local_weights"},
                "architecture": {
                    "callable": "file.py:Model",
                    "sha256": "0" * 64,  # dummy sha256
                },
            }
        ),
    ],
)
def test_model(model_data: Dict[str, Any], update: Dict[str, Any]):
    model_data.update(update)
    summary = validate_format(model_data, context=ValidationContext(root=HttpUrl("https://example.com/")))
    assert summary.status == "passed", summary.format()


def test_warn_long_name(model_data: Dict[str, Any]):
    model_data["name"] = "veeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeery loooooooooooooooong name"
    summary = validate_format(
        model_data, context=ValidationContext(root=HttpUrl("https://example.com/"), warning_level=INFO)
    )
    assert summary.status == "passed", summary.format()
    assert summary.warnings[0].loc == ("name",), summary.format()
    assert summary.warnings[0].msg in [
        "'veeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeery loooooooooooooooong name' incompatible with "
        f"{typing_module}.Annotated[typing.Any, Len(min_length=5, max_length=64)]"
        for typing_module in ("typing", "typing_extensions")
    ], summary.format()


def test_model_schema_raises_invalid_input_name(model_data: Dict[str, Any]):
    model_data["inputs"][0]["name"] = "invalid/name"
    summary = validate_format(model_data)
    assert summary.status == "failed", summary.format()


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

    summary = validate_format(model_data)
    assert summary.status == "failed", summary.format()


def test_output_ref_shape_mismatch(model_data: Dict[str, Any]):
    model_data["outputs"] = [
        {
            "name": "output_1",
            "description": "Output 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": {"reference_tensor": "input_1", "scale": [1, 2, 3, 4], "offset": [0, 0, 0, 0]},
        }
    ]

    summary = validate_format(model_data)
    assert summary.status == "failed", summary.format()


def test_output_ref_shape_too_small(model_data: Dict[str, Any]):
    model_data["outputs"] = [
        {
            "name": "output_1",
            "description": "Output 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": {"reference_tensor": "input_1", "scale": [1, 2, 3], "offset": [0, 0, 0]},
            "halo": [256, 128, 0],
        }
    ]
    summary = validate_format(model_data)
    assert summary.status == "failed", summary.format()


def test_model_has_parent_with_uri(model_data: Dict[str, Any]):
    uri = "https://doi.org/10.5281/zenodo.5744489"
    model_data["parent"] = dict(uri=uri, sha256="s" * 64)

    model, summary = load_description(model_data, context=ValidationContext(root=HttpUrl("https://example.com/")))
    assert summary.status == "passed", summary.format()

    assert isinstance(model, Model)
    assert isinstance(model.parent, ModelRdf)
    assert str(model.parent.rdf_source) == uri


def test_model_has_parent_with_id(model_data: Dict[str, Any]):
    model_data["parent"] = dict(id="10.5281/zenodo.5764892")
    summary = validate_format(model_data, context=ValidationContext(root=HttpUrl("https://example.com/")))
    assert summary.status == "passed", summary.format()


def test_model_with_expanded_output(model_data: Dict[str, Any]):
    model_data["outputs"] = [
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

    summary = validate_format(model_data, context=ValidationContext(root=HttpUrl("https://example.com/")))
    assert summary.status == "passed", summary.format()


def test_model_rdf_is_valid_general_rdf(model_data: Dict[str, Any]):
    model_data["type"] = "model_as_generic"
    summary = validate_format(model_data, context=ValidationContext(root=HttpUrl("https://example.com/")))
    assert summary.status == "passed", summary.format()


def test_model_does_not_accept_unknown_fields(model_data: Dict[str, Any]):
    model_data["unknown_additional_field"] = "shouldn't be here"
    summary = validate_format(model_data, context=ValidationContext(root=HttpUrl("https://example.com/")))
    assert summary.status == "failed", summary.format()
