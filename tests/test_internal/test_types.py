from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from dateutil.parser import isoparse
from pydantic import PlainSerializer, TypeAdapter
from typing_extensions import Annotated

import bioimageio.spec._internal.io_basics
from bioimageio.spec._internal import types
from bioimageio.spec._internal.io import RelativeFilePath
from bioimageio.spec._internal.types import Datetime, SiUnit
from tests.utils import check_type

TYPE_ARGS = {
    types.Datetime: (2024, 2, 14),
    types.Datetime: datetime.now().isoformat(),
    types.DeprecatedLicenseId: "AGPL-1.0",
    types.Doi: "10.5281/zenodo.5764892",
    types.Identifier: "id",
    types.IdentifierAnno: "id",
    types.ImportantFileSource: "README.md",
    types.LicenseId: "MIT",
    types.LowerCaseIdentifier: "id",
    types.LowerCaseIdentifierAnno: "id",
    types.OrcidId: "0000-0001-2345-6789",
    types.RelativeFilePath: Path(__file__).relative_to(Path().absolute()),
    types.SiUnit: "kg",
    types.AbsoluteDirectory: str(Path(__file__).absolute().parent),
    types.AbsoluteFilePath: str(Path(__file__).absolute()),
    types.FileName: "lala.py",
    types.Version: "1.0",
    types.HttpUrl: "http://example.com",
    bioimageio.spec._internal.io_basics.Sha256: "0" * 64,
}

IGNORE_TYPES_MEMBERS = {
    "AfterValidator",
    "annotated_types",
    "Annotated",
    "annotations",
    "Any",
    "BeforeValidator",
    "ClassVar",
    "datetime",
    "field_validation",
    "FileSource",
    "FormatVersionPlaceholder",  # a literal
    "ImportantFileSource",  # an annoated union
    "iskeyword",
    "isoparse",
    "Literal",
    "NotEmpty",
    "PermissiveFileSource",
    "PlainSerializer",
    "RootModel",
    "S",
    "Sequence",
    "StringConstraints",
    "Type",
    "TypeVar",
    "typing",
    "Union",
    "ValidatedString",
    "YamlValue",
}


@pytest.mark.parametrize(
    "name",
    [
        name
        for name in dir(types)
        if not name.startswith("_") and name not in IGNORE_TYPES_MEMBERS
    ],
)
def test_type_is_usable(name: str):
    """check if a type can be instantiated"""
    typ = getattr(types, name)
    if typ in TYPE_ARGS:
        args = TYPE_ARGS[typ]
        if not isinstance(args, tuple):
            args = (args,)
        _ = typ(*args)
    elif isinstance(typ, str):
        pass  # ignore string constants
    else:
        raise ValueError(f"No idea how to test {name} -> {typ}")


@pytest.mark.parametrize("path", [Path(__file__), Path()])
def test_relative_path(path: Path):
    with pytest.raises(ValueError):
        _ = RelativeFilePath(path.absolute())

    with pytest.raises(ValueError):
        _ = RelativeFilePath(
            str(path.absolute())  # pyright: ignore[reportArgumentType]
        )

    with pytest.raises(ValueError):
        _ = RelativeFilePath(
            path.absolute().as_posix()  # pyright: ignore[reportArgumentType]
        )


@pytest.mark.parametrize("value", ["lx·s", "kg/m^2·s^-2"])
def test_si_unit(value: str):
    check_type(SiUnit, value)


@pytest.mark.parametrize("value", ["lxs", " kg"])
def test_si_unit_invalid(value: str):
    check_type(SiUnit, value, is_invalid=True)


@pytest.mark.parametrize(
    "value,expected",
    [
        (
            "2019-12-11T12:22:32+00:00",
            isoparse("2019-12-11T12:22:32+00:00"),
        ),
        (
            "2019-12-11T12:22:32",
            datetime(2019, 12, 11, 12, 22, 32),
        ),
        (
            "2019-12-11T12:22:32-00:08",
            isoparse("2019-12-11T12:22:32-00:08"),
        ),
    ],
)
def test_datetime(value: str, expected: datetime):
    check_type(
        Datetime,
        value,
        expected_root=expected,
        expected_deserialized=value,
    )


@pytest.mark.parametrize(
    "value",
    [
        "2024-03-06T14:21:34.384830",
        "2024-03-06T14:21:34+00:00",
        "2024-03-06T14:21:34+00:05",
        "2024-03-06T14:21:34-00:08",
        "2019-12-11T12:22:32Z",
    ],
)
def test_datetime_more(value: str):
    from bioimageio.spec._internal.types import (
        _serialize_datetime_json,  # pyright: ignore[reportPrivateUsage]
    )

    root_adapter = TypeAdapter(Datetime)
    datetime_adapter: TypeAdapter[Any] = TypeAdapter(
        Annotated[
            datetime,
            PlainSerializer(_serialize_datetime_json, when_used="json-unless-none"),
        ]
    )

    expected = isoparse(value)

    actual_init = Datetime(expected)
    assert actual_init.root == expected

    actual_root = root_adapter.validate_python(value)
    assert actual_root.root == expected
    assert root_adapter.dump_python(actual_root, mode="python") == expected
    assert root_adapter.dump_python(actual_root, mode="json") == value.replace(
        "Z", "+00:00"
    )

    actual_datetime = datetime_adapter.validate_python(value)
    assert actual_datetime == expected
    assert datetime_adapter.dump_python(actual_datetime, mode="python") == expected
    assert datetime_adapter.dump_python(actual_datetime, mode="json") == value.replace(
        "Z", "+00:00"
    )


@pytest.mark.parametrize(
    "value",
    [
        "2019-12-11T12:22:32+00/00",
        "2019-12-11T12:22:32Y",
        "2019-12-11T12:22:32Zulu",
        "201912-11T12:22:32+00:00",
        "now",
        "today",
    ],
)
def test_datetime_invalid(value: str):
    check_type(Datetime, value, is_invalid=True)
