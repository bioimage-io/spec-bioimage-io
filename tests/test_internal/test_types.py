import typing
from pathlib import Path

import pytest

import bioimageio.spec._internal.io_basics
import bioimageio.spec._internal.io_validation
import bioimageio.spec._internal.url
from bioimageio.spec._internal import types

TYPE_ARGS = {
    bioimageio.spec._internal.io_basics.AbsoluteDirectory: str(
        Path(__file__).absolute().parent
    ),
    bioimageio.spec._internal.io_basics.AbsoluteFilePath: str(
        Path(__file__).absolute()
    ),
    types.ApplicationId: "appdev/app",
    types.CollectionId: "collectionid",
    types.DatasetId: "dataset-id",
    types.Datetime: (2024, 2, 14),
    types.Doi: "10.5281/zenodo.5764892",
    bioimageio.spec._internal.io_basics.FileName: "lala.py",
    bioimageio.spec._internal.url.HttpUrl: "http://example.com",
    types.Identifier: "id",
    types.IdentifierStr: "id",
    types.ImportantFileSource: "README.md",
    types.LowerCaseIdentifier: "id",
    types.LowerCaseIdentifierStr: "id",
    types.ModelId: "modelid",
    types.NotebookId: "notebookid",
    types.OrcidId: "0000-0001-2345-6789",
    types.RelativeFilePath: "here.py",
    types.ResourceId: "resoruce-id",
    bioimageio.spec._internal.io_validation.Sha256: "0" * 64,
    types.SiUnit: "kg",
    types.Version: "1.0",
}

IGNORE_TYPES_MEMBERS = {
    "annotated_types",
    "annotations",
    "IncludeInPackage",
    "NotEmpty",
    "typing",
    "YamlValue",
    "ImportantFileSource",  # an annoated union
    "field_validation",
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
    """check if a type can be instantiated or is a common Python type (e.g. Union or Literal)"""
    typ = getattr(types, name)
    if typ in TYPE_ARGS:
        args = TYPE_ARGS[typ]
        if not isinstance(args, tuple):
            args = (args,)
        _ = typ(*args)
    elif isinstance(typ, str):
        pass  # ignore string constants
    else:
        origin = typing.get_origin(typ)
        assert origin in (dict, list, typing.Union, typing.Literal) or type(typ) in (
            typing.TypeVar,
        ), name
