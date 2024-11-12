import json
from pathlib import Path
from typing import Any, Collection, Dict, Iterable, Mapping, Tuple

import pooch  # pyright: ignore [reportMissingTypeStubs]
import pytest

from bioimageio.spec import settings
from bioimageio.spec.common import HttpUrl, Sha256
from tests.utils import ParameterSet, check_bioimageio_yaml

BASE_URL = "https://uk1s3.embassy.ebi.ac.uk/public-datasets/bioimage.io/"

KNOWN_INVALID: Collection[str] = set()
EXCLUDE_FIELDS_FROM_ROUNDTRIP_DEFAULT: Collection[str] = {
    "version_number",  # deprecated field that gets dropped in favor of `version``
    "version",  # may be set from deprecated `version_number`
}
EXCLUDE_FIELDS_FROM_ROUNDTRIP: Mapping[str, Collection[str]] = {
    "affable-shark/1.1": {"inputs"}
}


def _get_rdf_sources():
    all_versions_path: Any = pooch.retrieve(
        BASE_URL + "all_versions.json", None, path=settings.cache_path
    )
    with Path(all_versions_path).open(encoding="utf-8") as f:
        entries = json.load(f)["entries"]

    ret: Dict[str, Tuple[HttpUrl, Sha256]] = {}
    for entry in entries:
        for version in entry["versions"]:
            ret[f"{entry['concept']}/{version['v']}"] = (
                HttpUrl(version["source"]),
                Sha256(version["sha256"]),
            )

    return ret


ALL_RDF_SOURCES: Mapping[str, Tuple[HttpUrl, Sha256]] = _get_rdf_sources()


def yield_bioimageio_yaml_urls() -> Iterable[ParameterSet]:
    for descr_url, sha in ALL_RDF_SOURCES.values():
        key = (
            descr_url.replace(BASE_URL, "")
            .replace("/files/rdf.yaml", "")
            .replace("/files/bioimageio.yaml", "")
        )
        yield pytest.param(descr_url, sha, key, id=key)


@pytest.mark.parametrize("descr_url,sha,key", list(yield_bioimageio_yaml_urls()))
def test_rdf(
    descr_url: Path,
    sha: Sha256,
    key: str,
    bioimageio_json_schema: Mapping[Any, Any],
):
    if key in KNOWN_INVALID:
        pytest.skip("known failure")

    check_bioimageio_yaml(
        descr_url,
        sha=sha,
        as_latest=False,
        exclude_fields_from_roundtrip=EXCLUDE_FIELDS_FROM_ROUNDTRIP.get(
            key, EXCLUDE_FIELDS_FROM_ROUNDTRIP_DEFAULT
        ),
        bioimageio_json_schema=bioimageio_json_schema,
        perform_io_checks=False,
    )


@pytest.mark.parametrize(
    "rdf_id",
    [
        "affable-shark",
        "ambitious-sloth",
    ],
)
def test_examplary_rdf(rdf_id: str, bioimageio_json_schema: Mapping[Any, Any]):
    """test a list of models we expect to be compatible with the latest spec version"""
    source, sha = ALL_RDF_SOURCES[rdf_id]
    check_bioimageio_yaml(
        source,
        sha=sha,
        as_latest=True,
        exclude_fields_from_roundtrip=EXCLUDE_FIELDS_FROM_ROUNDTRIP.get(
            rdf_id, EXCLUDE_FIELDS_FROM_ROUNDTRIP_DEFAULT
        ),
        bioimageio_json_schema=bioimageio_json_schema,
        perform_io_checks=True,
    )
