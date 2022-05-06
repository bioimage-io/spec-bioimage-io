from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from packaging.version import Version

from bioimageio.spec.shared import raw_nodes
from bioimageio.spec.shared.node_transformer import NodeTransformer, NodeVisitor, iter_fields
from bioimageio.spec.shared.raw_nodes import ResourceDescription


@dataclass
class MyNode(raw_nodes.RawNode):
    field_a: str
    field_b: int


def test_iter_fields():
    entry = MyNode("a", 42)
    assert [("field_a", "a"), ("field_b", 42)] == list(iter_fields(entry))


@dataclass
class Content:
    data: str


class TestNodeVisitor:
    @dataclass
    class Tree(raw_nodes.RawNode):
        left: Any
        right: Any

    @dataclass
    class URL:
        url: str

    @pytest.fixture
    def tree(self):
        return self.Tree(
            self.Tree(self.Tree(None, None), self.URL("https://example.com")),
            self.Tree(None, self.Tree(None, self.Tree(None, None))),
        )

    def test_node(self, tree):
        visitor = NodeVisitor()
        visitor.visit(tree)

    def test_node_transform(self, tree):
        class MyTransformer(NodeTransformer):
            def transform_URL(self, node):
                return Content(f"content of url {node.url}")

        assert isinstance(tree.left.right, self.URL)
        transformer = MyTransformer()
        transformed_tree = transformer.transform(tree)
        assert isinstance(transformed_tree.left.right, Content)


def test_resolve_remote_relative_path():
    from bioimageio.spec.shared.node_transformer import RelativePathTransformer

    remote_rdf = raw_nodes.URI(
        "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/"
        "unet2d_nuclei_broad/rdf.yaml"
    )
    remote_relative_path = Path("unet2d.py")

    uri = RelativePathTransformer(root=remote_rdf.parent).transform(remote_relative_path)

    assert (
        str(uri) == "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/"
        "unet2d_nuclei_broad/unet2d.py"
    )


@pytest.mark.parametrize(
    "data_update_expected",
    [
        ({"a": 1, "b": 2}, {"a": {"c": 1}}, {"a": {"c": 1}, "b": 2}),
        ({"a": [0, 1, 2, 3]}, {"a": [5]}, {"a": [5, 1, 2, 3]}),
        ([0, 1, 2, 3], [5], [5, 1, 2, 3]),
        ([0, {"a": [1]}, 2, 3], ["DROP", {"a": ["KEEP", 2]}], [{"a": [1, 2]}, 2, 3]),
        (
            ResourceDescription(
                format_version="0.1.0",
                name="resource",
                type="test",
                version=Version("0.1.0"),
            ),
            {"name": "updated resource"},
            ResourceDescription(
                format_version="0.1.0",
                name="updated resource",
                type="test",
                version=Version("0.1.0"),
            ),
        ),
    ],
)
def test_update_nested(data_update_expected):
    from bioimageio.spec.shared import update_nested

    data, update, expected = data_update_expected
    actual = update_nested(data, update)
    assert actual == expected
