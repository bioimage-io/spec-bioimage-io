from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

import bioimageio.spec
from bioimageio.spec.shared.nodes import Node
from tests.unittest_utils import BaseTestCases, Invalid, SubTest, Valid

yaml = YAML(typ="safe")


class TestExampleSpecs(BaseTestCases.TestNode):
    def __init__(self, methodName: str = "runTest") -> None:
        example_specs = Path(__file__).parent / "../example_specs"
        assert example_specs.exists(), example_specs
        self.sub_tests = []
        for rdf in example_specs.glob("**/*.yaml"):
            if rdf.name in ("environment.yaml",):
                continue

            assert rdf.name.startswith("invalid_rdf") or rdf.name.startswith("rdf"), rdf.name
            with rdf.open(encoding="utf-8") as f:
                data: dict[str, Any] = yaml.load(f)
                assert isinstance(data, dict)
                assert all(isinstance(k, str) for k in data)
                typ = data["type"]
                if hasattr(bioimageio.spec, typ):
                    node_class: type[Node] = getattr(getattr(bioimageio.spec, typ), typ.capitalize())
                else:
                    node_class = bioimageio.spec.generic.GenericDescription

                if rdf.name.startswith("rdf"):
                    st_class = Valid
                else:
                    st_class = Invalid

                self.sub_tests.append(
                    st_class(
                        kwargs=data,
                        name=str(rdf.relative_to(rdf.parent.parent)),
                        context=dict(root=rdf.parent),
                        node_class=node_class,
                    )
                )

        assert self.sub_tests, "failed to generate any subtests"
        super().__init__(methodName)
