from datetime import datetime

import pytest

from bioimageio.spec._internal.validation_context import ValidationContext


def test_is_valid_yaml_value():
    from bioimageio.spec._internal.field_validation import is_valid_yaml_value

    class Obj:
        pass

    invalid = {"a": 1, "b": ["1", 2, Obj()]}

    assert not is_valid_yaml_value(invalid)

    valid = {"a": 1, "b": ["1", 2], ("c", 1): ("a", "b", datetime.now())}
    assert is_valid_yaml_value(valid)


def test_validate_unique_entries():
    from bioimageio.spec._internal.field_validation import validate_unique_entries

    with pytest.raises(ValueError):
        _ = validate_unique_entries(["a", "a"])

    ret = validate_unique_entries(["a", "b"])
    assert ret == ["a", "b"]


def test_validate_github_user():
    from bioimageio.spec._internal.field_validation import validate_github_user

    with pytest.raises(ValueError), ValidationContext(perform_io_checks=True):
        _ = validate_github_user("arratemunoz")

    cpape = validate_github_user("Constantin Pape", hotfix_known_errorenous_names=True)
    assert cpape == "constantinpape"

    fynnbe = validate_github_user("fynnbe")
    assert fynnbe == "fynnbe"
