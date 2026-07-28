from __future__ import annotations

from types import ModuleType
from typing import Any, Mapping

import pytest

from bioimageio.spec import application, dataset, generic, model, notebook

IGNORE_MEMBERS = {
    "ALERT",
    "AfterValidator",
    "Annotated",
    "Any",
    "BioimageioYamlContent",
    "Callable",
    "ClassVar",
    "Converter",
    "CoverImageSource",
    "DeprecatedLicenseId",
    "Dict",
    "EmailStr",
    "FAIR",
    "Field",
    "FilePath",
    "FileSource",
    "Ge",
    "GenericDescr",
    "GenericDescrBase",
    "GenericModelDescrBase",
    "INFO",
    "KNOWN_SPECIFIC_RESOURCE_TYPES",
    "LICENSES",
    "Len",
    "LicenseId",
    "LinkedResourceBase",
    "List",
    "LowerCase",
    "Mapping",
    "MarkdownSource",
    "MaxLen",
    "MinLen",
    "Node",
    "NotEmpty",
    "Optional",
    "PermissiveFileSource",
    "Predicate",
    "ResourceDescrBase",
    "ResourceDescrType",
    "RestrictCharacters",
    "RootModel",
    "S",
    "Self",
    "Sequence",
    "TAG_CATEGORIES",
    "Type",
    "TypeVar",
    "Union",
    "V_suffix",
    "ValidatedString",
    "ValidationInfo",
    "WithSuffix",
    "YamlValue",
    "annotated_types",
    "annotations",
    "as_warning",
    "assert_never",
    "cast",
    "collections",
    "convert_from_older_format",
    "field_validator",
    "get_args",
    "get_validation_context",
    "httpx",
    "include_in_package",
    "include_in_package_serializer",
    "is_dict",
    "is_list",
    "is_mapping",
    "is_sequence",
    "is_yaml_value",
    "issue_warning",
    "model_validator",
    "partial",
    "pydantic",
    "settings",
    "string",
    "v0_2",
    "v0_3",
    "v0_4",
    "v0_5",
    "validate_github_user",
    "validate_suffix",
    "warn",
    "wo_special_file_name",
}


def get_members(m: ModuleType) -> Mapping[str, Any]:
    return {
        k: getattr(m, k)
        for k in dir(m)
        if not k.startswith("_")
        and k not in IGNORE_MEMBERS
        and not k.startswith("FileSource_")  # Annotated[FileSource, ...]
        and not k.startswith("FileDescr_")  # Annotated[FileDescr, ...]
    }


GENERIC_v0_2_MEMBERS = get_members(generic.v0_2)
GENERIC_v0_3_MEMBERS = get_members(generic.v0_3)


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
    generic_members: dict[str, Any], specific: ModuleType
):
    members = get_members(specific)
    missing = {k for k in generic_members if k not in members}
    assert not missing
