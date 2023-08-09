from datetime import datetime

import pytest
from marshmallow import ValidationError

from bioimageio.spec.model.v0_4 import raw_nodes as raw_nodes_m04
from bioimageio.spec.shared import yaml


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
