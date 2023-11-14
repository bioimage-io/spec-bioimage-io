import ast
import inspect
from types import ModuleType
from typing import Any, Dict, Iterator, Tuple

import pytest

import bioimageio.spec

GENERIC_ONLY_MEMBERS = {
    "FileSourceWithSha256",
    "Generic",
    "GenericBase",
    "GenericBaseNoFormatVersion",
    "GenericBaseNoSource",
    "GenericModelBase",
    "KNOWN_SPECIFIC_RESOURCE_TYPES",
    "ResourceDescriptionType",
    "VALID_COVER_IMAGE_EXTENSIONS",
}


def iterate_members(module: ModuleType) -> Iterator[Tuple[str, Any]]:
    code = inspect.getsource(module)
    root = ast.parse(code)
    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.ImportFrom):
            for name in node.names:
                if name.asname is not None and not name.asname.startswith("_"):
                    yield name.asname, getattr(module, name.asname)
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            yield node.name, getattr(module, node.name)


GENERIC_v0_2_MEMBERS = {k: v for k, v in iterate_members(bioimageio.spec.generic.v0_2) if k not in GENERIC_ONLY_MEMBERS}

GENERIC_v0_3_MEMBERS = {k: v for k, v in iterate_members(bioimageio.spec.generic.v0_3) if k not in GENERIC_ONLY_MEMBERS}


@pytest.mark.parametrize(
    "generic_members,specific",
    [
        (GENERIC_v0_2_MEMBERS, bioimageio.spec.application.v0_2),
        (GENERIC_v0_2_MEMBERS, bioimageio.spec.collection.v0_2),
        (GENERIC_v0_2_MEMBERS, bioimageio.spec.dataset.v0_2),
        (GENERIC_v0_2_MEMBERS, bioimageio.spec.model.v0_4),
        (GENERIC_v0_2_MEMBERS, bioimageio.spec.notebook.v0_2),
        (GENERIC_v0_3_MEMBERS, bioimageio.spec.application.v0_3),
        (GENERIC_v0_3_MEMBERS, bioimageio.spec.collection.v0_3),
        (GENERIC_v0_3_MEMBERS, bioimageio.spec.dataset.v0_3),
        (GENERIC_v0_3_MEMBERS, bioimageio.spec.model.v0_5),
        (GENERIC_v0_3_MEMBERS, bioimageio.spec.notebook.v0_3),
    ],
)
def test_specific_module_has_all_generic_symbols(generic_members: Dict[str, Any], specific: ModuleType):
    members = dict(iterate_members(specific))
    missing = {k for k in generic_members if k not in members}
    assert not missing
    unidentical = {k for k, v in generic_members.items() if v is not members[k]}
    assert not unidentical
