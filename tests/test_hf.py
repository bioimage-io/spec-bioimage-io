from pathlib import Path

from bioimageio.spec import load_model_description
from bioimageio.spec.model.v0_5 import ModelId


def test_hf(unet2d_path: Path):
    from bioimageio.spec._hf import push_to_hub

    my_model = load_model_description(unet2d_path, format_version="latest")
    my_model.id = ModelId("unet2d_nuclei_broad")
    push_to_hub(my_model, "thefynnbe", prep_only_no_upload=True)
