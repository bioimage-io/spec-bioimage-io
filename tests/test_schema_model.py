from datetime import datetime

import pytest
from marshmallow import ValidationError


def test_model_rdf_is_valid_general_rdf(unet2d_nuclei_broad_latest):
    from bioimageio.spec.rdf.schema import RDF

    RDF().load(unet2d_nuclei_broad_latest)


def test_model_does_not_accept_unknown_fields(unet2d_nuclei_broad_latest):
    from bioimageio.spec.model.schema import Model

    unet2d_nuclei_broad_latest["unknown_additional_field"] = "shouldn't be here"

    with pytest.raises(ValidationError):
        Model().load(unet2d_nuclei_broad_latest)


@pytest.fixture
def model_dict():
    """
    Valid model dict fixture
    """
    return {
        "documentation": "./docs.md",
        "license": "MIT",
        "framework": "pytorch",
        "language": "python",
        "source": "somesrc",
        "git_repo": "https://github.com/bioimage-io/python-bioimage-io",
        "format_version": "0.3.0",
        "description": "description",
        "authors": [
            {"name": "Author 1", "affiliation": "Affiliation 1"},
            {"name": "Author 2", "affiliation": "Affiliation 2"},
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
        "test_inputs": [],
        "test_outputs": [],
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
    ["pytorch_state_dict", "pytorch_script", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"],
)
def test_model_schema_accepts_valid_weight_formats(model_dict, format):
    from bioimageio.spec.model.schema import Model

    model_schema = Model()
    model_dict.update({"weights": {format: {"source": "local_weights"}}})
    validated_data = model_schema.load(model_dict)
    assert validated_data


def test_model_0_4_raises_on_duplicate_tensor_names(invalid_rdf_v0_4_0_duplicate_tensor_names):
    from bioimageio.spec.model.schema import Model
    from bioimageio.spec.model.v0_3.schema import Model as Model_v03

    model_schema = Model()
    with pytest.raises(ValidationError):
        model_schema.load(invalid_rdf_v0_4_0_duplicate_tensor_names)

    # as 0.3 the model should still be valid
    model_schema = Model_v03()
    invalid_rdf_v0_4_0_duplicate_tensor_names["format_version"] = "0.3.3"
    valid_data = model_schema.load(invalid_rdf_v0_4_0_duplicate_tensor_names)
    assert valid_data
