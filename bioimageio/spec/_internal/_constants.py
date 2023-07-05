from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from bioimageio.spec.shared.types import LicenseId

DOI_REGEX = r"10\.[0-9]{4}.+"  # lax DOI regex validating the first 7 DOI characters only

# license file generated with scripts/update_spdx_licenses.py
_license_file = Path(__file__).parent.parent / "static" / "licenses.json"
_license_data = json.loads(_license_file.read_text(encoding="utf-8"))
LICENSES: Dict[LicenseId, Dict[str, Any]] = {x["licenseId"]: x for x in _license_data["licenses"]}
LICENSE_DATA_VERSION = _license_data["licenseListVersion"]

SHA256_HINT = """You can drag and drop your file to this
[online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate a SHA256 in your browser.
Or you can generate a SHA256 checksum with Python's `hashlib`,
[here is a codesnippet](https://gist.github.com/FynnBe/e64460463df89439cff218bbf59c1100)."""

_tag_categories_file = Path(__file__).parent.parent / "static" / "tag_categories.json"
TAG_CATEGORIES = json.loads(_tag_categories_file.read_text(encoding="utf-8"))
