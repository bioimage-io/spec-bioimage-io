from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

from bioimageio.spec import load_raw_model, nodes, raw_nodes
from bioimageio.spec.shared import transformers

yaml = YAML(typ="safe")


@dataclass
class MyNode(nodes.Node):
    field_a: str
    field_b: int


def test_iter_fields():
    entry = MyNode("a", 42)
    assert [("field_a", "a"), ("field_b", 42)] == list(transformers.iter_fields(entry))


@dataclass
class Content:
    data: str


class TestNodeVisitor:
    @dataclass
    class Tree(nodes.Node):
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
        visitor = transformers.NodeVisitor()
        visitor.visit(tree)

    def test_node_transform(self, tree):
        class MyTransformer(transformers.NodeTransformer):
            def transform_URL(self, node):
                return Content(f"content of url {node.url}")

        assert isinstance(tree.left.right, self.URL)
        transformer = MyTransformer()
        transformed_tree = transformer.transform(tree)
        assert isinstance(transformed_tree.left.right, Content)


def test_resolve_import_path(tmpdir):
    tmpdir = Path(tmpdir)
    manifest_path = tmpdir / "manifest.yaml"
    manifest_path.touch()
    filepath = tmpdir / "my_mod.py"
    filepath.write_text("class Foo: pass", encoding="utf8")
    node = raw_nodes.ImportablePath(filepath=filepath, callable_name="Foo")
    uri_transformed = transformers.UriNodeTransformer(root_path=tmpdir).transform(node)
    source_transformed = transformers.SourceNodeTransformer().transform(uri_transformed)
    assert isinstance(source_transformed, nodes.ImportedSource)
    Foo = source_transformed.factory
    assert Foo.__name__ == "Foo"
    assert isinstance(Foo, type)


def test_resolve_directory_uri(tmpdir):
    node = raw_nodes.URI(scheme="", authority="", path=str(tmpdir), query="", fragment="")
    uri_transformed = transformers.UriNodeTransformer(root_path=Path(tmpdir)).transform(node)
    assert uri_transformed == Path(tmpdir)


def test_load_raw_model(rf_config_path):
    rf_model_data = yaml.load(rf_config_path)
    load_raw_model(rf_model_data)
