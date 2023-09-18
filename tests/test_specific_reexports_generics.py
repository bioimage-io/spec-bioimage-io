import ast
import inspect
from types import ModuleType
from typing import Iterator

import pytest

import bioimageio.spec

GENERIC_ONLY_MEMBERS = {
    "Generic",
    "GenericBase",
    "GenericBaseNoSource",
    "KNOWN_SPECIFIC_RESOURCE_TYPES",
    "GenericBaseNoSource",
    "ResourceDescriptionType",
    "GenericBaseNoFormatVersion",
    "VALID_COVER_IMAGE_EXTENSIONS",
}


def iterate_members(module: ModuleType) -> Iterator[str]:
    code = inspect.getsource(module)
    root = ast.parse(code)
    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.ImportFrom):
            for name in node.names:
                if name.asname is not None and not name.asname.startswith("_"):
                    yield name.asname
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            yield node.name


GENERIC_v0_2_MEMBERS = tuple(
    [m for m in iterate_members(bioimageio.spec.generic.v0_2) if m not in GENERIC_ONLY_MEMBERS]
)

GENERIC_v0_3_MEMBERS = tuple(
    [m for m in iterate_members(bioimageio.spec.generic.v0_3) if m not in GENERIC_ONLY_MEMBERS]
)


@pytest.mark.parametrize(
    "specific",
    [
        bioimageio.spec.application.v0_2,
        bioimageio.spec.collection.v0_2,
        bioimageio.spec.dataset.v0_2,
        bioimageio.spec.model.v0_4,
        bioimageio.spec.notebook.v0_2,
    ],
)
def test_specific_reexports_genericv02(specific: ModuleType):
    members = set(iterate_members(specific))
    missing = {r for r in GENERIC_v0_2_MEMBERS if r not in members}
    assert not missing


@pytest.mark.parametrize(
    "specific",
    [
        bioimageio.spec.application.v0_3,
        bioimageio.spec.collection.v0_3,
        bioimageio.spec.dataset.v0_3,
        bioimageio.spec.model.v0_5,
        bioimageio.spec.notebook.v0_3,
    ],
)
def test_specific_reexports_genericv03(specific: ModuleType):
    members = set(iterate_members(specific))
    missing = {r for r in GENERIC_v0_3_MEMBERS if r not in members}
    assert not missing
