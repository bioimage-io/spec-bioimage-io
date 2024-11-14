from copy import deepcopy
from datetime import datetime
from types import MappingProxyType
from typing import Any, Dict, Mapping, Union

import pytest
from pydantic import RootModel, ValidationError

from bioimageio.spec import build_description, validate_format
from bioimageio.spec._internal.io import FileDescr
from bioimageio.spec._internal.license_id import LicenseId
from bioimageio.spec._internal.url import HttpUrl
from bioimageio.spec._internal.validation_context import ValidationContext
from bioimageio.spec.model.v0_5 import (
    Author,
    AxisId,
    BatchAxis,
    ChannelAxis,
    CiteEntry,
    Datetime,
    Identifier,
    InputAxis,
    InputTensorDescr,
    IntervalOrRatioDataDescr,
    Maintainer,
    ModelDescr,
    OnnxWeightsDescr,
    OutputTensorDescr,
    ParameterizedSize,
    SizeReference,
    SpaceInputAxis,
    SpaceOutputAxis,
    TensorDescrBase,
    TensorId,
    WeightsDescr,
)
from tests.conftest import UNET2D_ROOT
from tests.utils import check_node, check_type


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            id="t0",
            test_tensor={"source": UNET2D_ROOT / "test_input.npy"},
            data={"values": ["cat", "dog", "parrot"]},
            axes=[{"type": "channel", "channel_names": ["animal"]}],
        ),
        dict(
            id="t1",
            test_tensor={"source": UNET2D_ROOT / "test_input.npy"},
            data=[
                {"values": ["cat", "dog", "parrot"]},
                {"values": ["mouse", "zebra", "elephant"]},
            ],
            axes=[{"type": "channel", "channel_names": ["animal", "other_animal"]}],
        ),
        dict(
            id="t2",
            test_tensor={"source": UNET2D_ROOT / "test_input.npy"},
            data=[
                {"values": [1, 2, 3]},
                {"type": "uint8"},
            ],
            axes=[
                {"type": "channel", "channel_names": ["animal_code", "animal_count"]}
            ],
        ),
        pytest.param(
            dict(
                id="t3",
                test_tensor={"source": UNET2D_ROOT / "test_input.npy"},
                data=[
                    {"values": ["mouse", "zebra", "elephant"]},
                    {"type": "uint8"},
                ],
                axes=[{"type": "channel", "channel_names": ["animal_code", "count"]}],
            ),
            id="string values and uint data type",
        ),
    ],
)
def test_tensor_base(kwargs: Dict[str, Any]):
    check_node(
        TensorDescrBase, kwargs, context=ValidationContext(perform_io_checks=False)
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param(
            dict(
                id="t5",
                test_tensor={"source": UNET2D_ROOT / "test_input.npy"},
                data=[
                    {"values": ["cat", "dog", "parrot"]},
                    {"values": [1.1, 2.2, 3.3]},
                ],
            ),
            id="str and float values",
        ),
        pytest.param(
            dict(
                id="t7",
                test_tensor={"source": UNET2D_ROOT / "test.npy"},
                data=[
                    {"values": ["mouse", "zebra", "elephant"]},
                    {"type": "int8"},
                ],
            ),
            id="string values and int data type",
        ),
    ],
)
def test_tensor_base_invalid(kwargs: Dict[str, Any]):
    check_node(
        TensorDescrBase,
        kwargs,
        is_invalid=True,
        context=ValidationContext(perform_io_checks=False),
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "id": "input_1",
            "description": "Input 1",
            "data": {"type": "float32"},
            "axes": [
                dict(type="space", id="x", size=10),
                dict(type="space", id="y", size=11),
                dict(type="channel", channel_names=tuple("abc")),
            ],
            "preprocessing": [
                {
                    "id": "scale_range",
                    "kwargs": {
                        "max_percentile": 99,
                        "min_percentile": 5,
                        "axes": ("x", "y"),
                    },
                }
            ],
            "test_tensor": {"source": UNET2D_ROOT / "test_input.npy"},
        },
    ],
)
def test_input_tensor(kwargs: Dict[str, Any]):
    check_node(
        InputTensorDescr, kwargs, context=ValidationContext(perform_io_checks=False)
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param(
            dict(
                id="input_2",
                test_tensor={"source": UNET2D_ROOT / "test.npy"},
                data=[
                    {"values": ["cat", "dog", "parrot"]},
                    {"values": ["mouse", "zebra", "elephant"]},
                ],
                axes=[{"type": "channel", "channel_names": ["a", "b", "c"]}],
            ),
            id="channel mismatch",
        ),
    ],
)
def test_input_tensor_invalid(kwargs: Dict[str, Any]):
    check_node(
        InputTensorDescr,
        kwargs,
        is_invalid=True,
        context=ValidationContext(perform_io_checks=False),
    )


def test_input_tensor_error_count(model_data: Dict[str, Any]):
    """this test checks that the discrminated union for `InputAxis` does its
    thing and we don't get errors for all options"""
    from bioimageio.spec import build_description

    model_data["inputs"][0]["axes"][0]["id"] = 42
    invalid = build_description(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert (
        len(invalid.validation_summary.details[1].errors) == 1
    ), invalid.validation_summary.details[1].errors


@pytest.mark.parametrize(
    "kwargs",
    [{}, {"type": "batch"}],
)
def test_batch_axis(kwargs: Dict[str, Any]):
    check_node(
        BatchAxis,
        kwargs,
        expected_dump_python={
            "type": "batch",
            "name": "batch",
            "description": "",
            "size": None,
        },
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"type": "space", "id": "x", "size": 10},
        SpaceInputAxis(id=AxisId("x"), size=10),
        {"type": "batch"},
    ],
)
def test_input_axis(kwargs: Union[Dict[str, Any], SpaceInputAxis]):
    check_type(InputAxis, kwargs)


@pytest.fixture(scope="module")
def model():
    """reuse model object to avoid expensive model validation,
    use only when not manipulating the model!"""
    with ValidationContext(perform_io_checks=False):
        return ModelDescr(
            documentation=UNET2D_ROOT / "README.md",
            license=LicenseId("MIT"),
            git_repo=HttpUrl("https://github.com/bioimage-io/core-bioimage-io-python"),
            format_version="0.5.3",
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
                Maintainer(github_user="githubuser2"),
            ],
            timestamp=Datetime(datetime.now()),
            cite=[CiteEntry(text="Paper title", url=HttpUrl("https://example.com/"))],
            inputs=[
                InputTensorDescr(
                    id=TensorId("input_1"),
                    description="Input 1",
                    data=IntervalOrRatioDataDescr(type="float32"),
                    axes=[
                        BatchAxis(),
                        ChannelAxis(channel_names=[Identifier("intensity")]),
                        SpaceInputAxis(
                            id=AxisId("x"),
                            size=SizeReference(
                                tensor_id=TensorId("input_1"), axis_id=AxisId("y")
                            ),
                        ),
                        SpaceInputAxis(
                            id=AxisId("y"), size=ParameterizedSize(min=256, step=8)
                        ),
                    ],
                    test_tensor=FileDescr(source=UNET2D_ROOT / "test_input.npy"),
                ),
            ],
            outputs=[
                OutputTensorDescr(
                    id=TensorId("output_1"),
                    description="Output 1",
                    axes=[
                        BatchAxis(),
                        ChannelAxis(channel_names=[Identifier("intensity")]),
                        SpaceOutputAxis(id=AxisId("x"), size=512),
                        SpaceOutputAxis(id=AxisId("y"), size=512),
                    ],
                    test_tensor=FileDescr(source=UNET2D_ROOT / "test_output.npy"),
                ),
            ],
            name="Model",
            tags=[],
            weights=WeightsDescr(
                onnx=OnnxWeightsDescr(
                    source=UNET2D_ROOT / "weights.onnx", opset_version=15
                )
            ),
            type="model",
        )


@pytest.fixture(scope="module")
def const_model_data(model: ModelDescr):
    data = model.model_dump(mode="json")
    assert data["documentation"] == str(UNET2D_ROOT / "README.md"), (
        data["documentation"],
        str(UNET2D_ROOT / "README.md"),
    )
    return MappingProxyType(data)


@pytest.fixture
def model_data(const_model_data: Mapping[str, Any]):
    return deepcopy(dict(const_model_data))


@pytest.mark.parametrize(
    "update",
    [
        dict(run_mode={"name": "special_run_mode", "kwargs": dict(marathon=True)}),
        dict(
            weights={
                "torchscript": {
                    "source": UNET2D_ROOT / "weights.onnx",
                    "pytorch_version": 1.15,
                }
            }
        ),
        dict(
            weights={
                "keras_hdf5": {
                    "source": UNET2D_ROOT / "weights.onnx",
                    "tensorflow_version": 1.10,
                }
            }
        ),
        dict(
            weights={
                "tensorflow_js": {
                    "source": UNET2D_ROOT / "weights.onnx",
                    "tensorflow_version": 1.10,
                }
            }
        ),
        dict(
            weights={
                "tensorflow_saved_model_bundle": {
                    "source": UNET2D_ROOT / "weights.onnx",
                    "tensorflow_version": 1.10,
                }
            }
        ),
        dict(
            weights={
                "onnx": {"source": UNET2D_ROOT / "weights.onnx", "opset_version": 15}
            }
        ),
        dict(
            weights={
                "pytorch_state_dict": {
                    "source": UNET2D_ROOT / "weights.onnx",
                    "pytorch_version": "1.15",
                    "architecture": {
                        "callable": "Model",
                        "source": "https://example.com/file.py",
                        "sha256": "0" * 64,  # dummy sha256
                    },
                },
            }
        ),
    ],
)
def test_model(model_data: Dict[str, Any], update: Dict[str, Any]):
    model_data.update(update)
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    summary.display()
    assert summary.status == "passed", summary.format()


def test_warn_long_name(model_data: Dict[str, Any]):
    model_data["name"] = (
        "veeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeery loooooooooooooooong name"
    )
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )

    assert summary.status == "passed", summary.format()
    assert summary.details[1].warnings[0].loc == ("name",), summary.format()
    assert summary.details[1].warnings[0].msg == "Name longer than 64 characters."


def test_model_schema_raises_invalid_input_id(model_data: Dict[str, Any]):
    model_data["inputs"][0]["id"] = "invalid/id"
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert summary.status == "failed", summary.format()


def test_output_fixed_shape_too_small(model_data: Dict[str, Any]):
    model_data["outputs"][0]["halo"] = 999
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert summary.status == "failed", summary.format()


def test_get_axis_sizes_with_surplus_n(model: ModelDescr):
    key = (model.inputs[0].id, AxisId("y"))
    _ = model.get_axis_sizes(ns={key: 1}, batch_size=1)


def test_get_axis_sizes_with_partial_max_size(model: ModelDescr):
    key = (model.inputs[0].id, AxisId("y"))
    ns = {key: 100}
    wo_max_shape = model.get_axis_sizes(ns=ns)
    with_max_shape = model.get_axis_sizes(ns=ns, max_input_shape={key: 32})
    assert wo_max_shape.inputs[key] > with_max_shape.inputs[key]


def test_get_axis_sizes_raises_with_missing_n(model_data: Dict[str, Any]):
    model_data["inputs"][0]["axes"][2] = {
        "type": "space",
        "id": "x",
        "size": {"min": 10, "step": 5},
    }

    with ValidationContext(perform_io_checks=False):
        model = ModelDescr(**model_data)

    with pytest.raises(ValueError):
        _ = model.get_axis_sizes(ns={}, batch_size=1)


def test_output_ref_shape_mismatch(model_data: Dict[str, Any]):
    model_data["outputs"][0]["axes"][2] = {
        "type": "space",
        "id": "x",
        "size": {"tensor_id": "input_1", "axis_id": "y"},
        "halo": 2,
    }
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert summary.status == "passed", summary.format()
    # input_1.x -> input_1.z
    model_data["outputs"][0]["axes"][2] = {
        "type": "space",
        "id": "x",
        "size": {"tensor_id": "input_1", "axis_id": "z"},
        "halo": 2,
    }
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert summary.status == "failed", summary.format()


def test_output_ref_shape_too_small(model_data: Dict[str, Any]):
    model_data["outputs"][0]["axes"][2] = {
        "type": "space",
        "id": "x",
        "size": {"tensor_id": "input_1", "axis_id": "y"},
        "halo": 2,
    }
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert summary.status == "passed", summary.format()

    model_data["outputs"][0]["axes"][2]["halo"] = 999
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert summary.status == "failed", summary.format()


def test_model_has_parent_with_id(model_data: Dict[str, Any]):
    model_data["parent"] = dict(id="10.5281/zenodo.5764892/6647674")
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert summary.status == "passed", summary.format()


def test_model_with_expanded_output(model_data: Dict[str, Any]):
    model_data["outputs"][0]["axes"] = [
        {
            "type": "space",
            "id": "x",
            "size": {"tensor_id": "input_1", "axis_id": "y"},
            "scale": 0.5,
        },
        {
            "type": "space",
            "id": "y",
            "size": {"tensor_id": "input_1", "axis_id": "y"},
            "scale": 4,
        },
        {"type": "space", "id": "z", "size": 7},
        {"type": "channel", "channel_names": list("abc")},
        {"type": "batch"},
    ]

    model = build_description(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert isinstance(model, ModelDescr), model.validation_summary.format()
    actual_inputs, actual_outputs = model.get_axis_sizes(
        {(TensorId("input_1"), AxisId("y")): 1}, batch_size=13
    )
    expected_inputs = {
        (TensorId("input_1"), AxisId("batch")): 13,
        (TensorId("input_1"), AxisId("channel")): 1,
        (TensorId("input_1"), AxisId("x")): 256 + 8,
        (TensorId("input_1"), AxisId("y")): 256 + 8,
    }
    expected_outputs = {
        (TensorId("output_1"), AxisId("batch")): 13,
        (TensorId("output_1"), AxisId("channel")): 3,
        (TensorId("output_1"), AxisId("x")): 2 * (256 + 8),
        (TensorId("output_1"), AxisId("y")): (256 + 8) // 4,
        (TensorId("output_1"), AxisId("z")): 7,
    }
    assert actual_inputs == expected_inputs
    assert actual_outputs == expected_outputs


def test_model_rdf_is_valid_general_rdf(model_data: Dict[str, Any]):
    model_data["type"] = "model_as_generic"
    model_data["format_version"] = "0.3.0"
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert summary.status == "passed", summary.format()


def test_model_does_not_accept_unknown_fields(model_data: Dict[str, Any]):
    model_data["unknown_additional_field"] = "shouldn't be here"
    summary = validate_format(
        model_data, context=ValidationContext(perform_io_checks=False)
    )
    assert summary.status == "failed", summary.format()


def test_empty_axis_data():
    from bioimageio.spec.model.v0_5 import InputAxis as InputAxisUnion
    from bioimageio.spec.model.v0_5 import OutputAxis as OutputAxisUnion

    InputAxis = RootModel[InputAxisUnion]

    with pytest.raises(ValidationError):
        _ = InputAxis.model_validate({})

    OutputAxis = RootModel[OutputAxisUnion]

    with pytest.raises(ValidationError):
        _ = OutputAxis.model_validate({})


@pytest.mark.parametrize(
    "a,b", [(TensorId("t"), TensorId("t")), (AxisId("a"), AxisId("a"))]
)
def test_identifier_identity(a: Any, b: Any):
    assert a == b


def test_validate_parameterized_size(model: ModelDescr):
    param_size = model.inputs[0].axes[3].size
    assert isinstance(param_size, ParameterizedSize), type(param_size)
    assert (actual := param_size.validate_size(512)) == 512, actual
