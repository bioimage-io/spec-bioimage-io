from pathlib import Path

from pydantic import HttpUrl

from bioimageio.spec.model.v0_5 import ModelRdf, TensorBase
from bioimageio.spec.shared.types import RelativeFilePath
from bioimageio.spec.shared.validation import ValidationContext
from tests.unittest_utils import BaseTestCases, Invalid, Valid


class TestModelRdf(BaseTestCases.TestNode):
    default_node_class = ModelRdf
    sub_tests = [
        Valid(
            dict(rdf_source=__file__, sha256="s" * 64),
            expected_dump_raw=dict(rdf_source=__file__, sha256="s" * 64),
            expected_dump_python=dict(rdf_source=RelativeFilePath(__file__, root=Path()), sha256="s" * 64),
            context=ValidationContext(root=Path()),
        ),
        Invalid(dict(uri="https://example.com", sha256="s" * 64)),
        Invalid(dict(id="lala", uri="https://example.com", sha256="s" * 64)),
        Invalid(dict(url="https://example.com", sha256="s" * 64)),
    ]


class TestTensorBase(BaseTestCases.TestNode):
    default_node_class = TensorBase
    sub_tests = [
        Valid(
            dict(
                name="tensor",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                values={"type": "nominal", "values": ["cat", "dog", "parrot"]},
            )
        ),
        Valid(
            dict(
                name="tensor",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                values=[
                    {"type": "nominal", "values": ["cat", "dog", "parrot"]},
                    {"type": "ordinal", "values": ["mouse", "zebra", "elephant"]},
                ],
            )
        ),
        Valid(
            dict(
                name="tensor",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                values=[
                    {"type": "ordinal", "values": [1, 2, 3]},
                    {"type": "interval", "data_type": "uint8"},
                ],
            )
        ),
        Invalid(
            dict(
                name="tensor",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                values=[
                    {"type": "ordinal", "values": ["mouse", "zebra", "elephant"]},
                    {"type": "interval", "data_type": "uint8"},
                ],
            ),
            name="string values and int data type",
        ),
        Invalid(
            dict(
                name="tensor",
                axes=[{"type": "channel", "channel_names": ["a", "b"]}],
                test_tensor="https://example.com/test.npy",
                values=[
                    {"type": "nominal", "values": ["cat", "dog", "parrot"]},
                    {"type": "ordinal", "values": [1, 2, 3]},
                ],
            ),
            name="str and int values",
        ),
        Invalid(
            dict(
                name="tensor",
                axes=[{"type": "channel", "channel_names": ["a", "b", "c"]}],
                test_tensor="https://example.com/test.npy",
                values=[
                    {"type": "nominal", "values": ["cat", "dog", "parrot"]},
                    {"type": "ordinal", "values": ["mouse", "zebra", "elephant"]},
                ],
            ),
            name="channel mismatch",
        ),
    ]
