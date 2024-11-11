from types import ModuleType
from typing import Any, Dict

import pytest

from bioimageio.spec import application, dataset, generic, model, notebook

IGNORE_MEMBERS = {
    "AfterValidator",
    "ALERT",
    "annotated_types",
    "Annotated",
    "annotations",
    "Any",
    "as_warning",
    "assert_never",
    "BioimageioYamlContent",
    "ClassVar",
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
    "include_in_package_serializer",
    "INFO",
    "InPackageIfLocalFileSource",
    "is_sequence",
    "issue_warning",
    "Len",
    "LicenseId",
    "LICENSES",
    "List",
    "LowerCase",
    "Mapping",
    "MarkdownSource",
    "MaxLen",
    "MinLen",
    "model_validator",
    "Node",
    "NotEmpty",
    "Optional",
    "partial",
    "PermissiveFileSource",
    "Predicate",
    "requests",
    "RestrictCharacters",
    "RootModel",
    "S",
    "Self",
    "Sequence",
    "settings",
    "string",
    "TAG_CATEGORIES",
    "Type",
    "TypeVar",
    "Union",
    "V_suffix",
    "v0_2",
    "v0_3",
    "v0_4",
    "v0_5",
    "validate_gh_user",
    "validate_suffix",
    "ValidatedString",
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
    "LinkedResourceNode",
    "ResourceDescrBase",
    "ResourceDescrType",
}

GENERIC_v0_2_MEMBERS = {
    k: v for k, v in get_members(generic.v0_2).items() if k not in GENERIC_ONLY_MEMBERS
}
GENERIC_v0_3_MEMBERS = {
    k: v for k, v in get_members(generic.v0_3).items() if k not in GENERIC_ONLY_MEMBERS
}


@pytest.mark.parametrize(
    "generic_members,specific",
    [
        (GENERIC_v0_2_MEMBERS, application.v0_2),
        (GENERIC_v0_2_MEMBERS, dataset.v0_2),
        (GENERIC_v0_2_MEMBERS, model.v0_4),
        (GENERIC_v0_2_MEMBERS, notebook.v0_2),
        (GENERIC_v0_3_MEMBERS, application.v0_3),
        (GENERIC_v0_3_MEMBERS, dataset.v0_3),
        (GENERIC_v0_3_MEMBERS, model.v0_5),
        (GENERIC_v0_3_MEMBERS, notebook.v0_3),
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
