from pathlib import Path

import pytest
from ruamel.yaml import YAML


yaml = YAML(typ="safe")


#
# pytorch unet2d model (broad nuclei model)
# containse pytorch_saved_dict, pytoch_script and onnx weights
#
# version 0.1 model

@pytest.fixture
def unet2d_pytorch_model_v01():
    return Path(__file__).parent / "../specs/models/unet2d-pytorch/v01"


# version 0.3 models

@pytest.fixture
def unet2d_pytorch_model_v030():
    return Path(__file__).parent / "../specs/models/unet2d-pytorch/v030/UNet2DNucleiBroad.model.yaml"


@pytest.fixture
def unet2d_pytorch_model_v031():
    return Path(__file__).parent / "../specs/models/unet2d-pytorch/v031"


@pytest.fixture
def unet2d_pytorch_model_v032():
    return Path(__file__).parent / "../specs/models/unet2d-pytorch/v032"


# latest version

@pytest.fixture
def unet2d_pytorch_model(unet2d_pytorch_model_v030):
    # return unet2d_pytorch_model_v032
    return unet2d_pytorch_model_v030

@pytest.fixture
def default_model(unet2d_pytorch_model):
    return unet2d_pytorch_model


# move this model here as well?
#
# pytorch unet2d model (broad nuclei model)
# contains tensorflow_model_bundle, keras_hdf and tensorflow_js weights
# current version is 0.3.0
#

@pytest.fixture
def FruNet_model_url():
    return "https://raw.githubusercontent.com/deepimagej/models/master/fru-net_sev_segmentation/model.yaml"
