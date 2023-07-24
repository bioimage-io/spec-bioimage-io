from __future__ import annotations

from pathlib import Path

from pydantic import HttpUrl

from bioimageio.spec.generic.v0_2 import (
    Attachments,
    Author,
    CiteEntry,
    Generic,
    Maintainer,
)
from bioimageio.spec.shared.types import RelativeFilePath
from tests.unittest_utils import BaseTestCases, Invalid, Valid

EXAMPLE_DOT_COM = "https://example.com/"


class TestAttachments(BaseTestCases.TestNode):
    default_node_class = Attachments
    sub_tests = [
        Valid(dict(files=(RelativeFilePath(__file__), HttpUrl(EXAMPLE_DOT_COM)), another_attachment=5)),
        Valid(dict(files=(__file__, EXAMPLE_DOT_COM), extra=Valid(dict(more="of this")))),
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
                email="them@example.com",
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
        Valid(dict(text="lala", url=EXAMPLE_DOT_COM)),
        Valid(dict(text="lala", doi="10.1234fakedoi")),
        Invalid(dict(text="lala")),
        Invalid(dict(url=EXAMPLE_DOT_COM)),
    ]


class TestGeneric(BaseTestCases.TestNode):
    default_node_class = Generic
    sub_tests = [
        Valid(
            dict(
                format_version=Generic.implemented_format_version,
                name="my name",
                description="the description",
                authors=[{"name": "Me"}],
                root=Path(__file__).parent.parent,
                type="my_type",
                version="1.0",
                license="BSD-2-Clause-FreeBSD",
            )
        ),
        Invalid(
            dict(
                format_version=Generic.implemented_format_version,
                name="my name",
                description="my description",
                authors=[{"name": "Me"}],
                root=Path(__file__).parent,
                type="my_type",
                version="1.0",
                license="BSD-2-Clause-FreeBSD",
                cite=[dict(name="lala", url=EXAMPLE_DOT_COM)],
            ),
            context={"root": Path(__file__).parent},
            name="deprecated license",
        ),
        Valid(
            dict(
                format_version=Generic.implemented_format_version,
                name="your name",
                description="my description",
                attachments={"files": [Path(__file__)], "something": 42},
                root=EXAMPLE_DOT_COM,
                type="my_type",
                version="0.1.0",
            ),
            context={},
        ),
        Invalid(
            dict(format_version=Generic.implemented_format_version, version="0.1.0", type="my_type", name="their name")
        ),
        Invalid(
            dict(
                format_version=Generic.implemented_format_version,
                version="0.1.0",
                type="my_type",
                name="its name",
                attachments={"files": [Path(__file__), "missing"], "something": 42},
            )
        ),
    ]
