import pytest
from marshmallow import ValidationError
from pytest import raises


class TestPreprocessing:
    class TestZeroMeanUniVarianceKwargs:
        def test_invalid(self):
            from bioimageio.spec.model import schema

            with raises(ValidationError):
                schema.Preprocessing().load({"name": "zero_mean_unit_variance"})

        def test_mode_fixed(self):
            from bioimageio.spec.model import schema

            schema.Preprocessing().load(
                {"name": "zero_mean_unit_variance", "kwargs": {"mode": "fixed", "mean": 1, "std": 2, "axes": "xy"}}
            )


def test_model_rdf_is_valid_general_rdf(unet2d_nuclei_broad_latest):
    from bioimageio.spec.rdf.schema import RDF

    RDF().load(unet2d_nuclei_broad_latest)


def test_model_does_not_accept_unknown_fields(unet2d_nuclei_broad_latest):
    from bioimageio.spec.model.schema import Model

    unet2d_nuclei_broad_latest["unknown_additional_field"] = "shouldn't be here"

    with pytest.raises(ValidationError):
        Model().load(unet2d_nuclei_broad_latest)


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
