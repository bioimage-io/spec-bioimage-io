from datetime import datetime

import pytest
from marshmallow import ValidationError

from bioimageio.spec.model.v0_4 import raw_nodes as raw_nodes_m04
from bioimageio.spec.shared import yaml

SKIP_ZENODO = True
SKIP_ZENODO_REASON = "zenodo api changes"


def test_model_rdf_is_valid_general_rdf(unet2d_nuclei_broad_latest):
    from bioimageio.spec.rdf.schema import RDF

    assert yaml is not None
    data = yaml.load(unet2d_nuclei_broad_latest)
    data["root_path"] = unet2d_nuclei_broad_latest.parent

    RDF().load(data)


def test_model_does_not_accept_unknown_fields(unet2d_nuclei_broad_latest):
    from bioimageio.spec.model.schema import Model

    assert yaml is not None
    data = yaml.load(unet2d_nuclei_broad_latest)
    data["root_path"] = unet2d_nuclei_broad_latest.parent

    data["unknown_additional_field"] = "shouldn't be here"

    with pytest.raises(ValidationError):
        Model().load(data)


@pytest.fixture
def model_dict():
    """
    Valid model dict fixture
    """
    return {
        "documentation": "./docs.md",
        "license": "MIT",
        "git_repo": "https://github.com/bioimage-io/python-bioimage-io",
        "format_version": "0.4.0",
        "description": "description",
        "authors": [
            {"name": "Author 1", "affiliation": "Affiliation 1"},
            {"name": "Author 2", "affiliation": "Affiliation 2"},
        ],
        "maintainers": [
            {"name": "Author 1", "affiliation": "Affiliation 1", "github_user": "githubuser1"},
            {"name": "Author 2", "affiliation": "Affiliation 2", "github_user": "githubuser2"},
        ],
        "timestamp": datetime.now(),
        "cite": [{"text": "Paper title", "doi": "doi"}],
        "inputs": [
            {"name": "input_1", "description": "Input 1", "data_type": "float32", "axes": "xyc", "shape": [128, 128, 3]}
        ],
        "outputs": [
            {
                "name": "output_1",
                "description": "Output 1",
                "data_type": "float32",
                "axes": "xyc",
                "shape": [128, 128, 3],
            }
        ],
        "name": "Model",
        "tags": [],
        "weights": {},
        "test_inputs": ["test_ipt.npy"],
        "test_outputs": ["test_out.npy"],
        "type": "model",
    }


def test_model_schema_accepts_run_mode(model_dict):
    from bioimageio.spec.model.schema import Model

    model_schema = Model()
    model_dict.update({"run_mode": {"name": "special_run_mode", "kwargs": dict(marathon=True)}})
    validated_data = model_schema.load(model_dict)
    assert validated_data


@pytest.mark.parametrize(
    "format",
    ["pytorch_state_dict", "torchscript", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"],
)
def test_model_schema_accepts_valid_weight_formats(model_dict, format):
    from bioimageio.spec.model.schema import Model

    model_schema = Model()
    model_dict.update({"weights": {format: {"source": "local_weights"}}})
    if format == "pytorch_state_dict":
        model_dict["weights"][format]["architecture"] = "file.py:Model"
        model_dict["weights"][format]["architecture_sha256"] = "0" * 64  # dummy sha256

    validated_data = model_schema.load(model_dict)
    assert validated_data


def test_model_schema_raises_invalid_name(model_dict):
    from bioimageio.spec.model.schema import Model

    model_schema = Model()
    model_dict["name"] = "invalid/name"
    with pytest.raises(ValidationError):
        model_schema.load(model_dict)


def test_model_schema_raises_invalid_input_name(model_dict):
    from bioimageio.spec.model.schema import Model

    model_schema = Model()
    model_dict["inputs"][0]["name"] = "invalid/name"
    with pytest.raises(ValidationError):
        model_schema.load(model_dict)


def test_model_schema_raises_invalid_output_name(model_dict):
    from bioimageio.spec.model.schema import Model

    model_schema = Model()
    model_dict["outputs"][0]["name"] = "invalid/name"
    with pytest.raises(ValidationError):
        model_schema.load(model_dict)


def test_model_0_4_raises_on_duplicate_tensor_names(invalid_rdf_v0_4_0_duplicate_tensor_names):
    from bioimageio.spec.model.schema import Model
    from bioimageio.spec.model.v0_3.schema import Model as Model_v03

    assert yaml is not None
    data = yaml.load(invalid_rdf_v0_4_0_duplicate_tensor_names)

    model_schema = Model()
    with pytest.raises(ValidationError):
        model_schema.load(data)

    # as 0.3 the model should still be valid with some small changes
    model_schema = Model_v03()
    data["format_version"] = "0.3.3"
    data["language"] = "python"
    data["framework"] = "pytorch"
    data["source"] = data["weights"]["pytorch_state_dict"].pop("architecture")
    data["kwargs"] = data["weights"]["pytorch_state_dict"].pop("kwargs")
    data["sha256"] = data["weights"]["pytorch_state_dict"].pop("architecture_sha256")

    valid_data = model_schema.load(data)
    assert valid_data


def test_output_fixed_shape_too_small(model_dict):
    from bioimageio.spec.model.schema import Model

    model_dict["outputs"] = [
        {
            "name": "output_1",
            "description": "Output 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": [128, 128, 3],
            "halo": [32, 128, 0],
        }
    ]

    with pytest.raises(ValidationError) as e:
        Model().load(model_dict)

    assert e.value.messages == {
        "_schema": ["Minimal shape [128 128   3] of output output_1 is too small for halo [32, 128, 0]."]
    }


def test_output_ref_shape_mismatch(model_dict):
    from bioimageio.spec.model.schema import Model

    model_dict["outputs"] = [
        {
            "name": "output_1",
            "description": "Output 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": {"reference_tensor": "input_1", "scale": [1, 2, 3, 4], "offset": [0, 0, 0, 0]},
        }
    ]

    with pytest.raises(ValidationError) as e:
        Model().load(model_dict)

    assert e.value.messages == {
        "_schema": [
            "Referenced tensor input_1 with 3 dimensions does not match output tensor output_1 with 4 dimensions."
        ]
    }


def test_output_ref_shape_too_small(model_dict):
    from bioimageio.spec.model.schema import Model

    model_dict["outputs"] = [
        {
            "name": "output_1",
            "description": "Output 1",
            "data_type": "float32",
            "axes": "xyc",
            "shape": {"reference_tensor": "input_1", "scale": [1, 2, 3], "offset": [0, 0, 0]},
            "halo": [256, 128, 0],
        }
    ]

    with pytest.raises(ValidationError) as e:
        Model().load(model_dict)

    assert e.value.messages == {
        "_schema": ["Minimal shape [128. 256.   9.] of output output_1 is too small for halo [256, 128, 0]."]
    }


@pytest.mark.skipif(SKIP_ZENODO, reason=SKIP_ZENODO_REASON)
def test_model_has_parent_with_uri(model_dict):
    from bioimageio.spec.model.schema import Model

    model_dict["parent"] = dict(uri="https://doi.org/10.5281/zenodo.5744489")

    valid_data = Model().load(model_dict)
    assert isinstance(valid_data, raw_nodes_m04.Model)


@pytest.mark.skipif(SKIP_ZENODO, reason=SKIP_ZENODO_REASON)
def test_model_has_parent_with_id(model_dict):
    from bioimageio.spec.model.schema import Model

    model_dict["parent"] = dict(id="10.5281/zenodo.5764892")

    valid_data = Model().load(model_dict)
    assert isinstance(valid_data, raw_nodes_m04.Model)


def test_model_with_expanded_output(model_dict):
    from bioimageio.spec.model.schema import Model

    model_dict["outputs"] = [
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

    model = Model().load(model_dict)
    assert isinstance(model, raw_nodes_m04.Model)
    out0_shape = model.outputs[0].shape
    assert isinstance(out0_shape, raw_nodes_m04.ImplicitOutputShape)
    assert out0_shape.scale == [1, 1, None, 1]
