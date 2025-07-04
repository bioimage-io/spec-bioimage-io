"""utils to test bioimageio.spec"""

import os
from contextlib import nullcontext
from copy import deepcopy
from io import StringIO
from pathlib import Path
from typing import (
    Any,
    Collection,
    ContextManager,
    Dict,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Type,
    Union,
)
from zipfile import ZipFile

import jsonschema
import pytest
from deepdiff.diff import DeepDiff
from pydantic import (
    DirectoryPath,
    RootModel,
    TypeAdapter,
    ValidationError,
    create_model,
)

from bioimageio.spec import InvalidDescr, ValidationContext, build_description
from bioimageio.spec._internal.common_nodes import Node
from bioimageio.spec._internal.io_utils import open_bioimageio_yaml, read_yaml
from bioimageio.spec._internal.root_url import RootHttpUrl
from bioimageio.spec._internal.type_guards import is_kwargs
from bioimageio.spec.application.v0_2 import ApplicationDescr as ApplicationDescr02
from bioimageio.spec.common import HttpUrl, Sha256
from bioimageio.spec.dataset.v0_2 import DatasetDescr as DatasetDescr02
from bioimageio.spec.generic._v0_2_converter import DOI_PREFIXES
from bioimageio.spec.generic.v0_2 import GenericDescr as GenericDescr02
from bioimageio.spec.model.v0_4 import ModelDescr as ModelDescr04
from bioimageio.spec.notebook.v0_2 import NotebookDescr as NotebookDescr02

unset = object()

expensive_test = pytest.mark.skipif(
    (run := os.getenv("RUN_EXPENSIVE_TESTS")) != "true",
    reason="Skipping expensive test (enable by RUN_EXPENSIVE_TESTS='true')",
)


def check_node(
    node_class: Type[Node],
    kwargs: Union[Dict[str, Any], Node],
    *,
    context: Optional[ValidationContext] = None,
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
            context=context or ValidationContext(root=Path(__file__).parent),
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
    type_: Union[Any, Type[Any]],
    value: Any,
    expected: Any = unset,
    expected_root: Any = unset,
    expected_deserialized: Any = unset,
    *,
    is_invalid: bool = False,
):
    type_adapter = TypeAdapter(type_)
    error_context: ContextManager = pytest.raises(ValidationError) if is_invalid else nullcontext()  # type: ignore

    with error_context:
        actual = type_adapter.validate_python(value)

    if expected is not unset:
        assert actual == expected, (actual, expected)

    if expected_root is not unset:
        assert isinstance(actual, RootModel)
        assert actual.root == expected_root, (actual.root, expected_root)

    if expected_deserialized is not unset:
        actual_deserialized = type_adapter.dump_python(
            actual, mode="json", exclude_unset=True
        )
        assert actual_deserialized == expected_deserialized, (
            actual_deserialized,
            expected_deserialized,
        )

    node = create_model("DummyNode", value=(type_, ...), __base__=DummyNodeBase)
    with error_context:
        actual_node = node.model_validate(dict(value=value))

    if expected is not unset:
        assert actual_node.value == expected, (actual_node.value, expected)

    if expected_root is not unset:
        assert isinstance(actual_node.value, RootModel)
        assert actual_node.value.root == expected_root, (
            actual_node.value.root,
            expected_root,
        )

    if expected_deserialized is not unset:
        node_deserialized = actual_node.model_dump(mode="json", exclude_unset=True)
        assert node_deserialized["value"] == expected_deserialized, (
            node_deserialized["value"],
            expected_deserialized,
        )


def check_bioimageio_yaml(
    source: Union[Path, HttpUrl],
    /,
    *,
    sha: Optional[Sha256] = None,
    root: Union[RootHttpUrl, DirectoryPath, ZipFile] = Path(),
    as_latest: bool,
    exclude_fields_from_roundtrip: Collection[str] = set(),
    is_invalid: bool = False,
    bioimageio_json_schema: Optional[Mapping[Any, Any]],
    perform_io_checks: bool = True,
) -> None:
    opened_yaml = open_bioimageio_yaml(source, sha256=sha)
    root = opened_yaml.original_root
    raw = opened_yaml.unparsed_content
    assert isinstance(raw, str)
    data = read_yaml(StringIO(raw))
    assert is_kwargs(data), type(data)
    format_version = "latest" if as_latest else "discover"
    with ValidationContext(
        root=root,
        file_name=opened_yaml.original_file_name,
        perform_io_checks=perform_io_checks,
    ):
        rd = build_description(deepcopy(data), format_version=format_version)
        assert not is_invalid or (
            is_invalid and isinstance(rd, InvalidDescr)
        ), "Invalid RDF passed validation"

    summary = rd.validation_summary
    assert summary is not None
    if is_invalid:
        assert summary.status == "failed", "passes despite marked as known failure case"
        assert isinstance(rd, InvalidDescr)
        return

    assert summary.status == "valid-format", summary.display()
    assert rd is not None

    json_data = rd.model_dump(mode="json")
    # check compatibility to our latest json schema...
    if bioimageio_json_schema is not None:
        try:
            jsonschema.validate(json_data, bioimageio_json_schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"jsonschema validation error for {source}") from e

    if as_latest:
        return

    # check rountrip
    exclude_from_comp = {
        "format_version",
        "timestamp",
        *exclude_fields_from_roundtrip,
    }
    if isinstance(
        rd,
        (
            ModelDescr04,
            ApplicationDescr02,
            DatasetDescr02,
            GenericDescr02,
            NotebookDescr02,
        ),
    ):
        # these fields may intentionally be manipulated
        exclude_from_comp |= {"version_number", "id_emoji", "id"}

    deserialized = rd.model_dump(
        mode="json", exclude=exclude_from_comp, exclude_unset=True
    )
    expect_back = {k: v for k, v in data.items() if k not in exclude_from_comp}
    assert_rdf_dict_equal(
        deserialized, expect_back, f"roundtrip {source}\n", ignore_known_rdf_diffs=True
    )


def assert_rdf_dict_equal(
    actual: Dict[Any, Any],
    expected: Dict[Any, Any],
    msg: str = "",
    *,
    ignore_known_rdf_diffs: bool = False,
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


WARNING_LEVEL_CONTEXT_KEY = "warning_level"
