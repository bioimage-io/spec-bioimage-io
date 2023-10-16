import pathlib

import pytest

from bioimageio.spec.shared import yaml

SKIP_ZENODO = True
SKIP_ZENODO_REASON = "zenodo api changes"


def test_get_resource_package_content(unet2d_nuclei_broad_latest, unet2d_nuclei_broad_url):
    from bioimageio.spec import get_resource_package_content

    from_local_content = get_resource_package_content(unet2d_nuclei_broad_latest)
    from_remote_content = get_resource_package_content(unet2d_nuclei_broad_url)
    local_keys = set(from_local_content)
    remote_keys = set(from_remote_content)
    assert local_keys == remote_keys


@pytest.mark.skipif(SKIP_ZENODO, reason=SKIP_ZENODO_REASON)
def test_load_animal_nickname():
    from bioimageio.spec import load_raw_resource_description
    from bioimageio.spec.model.v0_4.raw_nodes import Model as Model04

    nickname = "impartial-shrimp"
    model = load_raw_resource_description(nickname)
    assert isinstance(model, Model04)
    assert ".".join(model.format_version.split(".")[:2]) == "0.4"
    assert model.config["bioimageio"]["nickname"] == nickname


def test_resolve_download_url(unet2d_nuclei_broad_latest):
    from bioimageio.spec import load_raw_resource_description
    from bioimageio.spec.model.v0_4.raw_nodes import Model as Model04

    assert yaml is not None
    data = yaml.load(unet2d_nuclei_broad_latest)
    data["root_path"] = unet2d_nuclei_broad_latest.parent  # set root path manually as we load from the manipulated dict
    data["download_url"] = "relative_path_to.zip"

    model = load_raw_resource_description(data)
    assert isinstance(model, Model04)
    assert isinstance(model.download_url, pathlib.Path)
