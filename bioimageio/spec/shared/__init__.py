from __future__ import annotations

import json
from pathlib import Path

from .common import get_args, yaml  # noqa
from . import fields, raw_nodes, schema

_license_file = Path(__file__).parent.parent / "static" / "licenses.json"
_license_data = json.loads(_license_file.read_text(encoding="utf-8"))

LICENSES = {x["licenseId"]: x for x in _license_data["licenses"]}
LICENSE_DATA_VERSION = _license_data["licenseListVersion"]
