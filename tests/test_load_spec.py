from pathlib import Path

import pytest
from marshmallow import ValidationError

from bioimageio.spec import load_model


def test_load_non_existing_spec():
    spec_path = Path("some/none/existing/path/to/spec.model.yaml")

    with pytest.raises(FileNotFoundError):
        load_model(spec_path)


def test_load_non_valid_spec_name():
    spec_path = Path("some/none/existing/path/to/spec.not_valid_suffix")

    with pytest.raises(ValidationError):
        load_model(spec_path)
