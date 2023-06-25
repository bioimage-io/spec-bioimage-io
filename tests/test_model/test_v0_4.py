from pathlib import Path

from pydantic import HttpUrl

from bioimageio.spec.model.v0_4 import ModelRdf, LinkedModel, OnnxEntry
from bioimageio.spec.shared.types import RelativeFilePath
from bioimageio.spec.shared.validation import WARNINGS_ACTION_KEY
from tests.unittest_utils import BaseTestCases, Invalid, Valid


class TestModelRdf(BaseTestCases.TestNode):
    default_node_class = ModelRdf
    sub_tests = [
        Valid(
            dict(rdf_source=__file__, sha256="s" * 64),
            expected_dump_raw=dict(rdf_source=__file__, sha256="s" * 64),
            expected_dump_python=dict(rdf_source=RelativeFilePath(__file__, root=Path()), sha256="s" * 64),
            context=dict(root=Path()),
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
        Invalid(
            dict(opset_version=5, source="https://example.com", sha256="s" * 64), context={WARNINGS_ACTION_KEY: "raise"}
        ),
        Invalid(
            dict(source="https://example.com", sha256="s"),
        ),
    ]
