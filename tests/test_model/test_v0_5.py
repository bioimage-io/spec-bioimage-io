from pathlib import Path

from bioimageio.spec.model.v0_5 import InputTensor, ModelRdf, TensorBase
from bioimageio.spec.shared.types import RelativeFilePath
from bioimageio.spec.shared.validation import ValContext
from tests.unittest_utils import Invalid, TestBases, Valid


class TestModelRdf(TestBases.TestNode):
    default_node_class = ModelRdf
    sub_tests = [
        Valid(
            dict(rdf_source=__file__, sha256="s" * 64),
            expected_dump_raw=dict(rdf_source=__file__, sha256="s" * 64),
            expected_dump_python=dict(rdf_source=RelativeFilePath(__file__), sha256="s" * 64),
            context=ValContext(root=Path()),
        ),
        Invalid(dict(uri="https://example.com", sha256="s" * 64)),
        Invalid(dict(id="lala", uri="https://example.com", sha256="s" * 64)),
        Invalid(dict(url="https://example.com", sha256="s" * 64)),
    ]


class TestTensorBase(TestBases.TestNode):
    default_node_class = TensorBase
    sub_tests = [
        Valid(
            dict(
                name="t1",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data={"values": ["cat", "dog", "parrot"]},
            )
        ),
        Valid(
            dict(
                name="t2",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["cat", "dog", "parrot"]},
                    {"values": ["mouse", "zebra", "elephant"]},
                ],
            )
        ),
        Valid(
            dict(
                name="t3",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": [1, 2, 3]},
                    {"type": "uint8"},
                ],
            )
        ),
        Valid(
            dict(
                name="t4",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["mouse", "zebra", "elephant"]},
                    {"type": "uint8"},
                ],
            ),
            name="string values and uint data type",
        ),
        Invalid(
            dict(
                name="t4",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["mouse", "zebra", "elephant"]},
                    {"type": "int8"},
                ],
            ),
            name="string values and int data type",
        ),
        Invalid(
            dict(
                name="t5",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["cat", "dog", "parrot"]},
                    {"values": [1.1, 2.2, 3.3]},
                ],
            ),
            name="str and float values",
        ),
        Invalid(
            dict(
                name="t6",
                axes=[{"type": "channel", "channel_names": ["a", "b", "c"]}],
                test_tensor="https://example.com/test.npy",
                data=[
                    {"values": ["cat", "dog", "parrot"]},
                    {"values": ["mouse", "zebra", "elephant"]},
                ],
            ),
            name="channel mismatch",
        ),
    ]


class TestInputTensor(TestBases.TestNode):
    default_node_class = InputTensor
    sub_tests = [
        Valid(
            {
                "name": "input_1",
                "description": "Input 1",
                "data": {"type": "float32"},
                "axes": [
                    dict(type="space", name="x", size=10),
                    dict(type="space", name="y", size=11),
                    dict(type="channel", channel_names=tuple("abc")),
                ],
                "preprocessing": [
                    {
                        "name": "scale_range",
                        "kwargs": {"max_percentile": 99, "min_percentile": 5, "mode": "per_sample", "axes": ("x", "y")},
                    }
                ],
                "test_tensor": "https://example.com/test.npy",
            }
        ),
    ]
