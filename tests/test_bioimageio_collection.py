import datetime
import json
from pathlib import Path
from typing import Dict

import pooch  # type: ignore

from tests.unittest_utils import TestBases


BASE_URL = "https://bioimage-io.github.io/collection-bioimage-io/"
RDF_BASE_URL = BASE_URL + "rdfs/"
WEEK = f"{datetime.datetime.now().year}week{datetime.datetime.now().isocalendar()[1]}"
CACHE_PATH = Path(__file__).parent / "cache" / WEEK


class TestBioimageioCollection(TestBases.TestManyRdfs):
    rdf_root = CACHE_PATH
    known_invalid_as_is = {
        "10.5281/zenodo.5910854/6539073/rdf.yaml",
        "deepimagej/Mt3VirtualStaining/latest/rdf.yaml",
        "deepimagej/DeepSTORMZeroCostDL4Mic/latest/rdf.yaml",
        "deepimagej/MU-Lux_CTC_PhC-C2DL-PSC/latest/rdf.yaml",
        "deepimagej/Mt3VirtualStaining/latest/rdf.yaml",
    }

    known_invalid_as_latest = {
        "10.5281/zenodo.6559929/6559930/rdf.yaml",
        "10.5281/zenodo.7380171/7405349/rdf.yaml",
        "bioimageio/stardist/latest/rdf.yaml",
        "deepimagej/EVsTEMsegmentationFRUNet/latest/rdf.yaml" "deepimagej/MU-Lux_CTC_PhC-C2DL-PSC/latest/rdf.yaml",
        "deepimagej/MoNuSeg_digital_pathology_miccai2018/latest/rdf.yaml",
    }
    exclude_fields_from_roundtrip = {
        "10.5281/zenodo.7274275/8123818/rdf.yaml": {"inputs", "parent"},
    }

    @classmethod
    def yield_rdf_paths(cls):
        with open(pooch.retrieve(BASE_URL + "collection.json", None), encoding="utf-8") as f:  # type: ignore
            collection_data = json.load(f)["collection"]

        collection_registry: Dict[str, None] = {
            entry["rdf_source"].replace(RDF_BASE_URL, ""): None for entry in collection_data
        }
        collection = pooch.create(
            path=CACHE_PATH,
            base_url=RDF_BASE_URL,
            registry=collection_registry,
        )

        for rdf in collection_registry:
            yield Path(collection.fetch(rdf))
