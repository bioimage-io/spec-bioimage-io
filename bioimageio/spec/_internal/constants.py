from __future__ import annotations

import json
from types import MappingProxyType
from typing import Mapping, NamedTuple, Sequence, Set, Union

from .utils import files

with files("bioimageio.spec").joinpath("VERSION").open("r", encoding="utf-8") as f:
    VERSION: str = json.load(f)["version"]
    assert isinstance(VERSION, str), VERSION


DOI_REGEX = (  # lax DOI regex validating the first 7 DOI characters only
    r"^10\.[0-9]{4}.+$"
)

IN_PACKAGE_MESSAGE = "∈📦 "
"""DEPRECATED, use ImportantFileSource to indicate that a file source should be included in a package"""

# license file generated with scripts/update_spdx_licenses.py
with files("bioimageio.spec").joinpath("static/spdx_licenses.json").open(
    "r", encoding="utf-8"
) as f:
    _license_data = json.load(f)


SHA256_HINT = """You can drag and drop your file to this
[online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate a SHA256 in your browser.
Or you can generate a SHA256 checksum with Python's `hashlib`,
[here is a codesnippet](https://gist.github.com/FynnBe/e64460463df89439cff218bbf59c1100)."""

with files("bioimageio.spec").joinpath("static/tag_categories.json").open(
    "r", encoding="utf-8"
) as f:
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

# TODO: cache/store known gh users in file
KNOWN_GH_USERS: Set[str] = {
    "clementcaporal",
    "donglaiw",
    "jansanrom",
    "pedgomgal1",
    "aaitorg",
    "bioimageiobot",
    "carlosuc3m",
    "cfusterbarcelo",
    "constantinpape",
    "ctr26",
    "danifranco",
    "esgomezm",
    "fynnbe",
    "githubuser2",
    "iarganda",
    "ivanhcenalmor",
    "jansanrom",
    "k-dominik",
    "lenkaback",
    "oeway",
}
N_KNOWN_GH_USERS = len(KNOWN_GH_USERS)
KNOWN_INVALID_GH_USERS: Set[str] = {"arratemunoz", "lmescu"}
N_KNOWN_INVALID_GH_USERS = len(KNOWN_INVALID_GH_USERS)
