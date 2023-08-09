import platform
from pathlib import Path

import pytest

from bioimageio.spec.dataset.raw_nodes import Dataset
from bioimageio.spec.shared import yaml


# todo: fix test on windows
@pytest.mark.skipif(
    platform.system() == "Windows", reason="OSError: [WinError 1314] A required privilege is not held by the client"
)
def test_serialize_with_link_in_path(dataset_rdf, tmp_path: Path):
    from bioimageio.spec import load_raw_resource_description, serialize_raw_resource_description_to_dict

    data = load_raw_resource_description(dataset_rdf)
    assert isinstance(data, Dataset)
    true_root = tmp_path / "root"
    true_root.mkdir()
    linked_root = tmp_path / "link"
    linked_root.symlink_to(true_root, target_is_directory=True)

    doc_path = linked_root / "docs.md"
    doc_path.write_text("# Documentation")

    data.root_path = true_root
    data.documentation = doc_path  # doc path only in root through link

    serialized = serialize_raw_resource_description_to_dict(data, convert_absolute_paths=True)
    assert serialized["documentation"] == "docs.md"


# todo: fix test on windows
@pytest.mark.skipif(
    platform.system() == "Windows", reason="OSError: [WinError 1314] A required privilege is not held by the client"
)
def test_serialize_with_link_in_root(dataset_rdf, tmp_path: Path):
    from bioimageio.spec import load_raw_resource_description, serialize_raw_resource_description_to_dict

    data = load_raw_resource_description(dataset_rdf)
    assert isinstance(data, Dataset)

    true_root = tmp_path / "root"
    true_root.mkdir()
    linked_root = tmp_path / "link"
    linked_root.symlink_to(true_root, target_is_directory=True)

    doc_path = true_root / "docs.md"
    doc_path.write_text("# Documentation")

    data.root_path = linked_root  # root path is symlink to true root
    data.documentation = doc_path

    serialized = serialize_raw_resource_description_to_dict(data, convert_absolute_paths=True)
    assert serialized["documentation"] == "docs.md"
