from typing import Any, Collection, Dict, Iterable, Mapping, Tuple

import httpx
import pytest

from bioimageio.spec.common import HttpUrl, Sha256
from tests.utils import ParameterSet, check_bioimageio_yaml, expensive_test

BASE_URL = "https://uk1s3.embassy.ebi.ac.uk/public-datasets/bioimage.io/"

KNOWN_INVALID: Mapping[str, str] = {
    "stupendous-sheep/1.1": "requires relativ import of attachment",
    "whimsical-helmet/2.1.2": "invalid id",
    "modest-spider/0.1.1": "non-batch id 'b'",
}
EXCLUDE_FIELDS_FROM_ROUNDTRIP_DEFAULT: Collection[str] = {
    "version_number",  # deprecated field that gets dropped in favor of `version``
    "version",  # may be set from deprecated `version_number`
}
EXCLUDE_FIELDS_FROM_ROUNDTRIP: Mapping[str, Collection[str]] = {
    "affable-shark/1.1": {"inputs"},  # preprocessing ensure_dtype added
    "affable-shark/1.2": {"inputs"},  # preprocessing ensure_dtype added
    "charismatic-whale/1.0.1": {"inputs", "outputs"},  # int -> float
    "dynamic-t-rex/1": {"inputs"},  # int -> float
    "impartial-shrimp/1.1": {"inputs", "cite"},  # preprocessing ensure_dtype added
    "philosophical-panda/0.0.11": {"outputs"},  # int -> float
    "philosophical-panda/0.1.0": {"outputs"},  # int -> float
    "polite-pig/1.1": {"inputs", "outputs"},
    "charismatic-whale/1.0.2": {"inputs", "outputs"},  # int -> float
    "dynamic-t-rex/1.1": {"inputs"},  # int -> float
}


def _get_rdf_sources(only_latest: bool = True):
    entries: Any = httpx.get(BASE_URL + "all_versions.json").json()["entries"]
    ret: Dict[str, Tuple[HttpUrl, Sha256]] = {}
    for entry in entries:
        for version in entry["versions"]:
            ret[f"{entry['concept']}/{version['v']}"] = (
                HttpUrl(version["source"]),
                Sha256(version["sha256"]),
            )
            if only_latest:
                break

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


@expensive_test
@pytest.mark.parametrize(
    "descr_url,sha,key",
    sorted(
        yield_bioimageio_yaml_urls(),
        key=lambda p: p.id,  # pyright: ignore[reportAttributeAccessIssue,reportUnknownLambdaType]
    ),
)
def test_rdf(
    descr_url: HttpUrl,
    sha: Sha256,
    key: str,
    bioimageio_json_schema: Mapping[Any, Any],
):
    if key in KNOWN_INVALID:
        pytest.skip(KNOWN_INVALID[key])

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


@expensive_test
@pytest.mark.parametrize(
    "rdf_id",
    [
        "ambitious-sloth/1.2",
        "breezy-handbag/1",
        "faithful-chicken/1.2",
        "ilastik/ilastik/1",
        "uplifting-ice-cream/1",
    ],
)
def test_exemplary_rdf(rdf_id: str, bioimageio_json_schema: Mapping[Any, Any]):
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
