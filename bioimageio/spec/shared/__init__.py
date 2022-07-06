from __future__ import annotations

import json
from pathlib import Path

from ._resolve_source import (
    BIOIMAGEIO_COLLECTION,
    BIOIMAGEIO_COLLECTION_ERROR,
    BIOIMAGEIO_SITE_CONFIG,
    BIOIMAGEIO_SITE_CONFIG_ERROR,
    RDF_NAMES,
    DownloadCancelled,
    _resolve_json_from_url,
    resolve_local_source,
    resolve_rdf_source,
    resolve_rdf_source_and_type,
    resolve_source,
    source_available,
)
from ._update_nested import update_nested
from .common import get_args, yaml  # noqa

_license_file = Path(__file__).parent.parent / "static" / "licenses.json"
_license_data = json.loads(_license_file.read_text(encoding="utf-8"))

LICENSES = {x["licenseId"]: x for x in _license_data["licenses"]}
LICENSE_DATA_VERSION = _license_data["licenseListVersion"]
