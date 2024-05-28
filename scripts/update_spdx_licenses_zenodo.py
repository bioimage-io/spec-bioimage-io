"""script that updates the content of bioimageio/spec/static/spdx_licenses.json with the 'isKnownByZenodo' flag"""

import json
import sys
from pathlib import Path

import requests
from loguru import logger
from tqdm import tqdm

from bioimageio.spec.utils import SpdxLicenses

PROJECT_ROOT = Path(__file__).parent.parent

LICENSES_JSON_FILE = PROJECT_ROOT / "bioimageio/spec/static/spdx_licenses.json"


def main(recheck: bool = False):
    with LICENSES_JSON_FILE.open("rt", encoding="utf-8") as f:
        licenses_full = SpdxLicenses(**json.load(f))

    counts = {True: 0, False: 0, None: 0}
    try:
        for lic in tqdm(licenses_full["licenses"]):
            if recheck is False and isinstance(
                (known := lic.get("isKnownByZenodo")), bool
            ):
                counts[known] += 1
                continue

            url = (
                "https://zenodo.org/api/vocabularies/licenses/"
                + lic["licenseId"].lower()
            )
            r = requests.get(url, timeout=5)

            if 200 <= r.status_code < 300:
                known = True
            elif 400 <= r.status_code < 500:
                known = False
            elif 500 <= r.status_code < 600:
                logger.warning(
                    f"Zenodo server error {r.status_code, r.reason} for {url}"
                )
                known = None
            else:
                raise NotImplementedError(
                    f"got unexpected status code: {r.status_code}"
                )

            # `test_license_zenodo` makes sure `known` is a boolean
            lic["isKnownByZenodo"] = known  # pyright: ignore[reportGeneralTypeIssues]
            counts[known] += 1
    finally:
        with LICENSES_JSON_FILE.open("wt", encoding="utf-8") as f:
            json.dump(licenses_full, f, indent=2)

    print(f"Updated {LICENSES_JSON_FILE}")
    print(f"known to zenodo: {counts}")


if __name__ == "__main__":
    sys.exit(main())
