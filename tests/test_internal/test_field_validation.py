from datetime import datetime
from typing import ClassVar, Literal, Optional

import pytest
from pydantic import Field

from bioimageio.spec._internal.node import Node
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


def test_FAIR():
    from bioimageio.spec._internal.common_nodes import ResourceDescrBase
    from bioimageio.spec._internal.types import FAIR

    class Nested(Node):
        c_opt1: FAIR[str] = ""  # empty string is not FAIR (warning 3)

    class MyDescr(ResourceDescrBase):
        implemented_type: ClassVar[Literal["test"]] = "test"
        implemented_format_version: ClassVar[Literal["1.0.0"]] = "1.0.0"
        type: Literal["test"]
        format_version: Literal["1.0.0"]

        a_opt1: FAIR[int] = 0  # actual int value is considered FAIR
        a_opt2: FAIR[Optional[str]] = None  # None is not FAIR (warning 1)
        a_opt3: FAIR[str] = ""  # empty string is not FAIR (warning 2)
        nested: Nested = Field(default_factory=Nested.model_construct)

    my_descr = MyDescr.load({})
    assert (
        len(my_descr.validation_summary.warnings) == 3
    ), my_descr.validation_summary.display() or [
        e.msg for e in my_descr.validation_summary.errors
    ]
