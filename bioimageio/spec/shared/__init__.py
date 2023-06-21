from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

# from ._resolve_source import (
#     BIOIMAGEIO_COLLECTION,
#     BIOIMAGEIO_COLLECTION_ERROR,
#     BIOIMAGEIO_SITE_CONFIG,
#     BIOIMAGEIO_SITE_CONFIG_ERROR,
#     DownloadCancelled,
#     RDF_NAMES,
#     _resolve_json_from_url,
#     get_resolved_source_path,
#     resolve_local_source,
#     resolve_rdf_source,
#     resolve_rdf_source_and_type,
#     resolve_source,
#     source_available,
# )

# license file copied from https: //github.com/spdx/license-list-data/blob/v3.20/json/licenses.json
_license_file = Path(__file__).parent.parent / "static" / "licenses.json"
_license_data = json.loads(_license_file.read_text(encoding="utf-8"))

LICENSES: Dict[LicenseId, Dict[str, Any]] = {x["licenseId"]: x for x in _license_data["licenses"]}
LICENSE_DATA_VERSION = _license_data["licenseListVersion"]

_tag_categories_file = Path(__file__).parent.parent / "static" / "tag_categories.json"
TAG_CATEGORIES = json.loads(_tag_categories_file.read_text(encoding="utf-8"))
