from pathlib import Path

import pytest
from marshmallow import ValidationError


def test_load_non_existing_spec():
    from bioimageio.spec import load_node

    spec_path = Path("some/none/existing/path/to/spec.model.yaml")

    with pytest.raises(FileNotFoundError):
        load_node(spec_path)


def test_load_non_valid_spec_name():
    from bioimageio.spec import load_node

    spec_path = Path("some/none/existing/path/to/spec.not_valid_suffix")

    with pytest.raises(ValidationError):
        load_node(spec_path)
