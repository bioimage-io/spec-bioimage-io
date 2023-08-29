from contextlib import nullcontext
from copy import deepcopy
from pathlib import Path
from typing import Any, ContextManager, Dict, Optional, Protocol, Sequence, Set, Type, Union

import pytest
from deepdiff import DeepDiff  # type: ignore
from pydantic import AnyUrl, TypeAdapter, ValidationError, create_model
from ruamel.yaml import YAML

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.field_validation import get_validation_context
from bioimageio.spec.description import load_description
from bioimageio.spec.generic.v0_2_converter import DOI_PREFIXES
from bioimageio.spec.types import ValidationContext

yaml = YAML(typ="safe")


class not_set:
    pass


def check_node(
    node_class: Type[Node],
    kwargs: Union[Dict[str, Any], Node],
    *,
    context: Optional[ValidationContext] = None,
    expected_dump_json: Any = not_set,
    expected_dump_python: Any = not_set,
    is_invalid: bool = False,
):
    if is_invalid:
        assert expected_dump_json is not_set
        assert expected_dump_python is not_set

    error_context: ContextManager = pytest.raises(ValidationError) if is_invalid else nullcontext()  # type: ignore
    with error_context:
        node = node_class.model_validate(
            kwargs, context=dict(get_validation_context(**(context or {"root": Path(__file__).parent})))
        )

    if expected_dump_json is not not_set:
        actual = node.model_dump(mode="json")
        assert actual, expected_dump_json

    if expected_dump_python is not not_set:
        actual = node.model_dump(mode="python")
        assert actual, expected_dump_python


class DummyNodeBase(Node):
    value: Any


def check_type(type_: Type[Any], value: Any, expected: Any = not_set, *, is_invalid: bool = False):
    type_adapter = TypeAdapter(type_)
    error_context: ContextManager = pytest.raises(ValidationError) if is_invalid else nullcontext()  # type: ignore

    with error_context:
        actual = type_adapter.validate_python(value)

    if not (is_invalid or expected is not_set):
        assert actual == expected

    node = create_model("DummyNode", value=(type_, ...), __base__=DummyNodeBase)
    with error_context:
        actual_in_node = node.model_validate(dict(value=value)).value

    if not (is_invalid or expected is not_set):
        assert actual_in_node == expected


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
        rd, _ = load_description(data, context=context)
        assert rd is None, "Invalid RDF passed validation"

    exclude_from_comp = {
        "format_version",
        "timestamp",
        *exclude_fields_from_roundtrip,
    }

    format_version = "latest" if as_latest else "discover"
    expect_back = {k: v for k, v in data.items() if k not in exclude_from_comp}
    rd, summary = load_description(data, context=context, format_version=format_version)

    if is_invalid:
        assert summary.status == "failed", "passes despite marked as known failure case"
        assert rd is None
        return

    assert summary.status == "passed", summary.format()
    assert rd is not None

    if as_latest:
        return

    deserialized = rd.model_dump(mode="json", exclude=exclude_from_comp, exclude_unset=True)
    diff: Any = DeepDiff(expect_back, deserialized)
    if not diff:
        return

    # ignore some known differences...
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

    assert not slim_diff, f"roundtrip {rdf_path.as_posix()}\n" + slim_diff.pretty()


class ParameterSet(Protocol):
    def __init__(self, values: Sequence[Any], marks: Any, id: str) -> None:
        super().__init__()
