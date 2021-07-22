import pytest
from marshmallow import ValidationError
from pytest import raises

from bioimageio.spec.shared import get_dict_and_root_path_from_yaml_source


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


def test_model_rdf_is_valid_general_rdf(unet2d_nuclei_broad_latest_path):
    from bioimageio.spec.rdf.schema import RDF

    data, root_path = get_dict_and_root_path_from_yaml_source(unet2d_nuclei_broad_latest_path)

    RDF().load(data)


def test_model_does_not_accept_unknown_fields(unet2d_nuclei_broad_latest_path):
    from bioimageio.spec.model.schema import Model

    data, root_path = get_dict_and_root_path_from_yaml_source(unet2d_nuclei_broad_latest_path)

    data["unknown_additional_field"] = "shouldn't be here"

    with pytest.raises(ValidationError):
        Model().load(data)
