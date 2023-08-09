from pathlib import Path

from tests.unittest_utils import TestBases

EXAMPLE_SPECS = Path(__file__).parent / "../example_specs"


class TestExamples(TestBases.TestManyRdfs):
    rdf_root = EXAMPLE_SPECS
    known_invalid_as_latest = {Path("models/stardist_example_model/rdf_v0_4.yaml")}
    exclude_fields_from_roundtrip = {Path("models/stardist_example_model/rdf_v0_4.yaml"): {"dependencies"}}
