from __future__ import annotations

from typing import Any, Dict, Type

import pytest

from bioimageio.spec._internal.common_nodes import Node
from bioimageio.spec._internal.validation_context import ValidationContext
from bioimageio.spec._internal.warning_levels import WARNING
from bioimageio.spec.generic.v0_2 import (
    AttachmentsDescr,
    Author,
    CiteEntry,
    GenericDescr,
    Maintainer,
)
from tests.utils import check_node

EXAMPLE_COM = "https://example.com/"


@pytest.mark.parametrize(
    "node_class,kwargs,is_valid",
    [
        (AttachmentsDescr, {"magic_number": 5}, True),
        (AttachmentsDescr, {"extra": {"more": "of this"}}, True),
        (AttachmentsDescr, {"only": "other stuff"}, True),
        (AttachmentsDescr, {"files": "not a list"}, False),
        (AttachmentsDescr, {"files": ["non-existing-file"]}, False),
        (AttachmentsDescr, {"files": [123]}, False),
        (Author, {"name": "only_name"}, True),
        (
            Author,
            {
                "name": "Me",
                "affiliation": "Paradise",
                "email": "them@example.com",
                "github_user": "ghuser",
                "orcid": "0000-0001-2345-6789",
            },
            True,
        ),
        (
            Author,
            {
                "affiliation": "Paradise",
                "email": "you@example.com",
                "github_user": "ghuser",
                "orcid": "0000-0001-2345-6789",
            },
            False,
        ),
        (
            Author,
            {
                "name": "Me",
                "affiliation": "Paradise",
                "email": "me@example.com",
                "github_user": "ghuser",
                "orcid": "0000-0001-2345-6788",
            },
            False,
        ),
        (Author, {"name": 5}, False),
        (Maintainer, {"github_user": "ghuser_only"}, True),
        (
            Maintainer,
            {
                "name": "Me",
                "affiliation": "Paradise",
                "email": "me@example.com",
                "github_user": "ghuser",
                "orcid": "0000-0001-2345-6789",
            },
            True,
        ),
        (
            Maintainer,
            {
                "name": "Dani",
                "email": "me@example.com",
                "github_user": "danifranco",
                "orcid": "0000-0002-1109-110X",
            },
            True,
        ),
        (Maintainer, {"name": "without_gh"}, False),
        (Maintainer, {"github_user": 5.5}, False),
        (CiteEntry, {"text": "lala", "url": EXAMPLE_COM}, True),
        (CiteEntry, {"text": "lala", "doi": "10.1234fakedoi"}, True),
        (
            CiteEntry,
            {
                "text": "Title",
                "doi": "10.1109/5.771073",
                "url": "https://ieeexplore.ieee.org/document/771073",
            },
            True,
        ),
        (CiteEntry, {"text": "lala"}, False),
        (CiteEntry, {"url": EXAMPLE_COM}, False),
        (
            GenericDescr,
            {
                "authors": [{"name": "Me"}],
                "description": "the description",
                "format_version": GenericDescr.implemented_format_version,
                "license": "BSD-2-Clause-FreeBSD",
                "name": "my name",
                "type": "my_type",
                "unknown_extra_field": "present",
                "version": "0.1.0",
            },
            True,
        ),
        (
            GenericDescr,
            {
                "format_version": GenericDescr.implemented_format_version,
                "name": "your name",
                "description": "my description",
                "attachments": {"something": None},
                "type": "my_type",
                "version": "0.1.0",
            },
            True,
        ),
        (GenericDescr, {"text": "lala"}, False),
        (GenericDescr, {"url": EXAMPLE_COM}, False),
        (
            GenericDescr,
            {
                "format_version": GenericDescr.implemented_format_version,
                "name": "your name",
                "description": "my description",
                "attachments": {"something": 42},
                "type": "my_type",
                "version": "0.1.0",
            },
            True,
        ),
        (
            GenericDescr,
            {
                "format_version": GenericDescr.implemented_format_version,
                "version": "0.1.0",
                "type": "my_type",
                "name": "their name",
            },
            False,
        ),
        (
            GenericDescr,
            {
                "format_version": GenericDescr.implemented_format_version,
                "version": "0.1.0",
                "type": "my_type",
                "name": "its name",
                "attachments": {"files": ["missing"], "something": 42},
            },
            False,
        ),
    ],
)
def test_node(node_class: Type[Node], kwargs: Dict[str, Any], is_valid: bool):
    check_node(
        node_class,
        kwargs,
        is_invalid=not is_valid,
        context=ValidationContext(perform_io_checks=True),
    )


def test_deprecated_license_in_generic():
    check_node(
        GenericDescr,
        {
            "format_version": GenericDescr.implemented_format_version,
            "name": "my name",
            "description": "my description",
            "authors": [{"name": "Me"}],
            "type": "my_type",
            "version": "0.1.0",
            "license": "BSD-2-Clause-FreeBSD",
            "cite": [{"text": "lala", "url": EXAMPLE_COM}],
        },
        context=ValidationContext(warning_level=WARNING),
        is_invalid=True,
    )
