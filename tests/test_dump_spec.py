from copy import deepcopy

from bioimageio.spec import load_raw_model, raw_nodes, schema
from bioimageio.spec.shared import yaml


def test_spec_roundtrip(rf_config_path):
    data = yaml.load(rf_config_path)

    raw_model = load_raw_model(rf_config_path)
    assert isinstance(raw_model, raw_nodes.Model)

    serialized = schema.Model().dump(raw_model)
    assert isinstance(serialized, dict)

    # yaml.dump(serialized, Path() / "serialized.yml")

    assert serialized == data

    assert not schema.Model().validate(serialized)

    raw_model_from_serialized = load_raw_model(serialized)
    assert raw_model_from_serialized == raw_model

    raw_model_from_serialized_wo_defaults = load_raw_model(serialized)
    assert raw_model_from_serialized_wo_defaults == raw_model
