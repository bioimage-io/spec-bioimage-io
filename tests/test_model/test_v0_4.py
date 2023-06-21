from pydantic import HttpUrl
from bioimageio.spec.model.v0_4 import ModelParent
from bioimageio.spec.shared.types_custom import RelativeFilePath
from tests.unittest_utils import BaseTestCases


class TestGenericDescription(BaseTestCases.TestNode):
    NodeClass = ModelParent
    valid_kwargs = [
        dict(id="lala"),
        dict(rdf_source=__file__),
        dict(uri="https://example.com"),
    ]
    expected_dump_python = [
        dict(id="lala"),
        dict(rdf_source=RelativeFilePath(__file__)),
        dict(rdf_source=HttpUrl("https://example.com")),
    ]
    expected_dump_raw = [
        dict(id="lala"),
        dict(rdf_source=__file__),
        dict(rdf_source="https://example.com"),
    ]
    invalid_kwargs = [
        dict(id="lala", uri="https://example.com"),
        dict(url="https://example.com"),
    ]
