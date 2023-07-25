from __future__ import annotations
from importlib.resources import files

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Mapping, Sequence

if TYPE_CHECKING:
    from bioimageio.spec.shared.types import LicenseId

DOI_REGEX = r"10\.[0-9]{4}.+"  # lax DOI regex validating the first 7 DOI characters only

IN_PACKAGE_MESSAGE = "∈📦 "

# license file generated with scripts/update_spdx_licenses.py
with files("bioimageio.spec").joinpath("static/licenses.json").open("r", encoding="utf-8") as f:
    _license_data = json.load(f)

LICENSES: Dict[LicenseId, Dict[str, Any]] = {x["licenseId"]: x for x in _license_data["licenses"]}
LICENSE_DATA_VERSION = _license_data["licenseListVersion"]

SHA256_HINT = """You can drag and drop your file to this
[online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate a SHA256 in your browser.
Or you can generate a SHA256 checksum with Python's `hashlib`,
[here is a codesnippet](https://gist.github.com/FynnBe/e64460463df89439cff218bbf59c1100)."""

with files("bioimageio.spec").joinpath("static/tag_categories.json").open("r", encoding="utf-8") as f:
    TAG_CATEGORIES: Mapping[str, Mapping[str, Sequence[str]]] = json.load(f)

# SI unit regex adapted from https://stackoverflow.com/a/3573731
_prefix = "(Q|R|Y|Z|E|P|T|G|M|k|h|da|d|c|m|µ|n|p|f|a|z|y|r|q)"
_unit = "(m|g|s|A|K|mol|cd|Hz|N|Pa|J|W|C|V|F|Ω|S|Wb|T|H|lm|lx|Bq|Gy|Sv|kat|l|L)"
_any_power = r"(\^[+-]?[1-9]\d*)"
_pos_power = r"(\^+?[1-9]\d*)"
_unit_ap = f"{_prefix}?{_unit}{_any_power}?"
_unit_pp = f"{_prefix}?{_unit}{_pos_power}?"
SI_UNIT_REGEX = f"^{_unit_ap}((·{_unit_ap})|(/{_unit_pp}))*$"
