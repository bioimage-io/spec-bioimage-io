from __future__ import annotations

from pathlib import Path

from pydantic import HttpUrl

from bioimageio.spec.generic.v0_2 import (
    LATEST_FORMAT_VERSION,
    Attachments,
    Author,
    CiteEntry,
    GenericDescription,
    Maintainer,
)
from bioimageio.spec.shared.types_custom import RelativeFilePath
from tests.unittest_utils import BaseTestCases


class TestAttachments(BaseTestCases.TestNode):
    NodeClass = Attachments
    valid_kwargs = [
        dict(files=(RelativeFilePath(__file__), HttpUrl("https://example.com")), another_attachment=5),
        dict(files=(__file__, "https://example.com"), extra=dict(more="of this")),
        dict(files=(__file__, "http:example.com")),
        dict(only="other stuff"),
    ]
    invalid_kwargs = [
        dict(files=__file__),
        dict(files=["non-existing-file"]),
        dict(files=[123]),
    ]


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


class TestGenericDescription(BaseTestCases.TestNode):
    NodeClass = GenericDescription
    context = None
    valid_kwargs = [
        dict(
            format_version=LATEST_FORMAT_VERSION,
            name="my name",
            description="my description",
            authors=[{"name": "Me"}],
            root=Path(__file__).parent,
            type="my_type",
            version="0.1.0",
        ),
        dict(
            format_version=LATEST_FORMAT_VERSION,
            name="your name",
            description="my description",
            attachments={"files": [Path(__file__)], "something": 42},
            authors=[{"name": "Me"}],
            root="https://example.com",
            type="my_type",
            version="0.1.0",
        ),
    ]
    invalid_kwargs = [
        dict(format_version=LATEST_FORMAT_VERSION, version="0.1.0", type="my_type", name="their name"),
        dict(
            root="https://example.com",
            format_version=LATEST_FORMAT_VERSION,
            version="0.1.0",
            type="my_type",
            name="its name",
            attachments={"files": [Path(__file__), "missing"], "something": 42},
        ),
    ]
