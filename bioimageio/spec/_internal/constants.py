from __future__ import annotations

import json
from types import MappingProxyType
from typing import Mapping, NamedTuple, Sequence, Set, Union

from .utils import files

DOI_REGEX = (  # lax DOI regex validating the first 7 DOI characters only
    r"^10\.[0-9]{4}.+$"
)

SHA256_HINT = """You can drag and drop your file to this
[online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate a SHA256 in your browser.
Or you can generate a SHA256 checksum with Python's `hashlib`,
[here is a codesnippet](https://gist.github.com/FynnBe/e64460463df89439cff218bbf59c1100)."""

with (
    files("bioimageio.spec")
    .joinpath("static/tag_categories.json")
    .open("r", encoding="utf-8")
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


class _DtypeLimit(NamedTuple):
    min: Union[int, float]
    max: Union[int, float]


# numpy.dtype limits; see scripts/generate_dtype_limits.py
DTYPE_LIMITS = MappingProxyType(
    {
        "float32": _DtypeLimit(-3.4028235e38, 3.4028235e38),
        "float64": _DtypeLimit(-1.7976931348623157e308, 1.7976931348623157e308),
        "uint8": _DtypeLimit(0, 255),
        "int8": _DtypeLimit(-128, 127),
        "uint16": _DtypeLimit(0, 65535),
        "int16": _DtypeLimit(-32768, 32767),
        "uint32": _DtypeLimit(0, 4294967295),
        "int32": _DtypeLimit(-2147483648, 2147483647),
        "uint64": _DtypeLimit(0, 18446744073709551615),
        "int64": _DtypeLimit(-9223372036854775808, 9223372036854775807),
    }
)

# TODO: cache/store known GitHub users in file
KNOWN_GITHUB_USERS: Set[str] = {
    "aaitorg",
    "anwai98",
    "bioimageiobot",
    "carlosuc3m",
    "cfusterbarcelo",
    "clementcaporal",
    "constantinpape",
    "ctr26",
    "danifranco",
    "donglaiw",
    "esgomezm",
    "fynnbe",
    "githubuser2",
    "iarganda",
    "ilastik",
    "ivanhcenalmor",
    "jansanrom",
    "k-dominik",
    "lenkaback",
    "oeway",
    "pedgomgal1",
}

N_KNOWN_GITHUB_USERS = len(KNOWN_GITHUB_USERS)
KNOWN_INVALID_GITHUB_USERS: Set[str] = {"arratemunoz", "lmescu"}
N_KNOWN_INVALID_GITHUB_USERS = len(KNOWN_INVALID_GITHUB_USERS)
