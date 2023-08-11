from pathlib import Path

from tests.unittest_utils import TestBases

EXAMPLE_SPECS = Path(__file__).parent / "../example_specs"


class TestExamples(TestBases.TestManyRdfs):
    rdf_root = EXAMPLE_SPECS
    exclude_fields_from_roundtrip = {
        Path("models/stardist_example_model/rdf_v0_4.yaml"): {"dependencies"},
        Path("models/stardist_example_model/rdf_wrong_shape_v0_4.yaml"): {"dependencies"},
        Path("models/stardist_example_model/rdf_wrong_shape2_v0_4.yaml"): {"dependencies"},
        Path("models/unet2d_diff_output_shape/rdf_v0_4.yaml"): {
            "dependencies",
            "weights",
        },
        Path("models/unet2d_multi_tensor/rdf_v0_4.yaml"): {"dependencies", "weights"},
        Path("models/unet2d_multi_tensor/rdf_v0_4.yaml"): {"dependencies", "weights"},
        Path("models/unet2d_nuclei_broad/rdf_v0_4_0.yaml"): {
            "dependencies",
            "weights",
        },
        Path("models/upsample_test_model/rdf_v0_4.yaml"): {"dependencies", "weights"},
    }
