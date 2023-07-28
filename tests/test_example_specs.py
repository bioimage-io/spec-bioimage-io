import datetime
from pathlib import Path
from typing import Any, ClassVar, Dict, Tuple
from unittest import TestCase

from pydantic import TypeAdapter, ValidationError
from ruamel.yaml import YAML

from bioimageio.spec import ResourceDescription
from bioimageio.spec.shared.validation import ValidationContext
from bioimageio.spec.utils import check_type_and_format_version

yaml = YAML(typ="safe")

CURRENT_DATE = str(datetime.datetime.now().date())
BASE_URL = "https://bioimage-io.github.io/collection-bioimage-io/"
RDF_BASE_URL = BASE_URL + "rdfs/"
RDF_FILE_NAME = "rdf.yaml"


class TestExamplesMeta(type):
    def __new__(cls, name: str, bases: Tuple[type, ...], dct: Dict[str, Any]):
        example_specs = Path(__file__).parent / "../example_specs"
        assert example_specs.exists(), example_specs
        for rdf in example_specs.glob("**/*.yaml"):
            if not rdf.name.startswith("invalid_rdf") and not rdf.name.startswith("rdf"):
                continue

            def test_rdf(self: "TestExamples", rdf_path: Path = example_specs / rdf) -> None:
                with rdf_path.open(encoding="utf-8") as f:
                    data = yaml.load(f)

                if rdf_path.stem.startswith("invalid"):
                    with self.assertRaises(ValidationError):
                        check_type_and_format_version(data)
                        with ValidationContext(root=rdf_path.parent):
                            self.adapter.validate_python(data)
                else:
                    try:
                        check_type_and_format_version(data)
                        with ValidationContext(root=rdf_path.parent):
                            self.adapter.validate_python(data)
                    except ValidationError as e:
                        self.fail(str(e))

            test_case_name: str = f"test_{rdf.stem}"
            test_rdf.__name__ = test_case_name
            dct[test_case_name] = test_rdf

        return super().__new__(cls, name, bases, dct)


class TestExamples(TestCase, metaclass=TestExamplesMeta):
    adapter: ClassVar[TypeAdapter[ResourceDescription]] = TypeAdapter(ResourceDescription)
