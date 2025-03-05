from datetime import datetime, timezone
from pathlib import Path

import pytest
from dateutil.parser import isoparse

import bioimageio.spec._internal.io_basics
from bioimageio.spec._internal import types
from bioimageio.spec._internal.io import RelativeFilePath
from tests.utils import check_type

UTC = timezone.utc

TYPE_ARGS = {
    types.Datetime: (2024, 2, 14),
    types.Datetime: datetime.now().astimezone(UTC).isoformat(timespec="seconds"),
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
    types.AbsoluteTolerance: 3,
    types.RelativeTolerance: 1.0e-6,
    types.MismatchedElementsPerMillion: 99,
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
    "FilePath",
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
    "timezone",
    "Type",
    "TypeVar",
    "typing",
    "Union",
    "UTC",
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
        _ = typ(*args)  # type: ignore
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


@pytest.mark.parametrize("value", ["0000-0002-1109-110X"])
def test_orcid_id(value: str):
    check_type(types.OrcidId, value)


@pytest.mark.parametrize("value", ["lx·s", "kg/m^2·s^-2"])
def test_si_unit(value: str):
    check_type(types.SiUnit, value)


@pytest.mark.parametrize("value", ["lxs", " kg"])
def test_si_unit_invalid(value: str):
    check_type(types.SiUnit, value, is_invalid=True)


@pytest.mark.parametrize(
    "value,expected",
    [
        (
            "2001-12-11T12:22:32+00:00",
            isoparse("2001-12-11T12:22:32+00:00"),
        ),
        (
            "2002-12-11T12:22:32+00:00",
            datetime(2002, 12, 11, 12, 22, 32, tzinfo=UTC),
        ),
    ],
)
def test_datetime(value: str, expected: datetime):
    check_type(
        types.Datetime,
        value,
        expected_root=expected,
        expected_deserialized=value,
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
    check_type(types.Datetime, value, is_invalid=True)
