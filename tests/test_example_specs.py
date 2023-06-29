from pathlib import Path
from typing import Any, Dict, Optional, Type

from ruamel.yaml import YAML

import bioimageio.spec
from bioimageio.spec.shared.nodes import Node
from tests.unittest_utils import BaseTestCases, Invalid, Valid

yaml = YAML(typ="safe")


class TestExampleSpecs(BaseTestCases.TestNode):
    DEBUG_SUBTEST_NAME: Optional[str] = None  # "unet2d_nuclei_broad_col/rdf.yaml"  # limit subtests for debugging

    def __init__(self, methodName: str = "runTest") -> None:
        example_specs = Path(__file__).parent / "../example_specs"
        assert example_specs.exists(), example_specs
        self.sub_tests = []
        for rdf in example_specs.glob("**/*.yaml"):
            if rdf.name in ("environment.yaml",):
                continue

            assert rdf.name.startswith("invalid_rdf") or rdf.name.startswith("rdf"), rdf.name
            with rdf.open(encoding="utf-8") as f:
                data: Dict[str, Any] = yaml.load(f)
                assert isinstance(data, dict)
                assert all(isinstance(k, str) for k in data)
                typ = data["type"]
                if hasattr(bioimageio.spec, typ):
                    node_class: Type[Node] = getattr(getattr(bioimageio.spec, typ), typ.capitalize())
                else:
                    node_class = bioimageio.spec.generic.GenericDescription

                if rdf.name.startswith("rdf"):
                    st_class = Valid
                else:
                    st_class = Invalid

                name = str(rdf.relative_to(example_specs).as_posix())
                if self.DEBUG_SUBTEST_NAME is not None and self.DEBUG_SUBTEST_NAME != name:
                    continue
                self.sub_tests.append(
                    st_class(
                        kwargs=data,
                        name=name,
                        context=dict(root=rdf.parent),
                        node_class=node_class,
                    )
                )

        assert self.sub_tests, "failed to generate any subtests"
        super().__init__(methodName)
