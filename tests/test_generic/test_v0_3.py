from __future__ import annotations

from pathlib import Path

from bioimageio.spec._internal._constants import WARNING, WARNING_LEVEL_CONTEXT_KEY
from bioimageio.spec.generic.v0_3 import Generic
from tests.unittest_utils import Invalid, TestBases, Valid

EXAMPLE_DOT_COM = "https://example.com/"


class TestGeneric(TestBases.TestNode):
    default_node_class = Generic
    sub_tests = [
        Valid(
            dict(
                authors=[{"name": "Me"}],
                cite=[dict(text="lala", url=EXAMPLE_DOT_COM)],
                description="the description",
                format_version=Generic.implemented_format_version,
                license="BSD-2-Clause-FreeBSD",
                name="my name",
                type="my_type",
                unknown_extra_field="present",
                version="1.0",
            )
        ),
        Valid(
            dict(
                attachments={"files": [Path(__file__)], "something": 42},
                authors=[{"name": "Me"}],
                cite=[dict(text="lala", url=EXAMPLE_DOT_COM)],
                description="my description",
                format_version=Generic.implemented_format_version,
                license="BSD-2-Clause-FreeBSD",
                name="your name",
                type="my_type",
                version="0.1.0",
            ),
        ),
        Invalid(
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
            context={WARNING_LEVEL_CONTEXT_KEY: WARNING},
            name="deprecated license",
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
