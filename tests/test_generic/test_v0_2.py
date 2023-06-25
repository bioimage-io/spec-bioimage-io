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
from bioimageio.spec.shared.types import RelativeFilePath
from bioimageio.spec.shared.validation import RAISE_WARNINGS, WARNINGS_ACTION_KEY
from tests.unittest_utils import BaseTestCases, Invalid, Valid


class TestAttachments(BaseTestCases.TestNode):
    default_node_class = Attachments
    sub_tests = [
        Valid(dict(files=(RelativeFilePath(__file__), HttpUrl("https://example.com")), another_attachment=5)),
        Valid(dict(files=(__file__, "https://example.com"), extra=Valid(dict(more="of this")))),
        Valid(dict(files=(__file__, "http:example.com"))),
        Valid(dict(only="other stuff")),
        Invalid(dict(files=__file__)),
        Invalid(dict(files=["non-existing-file"])),
        Invalid(dict(files=[123])),
    ]


class TestAuthor(BaseTestCases.TestNode):
    default_node_class = Author
    sub_tests = [
        Valid(dict(name="only_name")),
        Valid(
            dict(
                name="Me",
                affiliation="Paradise",
                email="me@example.com",
                github_user="ghuser",
                orcid="0000-0001-2345-6789",
            )
        ),
        Invalid(
            dict(affiliation="Paradise", email="you@example.com", github_user="ghuser", orcid="0000-0001-2345-6789")
        ),
        Invalid(
            dict(
                name="Me",
                affiliation="Paradise",
                email="me@example.com",
                github_user="ghuser",
                orcid="0000-0001-2345-6788",
            )
        ),
        Invalid(dict(name=5)),
    ]


class TestMaintainer(BaseTestCases.TestNode):
    default_node_class = Maintainer
    sub_tests = [
        Valid(dict(github_user="ghuser_only")),
        Valid(
            dict(
                name="Me",
                affiliation="Paradise",
                email="me@example.com",
                github_user="ghuser",
                orcid="0000-0001-2345-6789",
            )
        ),
        Invalid(dict(name="only_name")),
        Invalid(dict(github_user=5.5)),
    ]


class TestCiteEntry(BaseTestCases.TestNode):
    default_node_class = CiteEntry
    sub_tests = [
        Valid(dict(text="lala", url="https://example.com")),
        Valid(dict(text="lala", doi="10.1234fakedoi")),
        Invalid(dict(text="lala")),
        Invalid(dict(url="https://example.com")),
    ]


class TestGenericDescription(BaseTestCases.TestNode):
    default_node_class = GenericDescription
    sub_tests = [
        Valid(
            dict(
                format_version=LATEST_FORMAT_VERSION,
                name="my name",
                description="my description",
                authors=[{"name": "Me"}],
                root=Path(__file__).parent.parent,
                type="my_type",
                version="1.0",
                license="BSD-2-Clause-FreeBSD",
            )
        ),
        Invalid(
            dict(
                format_version=LATEST_FORMAT_VERSION,
                name="my name",
                description="my description",
                authors=[{"name": "Me"}],
                root=Path(__file__).parent,
                type="my_type",
                version="1.0",
                license="BSD-2-Clause-FreeBSD",
            ),
            context={WARNINGS_ACTION_KEY: RAISE_WARNINGS, "root": Path(__file__).parent},
        ),
        Valid(
            dict(
                format_version=LATEST_FORMAT_VERSION,
                name="your name",
                description="my description",
                attachments={"files": [Path(__file__)], "something": 42},
                root="https://example.com",
                type="my_type",
                version="0.1.0",
            ),
            context={},
        ),
        Invalid(dict(format_version=LATEST_FORMAT_VERSION, version="0.1.0", type="my_type", name="their name")),
        Invalid(
            dict(
                format_version=LATEST_FORMAT_VERSION,
                version="0.1.0",
                type="my_type",
                name="its name",
                attachments={"files": [Path(__file__), "missing"], "something": 42},
            )
        ),
    ]
