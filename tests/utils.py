from contextlib import nullcontext
from copy import deepcopy
from pathlib import Path
from typing import Any, ContextManager, Dict, Protocol, Sequence, Set, Type, Union

import pytest
from deepdiff import DeepDiff
from pydantic import AnyUrl, TypeAdapter, ValidationError, create_model
from ruamel.yaml import YAML

from bioimageio.spec._description import InvalidDescription, build_description
from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.validation_context import (
    InternalValidationContext,
    ValidationContext,
    get_internal_validation_context,
)
from bioimageio.spec.generic.v0_2_converter import DOI_PREFIXES

yaml = YAML(typ="safe")


unset = object()


def check_node(
    node_class: Type[Node],
    kwargs: Union[Dict[str, Any], Node],
    *,
    context: Union[ValidationContext, InternalValidationContext, None] = None,
    expected_dump_json: Any = unset,
    expected_dump_python: Any = unset,
    is_invalid: bool = False,
):
    if is_invalid:
        assert expected_dump_json is unset
        assert expected_dump_python is unset

    error_context: ContextManager = pytest.raises(ValidationError) if is_invalid else nullcontext()  # type: ignore
    with error_context:
        node = node_class.model_validate(
            kwargs,
            context=dict(get_internal_validation_context(context or ValidationContext(root=Path(__file__).parent))),
        )

    if expected_dump_json is not unset:
        actual = node.model_dump(mode="json")
        assert actual, expected_dump_json

    if expected_dump_python is not unset:
        actual = node.model_dump(mode="python")
        assert actual, expected_dump_python


class DummyNodeBase(Node):
    value: Any


def check_type(
    type_: Type[Any], value: Any, expected: Any = unset, expected_deserialized: Any = unset, *, is_invalid: bool = False
):
    type_adapter = TypeAdapter(type_)
    error_context: ContextManager = pytest.raises(ValidationError) if is_invalid else nullcontext()  # type: ignore

    with error_context:
        actual = type_adapter.validate_python(value)

    if expected is not unset:
        assert actual == expected, (actual, expected)

    if expected_deserialized is not unset:
        actual_deserialized = type_adapter.dump_python(actual, mode="json", exclude_unset=True)
        assert actual_deserialized == expected_deserialized, (actual_deserialized, expected_deserialized)

    node = create_model("DummyNode", value=(type_, ...), __base__=DummyNodeBase)
    with error_context:
        actual_node = node.model_validate(dict(value=value))

    if expected is not unset:
        assert actual_node.value == expected, (actual_node.value, expected)

    if expected_deserialized is not unset:
        node_deserialized = actual_node.model_dump(mode="json", exclude_unset=True)
        assert node_deserialized["value"] == expected_deserialized, (node_deserialized["value"], expected_deserialized)


def check_rdf(
    root_path: Union[Path, AnyUrl],
    rdf_path: Path,
    as_latest: bool,
    exclude_fields_from_roundtrip: Set[str] = set(),
    *,
    is_invalid: bool = False,
) -> None:
    with rdf_path.open(encoding="utf-8") as f:
        data = yaml.load(f)

    context = ValidationContext(root=root_path, file_name=rdf_path.name)
    if is_invalid:
        rd = build_description(data, context=context)
        assert isinstance(rd, InvalidDescription), "Invalid RDF passed validation"

    exclude_from_comp = {
        "format_version",
        "timestamp",
        *exclude_fields_from_roundtrip,
    }

    format_version = "latest" if as_latest else "discover"
    expect_back = {k: v for k, v in data.items() if k not in exclude_from_comp}
    rd = build_description(data, context=context, format_version=format_version)
    summary = rd.validation_summaries[0]
    if is_invalid:
        assert summary.status == "failed", "passes despite marked as known failure case"
        assert isinstance(rd, InvalidDescription)
        return

    assert summary.status == "passed", summary.format()
    assert rd is not None

    if as_latest:
        return

    deserialized = rd.model_dump(mode="json", exclude=exclude_from_comp, exclude_unset=True)
    assert_dict_equal(deserialized, expect_back, f"roundtrip {rdf_path.as_posix()}\n", ignore_known_rdf_diffs=True)


def assert_dict_equal(
    actual: Dict[Any, Any], expected: Dict[Any, Any], msg: str = "", *, ignore_known_rdf_diffs: bool = False
):
    diff: Any = DeepDiff(expected, actual)
    if ignore_known_rdf_diffs:
        slim_diff = deepcopy(diff)
        VC = "values_changed"
        k: Any
        for k in diff.get(VC, {}):
            if (
                isinstance(k, str)
                and k.startswith("root['cite'][")
                and k.endswith("]['doi']")
                and any(diff[VC][k]["old_value"].startswith(dp) for dp in DOI_PREFIXES)
            ):
                # 1. we dop 'https://doi.org/' from cite.i.doi field
                slim_diff[VC].pop(k)

        if VC in slim_diff and not slim_diff[VC]:
            slim_diff.pop(VC)

        diff = slim_diff

    assert not diff, msg + diff.pretty()


class ParameterSet(Protocol):
    def __init__(self, values: Sequence[Any], marks: Any, id: str) -> None:
        super().__init__()
