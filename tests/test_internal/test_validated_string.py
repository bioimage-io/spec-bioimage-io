from typing import Any, ClassVar, Type

import annotated_types
import pytest
from pydantic import RootModel, ValidationError
from typing_extensions import Annotated


def test_valid_validated_string():
    from bioimageio.spec._internal.validated_string import ValidatedString

    class V(ValidatedString):
        root_model: ClassVar[Type[RootModel[Any]]] = RootModel[
            Annotated[str, annotated_types.Predicate(str.islower)]
        ]

    out = V("abc")
    assert isinstance(out, str)
    assert out == "abc"

    with pytest.raises(ValidationError):
        _ = V("ABC")
