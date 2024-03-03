from typing import Any


def test_converter_with_arg():
    from bioimageio.spec._internal.common_nodes import Converter, Node

    class A(Node):
        a: int

    class B(Node):
        b: str

    class AtoB(Converter[A, B, str]):
        def _convert(
            self, src: A, tgt: "type[B] | type[dict[str, Any]]", /, prefix: str
        ) -> "B | dict[str, Any]":
            return tgt(b=prefix + str(src.a))

    converter = AtoB(A, B)

    _ = converter.convert(A(a=5), "prefix")
