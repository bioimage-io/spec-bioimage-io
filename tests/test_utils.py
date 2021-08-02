from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from bioimageio.spec.shared import nodes, raw_nodes, utils


@dataclass
class MyNode(nodes.Node):
    field_a: str
    field_b: int


def test_iter_fields():
    entry = MyNode("a", 42)
    assert [("field_a", "a"), ("field_b", 42)] == list(utils.iter_fields(entry))


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
        visitor = utils.NodeVisitor()
        visitor.visit(tree)

    def test_node_transform(self, tree):
        class MyTransformer(utils.NodeTransformer):
            def transform_URL(self, node):
                return Content(f"content of url {node.url}")

        assert isinstance(tree.left.right, self.URL)
        transformer = MyTransformer()
        transformed_tree = transformer.transform(tree)
        assert isinstance(transformed_tree.left.right, Content)


def test_resolve_remote_relative_path():
    from bioimageio.spec.shared.utils import PathToRemoteUriTransformer

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


def test_resolve_import_path(tmpdir):
    tmpdir = Path(tmpdir)
    manifest_path = tmpdir / "manifest.yaml"
    manifest_path.touch()
    source_file = raw_nodes.URI(path="my_mod.py")
    (tmpdir / str(source_file)).write_text("class Foo: pass", encoding="utf8")
    node = raw_nodes.ImportableSourceFile(source_file=source_file, callable_name="Foo")
    uri_transformed = utils.UriNodeTransformer(root_path=tmpdir).transform(node)
    source_transformed = utils.SourceNodeTransformer().transform(uri_transformed)
    assert isinstance(source_transformed, nodes.ImportedSource)
    Foo = source_transformed.factory
    assert Foo.__name__ == "Foo"
    assert isinstance(Foo, type)


def test_resolve_directory_uri(tmpdir):
    node = raw_nodes.URI(Path(tmpdir).as_uri())
    uri_transformed = utils.UriNodeTransformer(root_path=Path(tmpdir)).transform(node)
    assert uri_transformed == Path(tmpdir)


def test_uri_available():
    pass


def test_all_uris_available():
    from bioimageio.spec.shared.utils import all_uris_available

    not_available = {
        "uri": raw_nodes.URI(path="non_existing_file_in/non_existing_dir/ftw"),
        "uri_exists": raw_nodes.URI(path="."),
    }
    assert not all_uris_available(not_available)
