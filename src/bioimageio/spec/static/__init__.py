import json
import importlib.resources

_licenses_root = json.loads(importlib.resources.read_text(__package__, "licenses.json"))

LICENSES = {x["licenseId"]: x for x in _licenses_root["licenses"]}
LICENSE_DATA_VERSION = _licenses_root["licenseListVersion"]

del _licenses_root
