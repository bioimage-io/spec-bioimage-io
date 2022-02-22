from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ._resolve_source import (
    RDF_NAMES,
    resolve_local_source,
    resolve_rdf_source,
    resolve_rdf_source_and_type,
    resolve_source,
    source_available,
)
from .common import BIOIMAGEIO_SITE_CONFIG_URL, get_args, yaml  # noqa

_license_file = Path(__file__).parent.parent / "static" / "licenses.json"
_license_data = json.loads(_license_file.read_text(encoding="utf-8"))

LICENSES = {x["licenseId"]: x for x in _license_data["licenses"]}
LICENSE_DATA_VERSION = _license_data["licenseListVersion"]


try:
    p = resolve_source(BIOIMAGEIO_SITE_CONFIG_URL)
    with p.open() as f:
        BIOIMAGEIO_SITE_CONFIG = json.load(f)

    assert isinstance(BIOIMAGEIO_SITE_CONFIG, dict)
except Exception as e:
    BIOIMAGEIO_SITE_CONFIG = None
    BIOIMAGEIO_SITE_CONFIG_ERROR: Optional[str] = str(e)
else:
    BIOIMAGEIO_SITE_CONFIG_ERROR = None
