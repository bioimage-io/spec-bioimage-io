import datetime
import json
from pathlib import Path
from typing import Any, ClassVar, Dict, Tuple
from unittest import TestCase

import pooch  # type: ignore
from pydantic import HttpUrl, TypeAdapter, ValidationError
from ruamel.yaml import YAML

from bioimageio.spec import ResourceDescription
from bioimageio.spec.shared.validation import ValidationContext
from bioimageio.spec.utils import check_type_and_format_version

yaml = YAML(typ="safe")

WEEK = f"{datetime.datetime.now().year}week{datetime.datetime.now().isocalendar()[1]}"
BASE_URL = "https://bioimage-io.github.io/collection-bioimage-io/"
RDF_BASE_URL = BASE_URL + "rdfs/"
RDF_FILE_NAME = "rdf.yaml"
CACHE_PATH = Path(__file__).parent / "cache" / WEEK


class TestBioimageioCollectionMeta(type):
    def __new__(cls, name: str, bases: Tuple[type, ...], dct: Dict[str, Any]):
        with open(pooch.retrieve(BASE_URL + "collection.json", None), encoding="utf-8") as f:  # type: ignore
            collection_data = json.load(f)["collection"]

        collection_registry: Dict[str, None] = {
            entry["rdf_source"].replace(RDF_BASE_URL, ""): None for entry in collection_data
        }
        collection = pooch.create(  # type: ignore
            path=CACHE_PATH,
            base_url=RDF_BASE_URL,
            registry=collection_registry,
        )

        for rdf in collection_registry:

            def test_rdf(self: "TestBioimageioCollection", rdf_: str = rdf) -> None:
                rdf_path = Path(collection.fetch(rdf_))  # type: ignore
                with rdf_path.open(encoding="utf-8") as f:
                    data = yaml.load(f)

                try:
                    check_type_and_format_version(data)
                    with ValidationContext(root=HttpUrl(BASE_URL + rdf_[: -len(RDF_FILE_NAME)])):
                        self.adapter.validate_python(data)
                except ValidationError as e:
                    self.fail(str(e))

            assert rdf.endswith("/" + RDF_FILE_NAME)
            rdf_name = rdf[: -(len(RDF_FILE_NAME) + 1)].replace(".", "_").replace("/", "_")
            test_case_name: str = f"test_{rdf_name}"
            test_rdf.__name__ = test_case_name
            dct[test_case_name] = test_rdf

        return super().__new__(cls, name, bases, dct)


class TestBioimageioCollection(TestCase, metaclass=TestBioimageioCollectionMeta):
    adapter: ClassVar[TypeAdapter[ResourceDescription]] = TypeAdapter(ResourceDescription)
