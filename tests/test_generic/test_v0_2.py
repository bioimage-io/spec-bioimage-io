from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Type

import pytest
from pydantic import HttpUrl, ValidationError

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.constants import WARNING
from bioimageio.spec.generic.v0_2 import Attachments, Author, CiteEntry, Generic, Maintainer
from bioimageio.spec.types import RelativeFilePath, ValidationContext
from tests.utils import check_node

EXAMPLE_DOT_COM = "https://example.com/"


@pytest.mark.parametrize(
    "node_class,kwargs,is_valid",
    [
        (Attachments, dict(files=(RelativeFilePath(__file__), HttpUrl(EXAMPLE_DOT_COM)), another_attachment=5), True),
        (Attachments, dict(files=(__file__, EXAMPLE_DOT_COM), extra=dict(more="of this")), True),
        (Attachments, dict(files=(__file__, "http:example.com")), True),
        (Attachments, dict(only="other stuff"), True),
        (Attachments, dict(files=__file__), False),
        (Attachments, dict(files=["non-existing-file"]), False),
        (Attachments, dict(files=[123]), False),
        (Author, dict(name="only_name"), True),
        (
            Author,
            dict(
                name="Me",
                affiliation="Paradise",
                email="them@example.com",
                github_user="ghuser",
                orcid="0000-0001-2345-6789",
            ),
            True,
        ),
        (
            Author,
            dict(affiliation="Paradise", email="you@example.com", github_user="ghuser", orcid="0000-0001-2345-6789"),
            False,
        ),
        (
            Author,
            dict(
                name="Me",
                affiliation="Paradise",
                email="me@example.com",
                github_user="ghuser",
                orcid="0000-0001-2345-6788",
            ),
            False,
        ),
        (Author, dict(name=5), False),
        (Maintainer, dict(github_user="ghuser_only"), True),
        (
            Maintainer,
            dict(
                name="Me",
                affiliation="Paradise",
                email="me@example.com",
                github_user="ghuser",
                orcid="0000-0001-2345-6789",
            ),
            True,
        ),
        (Maintainer, dict(name="without_gh"), False),
        (Maintainer, dict(github_user=5.5), False),
        (CiteEntry, dict(text="lala", url=EXAMPLE_DOT_COM), True),
        (CiteEntry, dict(text="lala", doi="10.1234fakedoi"), True),
        (
            CiteEntry,
            dict(
                text="Title",
                doi="10.1109/5.771073",
                url="https://ieeexplore.ieee.org/document/771073",
            ),
            True,
        ),
        (CiteEntry, dict(text="lala"), False),
        (CiteEntry, dict(url=EXAMPLE_DOT_COM), False),
        (
            Generic,
            dict(
                authors=[{"name": "Me"}],
                description="the description",
                format_version=Generic.implemented_format_version,
                license="BSD-2-Clause-FreeBSD",
                name="my name",
                type="my_type",
                unknown_extra_field="present",
                version="1.0",
            ),
            True,
        ),
        (
            Generic,
            dict(
                format_version=Generic.implemented_format_version,
                name="your name",
                description="my description",
                attachments={"files": [Path(__file__)], "something": 42},
                type="my_type",
                version="0.1.0",
            ),
            True,
        ),
        (Generic, dict(text="lala"), False),
        (Generic, dict(url=EXAMPLE_DOT_COM), False),
        (
            Generic,
            dict(
                authors=[{"name": "Me"}],
                description="the description",
                format_version=Generic.implemented_format_version,
                license="BSD-2-Clause-FreeBSD",
                name="my name",
                type="my_type",
                unknown_extra_field="present",
                version="1.0",
            ),
            True,
        ),
        (
            Generic,
            dict(
                format_version=Generic.implemented_format_version,
                name="your name",
                description="my description",
                attachments={"files": [Path(__file__)], "something": 42},
                type="my_type",
                version="0.1.0",
            ),
            True,
        ),
        (
            Generic,
            dict(format_version=Generic.implemented_format_version, version="0.1.0", type="my_type", name="their name"),
            False,
        ),
        (
            Generic,
            dict(
                format_version=Generic.implemented_format_version,
                version="0.1.0",
                type="my_type",
                name="its name",
                attachments={"files": [Path(__file__), "missing"], "something": 42},
            ),
            False,
        ),
    ],
)
def test_node(node_class: Type[Node], kwargs: Dict[str, Any], is_valid: bool):
    check_node(node_class, kwargs, is_invalid=not is_valid)


def test_deprecated_license_in_generic():
    check_node(
        Generic,
        dict(
            format_version=Generic.implemented_format_version,
            name="my name",
            description="my description",
            authors=[{"name": "Me"}],
            type="my_type",
            version="1.0",
            license="BSD-2-Clause-FreeBSD",
            cite=[dict(text="lala", url=EXAMPLE_DOT_COM)],
        ),
        context=ValidationContext(warning_level=WARNING),
        is_invalid=True,
    )
