import logging
from pathlib import Path
from types import MappingProxyType
from typing import Annotated
from unittest import TestCase

from annotated_types import Ge
from pydantic import ValidationError
from ruamel.yaml import YAML

from bioimageio.spec._internal._constants import ALERT, INFO, WARNING, WARNING_LEVEL_CONTEXT_KEY
from bioimageio.spec._internal._warn import warn
from bioimageio.spec.shared.nodes import Node
from bioimageio.spec.utils import update_format, validate

yaml = YAML(typ="safe")

EXAMPLE_SPECS = Path(__file__).parent / "../example_specs"


class TestUpdateFormatWithStardist(TestCase):
    @classmethod
    def setUpClass(cls):
        with (EXAMPLE_SPECS / "models/stardist_example_model/rdf_v0_4.yaml").open() as f:
            cls.data = MappingProxyType(yaml.load(f))

    def test_update_format(self):
        _ = update_format(self.data)
        with self.assertRaises(ValueError):
            _ = update_format(self.data, context={"warning_level": ALERT})


class TestForwardCompatibility(TestCase):
    @classmethod
    def setUpClass(cls):
        root = EXAMPLE_SPECS / "models/unet2d_nuclei_broad"
        with (root / "rdf.yaml").open() as f:
            data = yaml.load(f)

        data["root"] = root
        cls.data = MappingProxyType(data)

    def test_forward_compatibility(self):
        data = dict(self.data)
        data["format_version"] = "9999.0.0"  # assume it is valid in a future format version

        summary = validate(data)
        self.assertEqual(summary["status"], "passed", summary)

        # expect warning about treating future format version as latest
        ws = summary.get("warnings", [])
        self.assertEqual(len(ws), 1, ws)
        self.assertEqual(ws[0]["loc"], ("format_version",), ws[0]["loc"])

    def test_no_forward_compatibility(self):
        data = dict(self.data)
        data["authors"] = 42  # make sure rdf is invalid
        data["format_version"] = "9999.0.0"  # assume it is valid in a future format version

        summary = validate(data)
        self.assertEqual(summary["status"], "failed", summary)

        errors = summary.get("errors", [])
        self.assertEqual(len(errors), 1, errors)
        self.assertEqual(errors[0]["loc"], ("authors",), errors[0]["loc"])

        # expect warning about treating future format version as latest
        ws = summary.get("warnings", [])
        self.assertEqual(len(ws), 1, ws)
        self.assertEqual(ws[0]["loc"], ("format_version",), ws[0]["loc"])
