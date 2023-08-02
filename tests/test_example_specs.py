from pathlib import Path

from tests.unittest_utils import BaseTestCases

EXAMPLE_SPECS = Path(__file__).parent / "../example_specs"


class TestExamples(BaseTestCases.TestManyRdfs):
    rdf_root = EXAMPLE_SPECS
