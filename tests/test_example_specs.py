from pathlib import Path

from tests.unittest_utils import TestBases

EXAMPLE_SPECS = Path(__file__).parent / "../example_specs"


class TestExamples(TestBases.TestManyRdfs):
    rdf_root = EXAMPLE_SPECS
