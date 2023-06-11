from __future__ import annotations
from pathlib import Path
import unittest
from pydantic import HttpUrl
from bioimageio.spec.rdf.v0_2.nodes import Attachments, Author, CiteEntry, RdfBase
from bioimageio.spec.rdf.v0_2.nodes import Maintainer

from bioimageio.spec.shared.fields import RelativePath

from tests.unittest_utils import BaseTestCases


class TestAttachments(BaseTestCases.TestNode):
    NodeClass = Attachments
    valid_kwargs = [
        dict(files=(RelativePath(__file__), HttpUrl("https://example.com")), another_attachment=5),
        dict(files=(__file__, "https://example.com"), extra=dict(more="of this")),
        dict(files=(__file__, "http:example.com")),
        dict(only="other stuff"),
    ]
    invalid_kwargs = [dict(files=__file__), dict(files=(__file__, "example.com")), dict(files=(123,))]


class TestAuthor(BaseTestCases.TestNode):
    NodeClass = Author
    valid_kwargs = [
        dict(name="only_name"),
        dict(
            name="Me", affiliation="Paradise", email="me@example.com", github_user="ghuser", orcid="0000-0001-2345-6789"
        ),
    ]
    invalid_kwargs = [
        dict(affiliation="Paradise", email="me@example.com", github_user="ghuser", orcid="0000-0001-2345-6789"),
        dict(
            name="Me", affiliation="Paradise", email="me@example.com", github_user="ghuser", orcid="0000-0001-2345-6788"
        ),
        dict(name=5),
    ]


class TestMaintainer(BaseTestCases.TestNode):
    NodeClass = Maintainer
    valid_kwargs = [
        dict(github_user="ghuser_only"),
        dict(
            name="Me", affiliation="Paradise", email="me@example.com", github_user="ghuser", orcid="0000-0001-2345-6789"
        ),
    ]
    invalid_kwargs = [
        dict(name="only_name"),
        dict(github_user=5.5),
    ]


class TestCiteEntry(BaseTestCases.TestNode):
    NodeClass = CiteEntry
    valid_kwargs = [dict(text="lala", url="https://example.com"), dict(text="lala", doi="10.1234fakedoi")]
    invalid_kwargs = [dict(text="lala"), dict(url="https://example.com")]


class TestRdfBase(BaseTestCases.TestNode):
    NodeClass = RdfBase
    context = None
    valid_kwargs = [
        dict(root=Path(__file__).parent, format_version="0.2.0", version="0.1.0", type="my_type", name="my name")
    ]
