import pathlib

import pytest


@pytest.fixture
def unet2d_nuclei_broad_base_path():
    return pathlib.Path(__file__).parent / "../example_specs/models/unet2d_nuclei_broad"


def get_unet2d_nuclei_broad(unet2d_nuclei_broad_base_path, request) -> dict:
    if request.param == "v0_4_5":
        v = ""
    else:
        v = f"_{request.param}"

    f_name = f"rdf{v}.yaml"
    return unet2d_nuclei_broad_base_path / f_name


@pytest.fixture(params=["v0_3_0", "v0_3_1", "v0_3_2", "v0_3_3", "v0_3_6", "v0_4_0", "v0_4_5"])
def unet2d_nuclei_broad_any(unet2d_nuclei_broad_base_path, request):
    yield get_unet2d_nuclei_broad(unet2d_nuclei_broad_base_path, request)


@pytest.fixture(params=["v0_3_0", "v0_3_1", "v0_3_2", "v0_3_3", "v0_3_6", "v0_4_0"])
def unet2d_nuclei_broad_before_latest(unet2d_nuclei_broad_base_path, request):
    yield get_unet2d_nuclei_broad(unet2d_nuclei_broad_base_path, request)


@pytest.fixture(params=["v0_4_5"])
def unet2d_nuclei_broad_latest(unet2d_nuclei_broad_base_path, request):
    yield get_unet2d_nuclei_broad(unet2d_nuclei_broad_base_path, request)


@pytest.fixture(params=["v0_3_6", "v0_4_5"])
def unet2d_nuclei_broad_any_minor(unet2d_nuclei_broad_base_path, request):
    yield get_unet2d_nuclei_broad(unet2d_nuclei_broad_base_path, request)


@pytest.fixture
def invalid_rdf_v0_4_0_duplicate_tensor_names(unet2d_nuclei_broad_base_path):
    return unet2d_nuclei_broad_base_path / "invalid_rdf_v0_4_0_duplicate_tensor_names.yaml"


@pytest.fixture
def unet2d_nuclei_broad_collection():
    return pathlib.Path(__file__).parent / "../example_specs/collections/unet2d_nuclei_broad_coll/rdf.yaml"


@pytest.fixture
def partner_collection():
    return pathlib.Path(__file__).parent / "../example_specs/collections/partner_collection/rdf.yaml"


@pytest.fixture
def unet2d_nuclei_broad_url():
    return "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/rdf.yaml"


@pytest.fixture
def FruNet_model_url():
    return "https://raw.githubusercontent.com/deepimagej/models/master/fru-net_sev_segmentation/model.yaml"


@pytest.fixture
def unet2d_diff_output_shape():
    return pathlib.Path(__file__).parent / "../example_specs/models/unet2d_diff_output_shape/rdf.yaml"


@pytest.fixture
def unet2d_fixed_shape():
    return pathlib.Path(__file__).parent / "../example_specs/models/unet2d_fixed_shape/rdf.yaml"


@pytest.fixture
def unet2d_multi_tensor():
    return pathlib.Path(__file__).parent / "../example_specs/models/unet2d_multi_tensor/rdf.yaml"


@pytest.fixture
def unet2d_expanded_output_shape():
    return pathlib.Path(__file__).parent / "../example_specs/models/unet2d_nuclei_broad/rdf_expand_output_shape.yaml"


@pytest.fixture
def hpa_model():
    return pathlib.Path(__file__).parent / "../example_specs/models/hpa-densenet/rdf.yaml"


@pytest.fixture
def stardist_model():
    return pathlib.Path(__file__).parent / "../example_specs/models/stardist_example_model/rdf.yaml"


@pytest.fixture
def unet2d_keras_tf():
    return pathlib.Path(__file__).parent / "../example_specs/models/unet2d_keras_tf/rdf.yaml"


@pytest.fixture
def dataset_rdf():
    return pathlib.Path(__file__).parent / "../example_specs/datasets/covid_if_training_data/rdf.yaml"
