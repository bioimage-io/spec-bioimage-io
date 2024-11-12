import json
from pathlib import Path
from typing import Any, Collection, Iterable, Mapping, Tuple

import pooch  # pyright: ignore [reportMissingTypeStubs]
import pytest

from bioimageio.spec import settings
from bioimageio.spec.common import HttpUrl
from tests.utils import ParameterSet, check_bioimageio_yaml

BASE_URL = "https://uk1s3.embassy.ebi.ac.uk/public-datasets/bioimage.io/"

KNOWN_INVALID: Collection[str] = set()
EXCLUDE_FIELDS_FROM_ROUNDTRIP_DEFAULT: Collection[str] = set()
EXCLUDE_FIELDS_FROM_ROUNDTRIP: Mapping[str, Collection[str]] = {
    "affable-shark/1.1": {"inputs"}
}


def _get_collection_data():
    collection_path: Any = pooch.retrieve(
        BASE_URL + "collection.json", None, path=settings.cache_path
    )
    with Path(collection_path).open(encoding="utf-8") as f:
        data = json.load(f)["collection"]

    assert not (
        bad_entries := [d for d in data if not isinstance(d, dict)]
    ), bad_entries
    assert not (wo_id := [entry for entry in data if "id" not in entry]), wo_id
    return data


ALL_LATEST_RDF_SOURCES: Mapping[str, Tuple[HttpUrl, str]] = {
    str(entry.get("nickname", entry["id"])): (
        HttpUrl(entry["rdf_source"]),
        str(entry.get("nickname_icon", "")),
    )
    for entry in _get_collection_data()
}


def yield_bioimageio_yaml_urls() -> Iterable[ParameterSet]:
    for descr_url, icon in ALL_LATEST_RDF_SOURCES.values():
        key = icon + (
            descr_url.replace(BASE_URL, "")
            .replace("/files/rdf.yaml", "")
            .replace("/files/bioimageio.yaml", "")
        )
        yield pytest.param(descr_url, key, id=key)


@pytest.mark.parametrize("descr_url,key", list(yield_bioimageio_yaml_urls()))
def test_rdf(
    descr_url: Path,
    key: str,
    bioimageio_json_schema: Mapping[Any, Any],
):
    if key in KNOWN_INVALID:
        pytest.skip("known failure")

    check_bioimageio_yaml(
        descr_url,
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
    check_bioimageio_yaml(
        ALL_LATEST_RDF_SOURCES[rdf_id][0],
        as_latest=True,
        exclude_fields_from_roundtrip=EXCLUDE_FIELDS_FROM_ROUNDTRIP.get(
            rdf_id, EXCLUDE_FIELDS_FROM_ROUNDTRIP_DEFAULT
        ),
        bioimageio_json_schema=bioimageio_json_schema,
        perform_io_checks=True,
    )
