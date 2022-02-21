from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from bioimageio.spec.shared import raw_nodes
from bioimageio.spec.shared.node_transformer import NodeTransformer, NodeVisitor, iter_fields


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
    from bioimageio.spec.shared.node_transformer import PathToRemoteUriTransformer

    remote_rdf = raw_nodes.URI(
        "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/"
        "unet2d_nuclei_broad/rdf.yaml"
    )
    remote_relative_path = Path("unet2d.py")

    uri = PathToRemoteUriTransformer(remote_source=remote_rdf).transform(remote_relative_path)

    assert (
        str(uri) == "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/"
        "unet2d_nuclei_broad/unet2d.py"
    )
