from pathlib import Path

from pydantic import HttpUrl

from bioimageio.spec.model.v0_4 import LinkedModel, ModelRdf, OnnxEntry, ScaleLinearKwargs
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
        Valid(
            dict(uri="https://example.com", sha256="s" * 64),
            expected_dump_raw=dict(rdf_source="https://example.com/", sha256="s" * 64),
            expected_dump_python=dict(rdf_source=HttpUrl("https://example.com/"), sha256="s" * 64),
        ),
        Invalid(dict(id="lala", uri="https://example.com", sha256="s" * 64)),
        Invalid(dict(url="https://example.com", sha256="s" * 64)),
    ]


class TestLinkedModel(BaseTestCases.TestNode):
    default_node_class = LinkedModel
    sub_tests = [
        Valid(dict(id="lala"), expected_dump_raw=dict(id="lala"), expected_dump_python=dict(id="lala")),
        Invalid(dict(id="lala", uri="https://example.com")),
        Invalid(dict(url="https://example.com")),
    ]


class TestOnnxEntry(BaseTestCases.TestNode):
    default_node_class = OnnxEntry
    sub_tests = [
        Valid(
            dict(type="onnx", opset_version=8, source="https://example.com", sha256="s" * 64),
            expected_dump_raw=dict(opset_version=8, source="https://example.com/", sha256="s" * 64),
        ),
        Valid(
            dict(opset_version=8, source="https://example.com", sha256="s" * 64),
            expected_dump_raw=dict(opset_version=8, source="https://example.com/", sha256="s" * 64),
        ),
        Valid(
            dict(source="https://example.com", sha256="s" * 64),
            expected_dump_raw=dict(source="https://example.com/", sha256="s" * 64),
        ),
        Invalid(dict(opset_version=5, source="https://example.com", sha256="s" * 64)),
        Invalid(
            dict(source="https://example.com", sha256="s"),
        ),
    ]


class TestScaleLinearKwargs(BaseTestCases.TestNode):
    default_node_class = ScaleLinearKwargs
    sub_tests = [
        Valid(dict(axes="xy", gain=2.0, offset=0.5)),
        Valid(dict(offset=2.0)),
        Valid(dict(gain=2.0)),
        Valid(dict(axes="xy", gain=[1.0, 2.0], offset=[0.5, 0.3])),
        Valid(dict(gain=2.0, offset=0.5)),
        Invalid(dict(), name="empty kwargs"),
        Invalid(dict(gain=1.0)),
        Invalid(dict(offset=0.0)),
    ]
