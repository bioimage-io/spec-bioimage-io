from typing import Any


def test_converter_with_kwargs():
    from bioimageio.spec._internal.base_nodes import ConverterWithKwargs, Node

    class A(Node):
        a: int

    class B(Node):
        b: str

    class AtoB(ConverterWithKwargs[A, B, [str]]):
        def _convert(self, src: A, tgt: "type[B] | type[dict[str, Any]]", /, prefix: str) -> "B | dict[str, Any]":
            return tgt(b=prefix + str(src.a))

    converter = AtoB(A, B)

    converter.convert(A(a=5))
