import pathlib

import pytest

from bioimageio.spec.shared import yaml


@pytest.fixture
def unet2d_nuclei_broad_base_path():
    return pathlib.Path(__file__).parent / "../example_specs/models/unet2d_nuclei_broad"


def get_unet2d_nuclei_broad(unet2d_nuclei_broad_base_path, request) -> dict:
    if request.param == "v0_4_1":
        v = ""
    else:
        v = f"_{request.param}"

    f_name = f"rdf{v}.yaml"
    path = unet2d_nuclei_broad_base_path / f_name
    return yaml.load(path)


@pytest.fixture(params=["v0_1_0", "v0_3_0", "v0_3_1", "v0_3_2", "v0_3_3", "v0_3_4", "v0_4_0", "v0_4_1"])
def unet2d_nuclei_broad_any(unet2d_nuclei_broad_base_path, request):
    yield get_unet2d_nuclei_broad(unet2d_nuclei_broad_base_path, request)


@pytest.fixture(params=["v0_1_0", "v0_3_0", "v0_3_1", "v0_3_2", "v0_3_3", "v0_3_4", "v0_4_0"])
def unet2d_nuclei_broad_before_latest(unet2d_nuclei_broad_base_path, request):
    yield get_unet2d_nuclei_broad(unet2d_nuclei_broad_base_path, request)


@pytest.fixture(params=["v0_4_1"])
def unet2d_nuclei_broad_latest(unet2d_nuclei_broad_base_path, request):
    yield get_unet2d_nuclei_broad(unet2d_nuclei_broad_base_path, request)


@pytest.fixture(params=["v0_1_0", "v0_3_4", "v0_4_1"])
def unet2d_nuclei_broad_any_minor(unet2d_nuclei_broad_base_path, request):
    yield get_unet2d_nuclei_broad(unet2d_nuclei_broad_base_path, request)


@pytest.fixture
def unet2d_nuclei_broad_latest_path(unet2d_nuclei_broad_base_path):
    return unet2d_nuclei_broad_base_path / "rdf.yaml"


@pytest.fixture
def invalid_rdf_v0_4_0_duplicate_tensor_names(unet2d_nuclei_broad_base_path):
    return yaml.load(unet2d_nuclei_broad_base_path / "invalid_rdf_v0_4_0_duplicate_tensor_names.yaml")


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
def hpa_model():
    return pathlib.Path(__file__).parent / "../example_specs/models/hpa-densenet/rdf.yaml"


@pytest.fixture
def stardist_model():
    return pathlib.Path(__file__).parent / "../example_specs/models/stardist_example_model/rdf.yaml"


@pytest.fixture
def unet2d_keras_tf():
    return pathlib.Path(__file__).parent / "../example_specs/models/unet2d_keras_tf/rdf.yaml"
