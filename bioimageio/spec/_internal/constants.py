from __future__ import annotations

import json
import sys
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Dict, Mapping, NamedTuple, Sequence, Union

from bioimageio.spec._internal.utils import files

if TYPE_CHECKING:
    from bioimageio.spec._internal.types import FormatVersionPlaceholder, LicenseId
    from bioimageio.spec._internal.validation_context import WarningLevel
    from bioimageio.spec.summary import WarningLevelName, WarningSeverity, WarningSeverityName


if sys.version_info < (3, 10):
    SLOTS: Dict[str, bool] = {}
    KW_ONLY: Dict[str, bool] = {}
else:
    SLOTS = {"slots": True}
    KW_ONLY = {"kw_only": True}

with files("bioimageio.spec").joinpath("VERSION").open("r", encoding="utf-8") as f:
    VERSION: str = json.load(f)["version"]
    assert isinstance(VERSION, str), VERSION

DOI_REGEX = r"^10\.[0-9]{4}.+$"  # lax DOI regex validating the first 7 DOI characters only

IN_PACKAGE_MESSAGE = "∈📦 "

# license file generated with scripts/update_spdx_licenses.py
with files("bioimageio.spec").joinpath("static/spdx_licenses.json").open("r", encoding="utf-8") as f:
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


class MinMax(NamedTuple):
    min: Union[int, float]
    max: Union[int, float]


# numpy.dtype limits; see scripts/generate_dtype_limits.py
DTYPE_LIMITS = MappingProxyType(
    {
        "float32": MinMax(-3.4028235e38, 3.4028235e38),
        "float64": MinMax(-1.7976931348623157e308, 1.7976931348623157e308),
        "uint8": MinMax(0, 255),
        "int8": MinMax(-128, 127),
        "uint16": MinMax(0, 65535),
        "int16": MinMax(-32768, 32767),
        "uint32": MinMax(0, 4294967295),
        "int32": MinMax(-2147483648, 2147483647),
        "uint64": MinMax(0, 18446744073709551615),
        "int64": MinMax(-9223372036854775808, 9223372036854775807),
    }
)

WARNING_LEVEL_CONTEXT_KEY = "warning_level"
ERROR, ERROR_NAME = 50, "error"
"""A warning of the error level is always raised (equivalent to a validation error)"""

ALERT, ALERT_NAME = 35, "alert"
"""no ALERT nor ERROR -> RDF is worriless"""

WARNING, WARNING_NAME = 30, "warning"
"""no WARNING nor ALERT nor ERROR -> RDF is watertight"""

INFO, INFO_NAME = 20, "info"
"""info warnings are about purely cosmetic issues, etc."""

WARNING_SEVERITY_TO_NAME: Mapping[WarningSeverity, WarningSeverityName] = MappingProxyType(
    {INFO: INFO_NAME, WARNING: WARNING_NAME, ALERT: ALERT_NAME}
)
WARNING_LEVEL_TO_NAME: Mapping[WarningLevel, WarningLevelName] = MappingProxyType(
    {**WARNING_SEVERITY_TO_NAME, ERROR: ERROR_NAME}
)
WARNING_NAME_TO_LEVEL: Mapping[WarningLevelName, WarningLevel] = MappingProxyType(
    {v: k for k, v in WARNING_LEVEL_TO_NAME.items()}
)

LATEST: FormatVersionPlaceholder = "latest"
"""placeholder for the latest available format version"""

DISCOVER: FormatVersionPlaceholder = "discover"
"""placeholder for whatever format version an RDF specifies"""
