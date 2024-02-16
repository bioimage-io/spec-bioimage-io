from types import ModuleType
from typing import Any, Dict

import pytest

import bioimageio.spec

IGNORE_MEMBERS = {
    "ALERT",
    "Annotated",
    "annotations",
    "Any",
    "as_warning",
    "BioimageioYamlContent",
    "collections",
    "convert_from_older_format",
    "Converter",
    "CoverImageSource",
    "DeprecatedLicenseId",
    "Dict",
    "DocumentationSource",
    "EmailStr",
    "field_validator",
    "Field",
    "FileSource",
    "Ge",
    "get_args",
    "ImportantFileSource",
    "IncludeInPackage",
    "issue_warning",
    "Len",
    "LicenseId",
    "LICENSES",
    "List",
    "LowerCase",
    "Mapping",
    "MarkdownSource",
    "MaxLen",
    "model_validator",
    "Node",
    "NotEmpty",
    "Optional",
    "partial",
    "Predicate",
    "requests",
    "ResourceDescriptionBase",
    "ResourceDescrType",
    "Self",
    "Sequence",
    "settings",
    "TAG_CATEGORIES",
    "TypeVar",
    "Union",
    "v0_2",
    "v0_3",
    "v0_4",
    "v0_5",
    "validation_context_var",
    "ValidationInfo",
    "warn",
    "WithSuffix",
    "YamlValue",
}


def get_members(m: ModuleType):
    return {
        k: getattr(m, k)
        for k in dir(m)
        if not k.startswith("_") and k not in IGNORE_MEMBERS
    }


GENERIC_ONLY_MEMBERS = {
    "GenericDescr",
    "GenericDescrBase",
    "GenericModelDescrBase",
    "KNOWN_SPECIFIC_RESOURCE_TYPES",
    "VALID_COVER_IMAGE_EXTENSIONS",
}

GENERIC_v0_2_MEMBERS = {
    k: v
    for k, v in get_members(bioimageio.spec.generic.v0_2).items()
    if k not in GENERIC_ONLY_MEMBERS
}
GENERIC_v0_3_MEMBERS = {
    k: v
    for k, v in get_members(bioimageio.spec.generic.v0_3).items()
    if k not in GENERIC_ONLY_MEMBERS
}


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
def test_specific_module_has_all_generic_symbols(
    generic_members: Dict[str, Any], specific: ModuleType
):
    members = get_members(specific)
    missing = {k for k in generic_members if k not in members}
    assert not missing
    unidentical = {k for k, v in generic_members.items() if v is not members[k]}
    assert not unidentical
