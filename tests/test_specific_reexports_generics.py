from types import ModuleType
from typing import Any, Dict, Mapping

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
    "Callable",
    "cast",
    "ClassVar",
    "collections",
    "convert_from_older_format",
    "Converter",
    "CoverImageSource",
    "DeprecatedLicenseId",
    "Dict",
    "EmailStr",
    "FAIR",
    "field_validator",
    "Field",
    "FilePath",
    "FileSource",
    "Ge",
    "GenericDescr",
    "GenericDescrBase",
    "GenericModelDescrBase",
    "get_args",
    "get_validation_context",
    "httpx",
    "include_in_package_serializer",
    "include_in_package",
    "INFO",
    "is_dict",
    "is_sequence",
    "is_yaml_value",
    "issue_warning",
    "KNOWN_SPECIFIC_RESOURCE_TYPES",
    "Len",
    "LicenseId",
    "LICENSES",
    "LinkedResourceBase",
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
    "pydantic",
    "ResourceDescrBase",
    "ResourceDescrType",
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
    "validate_github_user",
    "validate_suffix",
    "ValidatedString",
    "ValidationInfo",
    "warn",
    "WithSuffix",
    "wo_special_file_name",
    "YamlValue",
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
    generic_members: Dict[str, Any], specific: ModuleType
):
    members = get_members(specific)
    missing = {k for k in generic_members if k not in members}
    assert not missing
