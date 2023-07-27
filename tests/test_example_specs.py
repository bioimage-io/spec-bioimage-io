import datetime
import json
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Tuple
from unittest import TestCase

import pooch  # type: ignore
from pydantic import HttpUrl, TypeAdapter, ValidationError
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
            if rdf.name in ("environment.yaml",):
                continue

            assert rdf.name.startswith("invalid_rdf") or rdf.name.startswith("rdf"), rdf.name

        for rdf in collection_registry:

            def test_rdf(self: "TestExamples", rdf_: str = rdf) -> None:
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


class TestExamples(TestCase, metaclass=TestExamplesMeta):
    adapter: ClassVar[TypeAdapter[ResourceDescription]] = TypeAdapter(ResourceDescription)


# from pathlib import Path
# from typing import Any, Dict, Optional, Type

# from ruamel.yaml import YAML

# import bioimageio.spec
# from bioimageio.spec.shared.nodes import Node
# from bioimageio.spec.shared.validation import ValidationContext
# from tests.unittest_utils import BaseTestCases, Invalid, Valid

# yaml = YAML(typ="safe")


# class TestExampleSpecs(BaseTestCases.TestNode):
#     DEBUG_SUBTEST_NAME: Optional[
#         str
#     ] = "models/stardist_example_model/invalid_rdf_wrong_shape.yaml"  # None  # "models/unet2d_nuclei_broad_col/rdf.yaml"  # limit subtests for debugging

#     def __init__(self, methodName: str = "runTest") -> None:
#         example_specs = Path(__file__).parent / "../example_specs"
#         assert example_specs.exists(), example_specs
#         self.sub_tests = []
#         for rdf in example_specs.glob("**/*.yaml"):
#             if rdf.name in ("environment.yaml",):
#                 continue

#             assert rdf.name.startswith("invalid_rdf") or rdf.name.startswith("rdf"), rdf.name
#             with rdf.open(encoding="utf-8") as f:
#                 data: Dict[str, Any] = yaml.load(f)
#                 assert isinstance(data, dict)
#                 assert all(isinstance(k, str) for k in data)
#                 typ = data["type"]
#                 fv_module = f"v{'_'.join(data['format_version'].split('.')[:2])}"
#                 if hasattr(bioimageio.spec, typ):
#                     node_class: Type[Node] = getattr(
#                         getattr(getattr(bioimageio.spec, typ), fv_module), typ.capitalize()
#                     )
#                 else:
#                     node_class = getattr(bioimageio.spec.generic, fv_module).Generic

#                 if rdf.name.startswith("rdf"):
#                     st_class = Valid
#                 else:
#                     st_class = Invalid

#                 name = str(rdf.relative_to(example_specs).as_posix())
#                 if self.DEBUG_SUBTEST_NAME is not None and self.DEBUG_SUBTEST_NAME != name:
#                     continue
#                 self.sub_tests.append(
#                     st_class(
#                         kwargs=data,
#                         name=name,
#                         context=ValidationContext(root=rdf.parent),
#                         node_class=node_class,
#                     )
#                 )

#         assert self.sub_tests, "failed to generate any subtests"
#         super().__init__(methodName)
