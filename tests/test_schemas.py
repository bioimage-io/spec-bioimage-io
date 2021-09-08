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
