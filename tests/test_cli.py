import os
import subprocess
import zipfile
from typing import Sequence

import pytest

from bioimageio.spec.io_ import (
    load_raw_resource_description,
    save_raw_resource_description,
    serialize_raw_resource_description,
)
from bioimageio.spec.shared import yaml

SKIP_ZENODO = True
SKIP_ZENODO_REASON = "zenodo api changes"


def run_subprocess(commands: Sequence[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", **kwargs)


def test_cli_validate_model(unet2d_nuclei_broad_latest):
    ret = run_subprocess(["bioimageio", "validate", str(unet2d_nuclei_broad_latest)])
    assert ret.returncode == 0


def test_cli_validate_model_url():
    ret = run_subprocess(
        [
            "bioimageio",
            "validate",
            "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/rdf.yaml",
        ]
    )
    assert ret.returncode == 0


def test_cli_validate_model_url_wo_cache():
    env = os.environ.copy()
    env["BIOIMAGEIO_USE_CACHE"] = "false"
    ret = run_subprocess(
        [
            "bioimageio",
            "validate",
            "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/rdf.yaml",
        ],
        env=env,
    )
    assert ret.returncode == 0


@pytest.mark.skipif(SKIP_ZENODO, reason=SKIP_ZENODO_REASON)
def test_cli_validate_model_doi():
    ret = run_subprocess(["bioimageio", "validate", "10.5281/zenodo.5744489"])
    assert ret.returncode == 0


def test_cli_validate_model_package(unet2d_nuclei_broad_latest, tmpdir):
    zf_path = tmpdir / "package.zip"

    # load from path and serialize with absolute paths
    raw_rd = load_raw_resource_description(unet2d_nuclei_broad_latest)
    rdf_str = serialize_raw_resource_description(raw_rd, convert_absolute_paths=False)

    with zipfile.ZipFile(zf_path, "w") as zf:
        zf.writestr("rdf.yaml", rdf_str)

    ret = run_subprocess(["bioimageio", "validate", str(zf_path)])
    assert ret.returncode == 0


def test_cli_validate_model_package_wo_cache(unet2d_nuclei_broad_latest, tmpdir):
    env = os.environ.copy()
    env["BIOIMAGEIO_USE_CACHE"] = "false"

    # load from path and serialize with absolute paths
    raw_rd = load_raw_resource_description(unet2d_nuclei_broad_latest)
    rdf_str = serialize_raw_resource_description(raw_rd, convert_absolute_paths=False)

    zf_path = tmpdir / "package.zip"
    with zipfile.ZipFile(zf_path, "w") as zf:
        zf.writestr("rdf.yaml", rdf_str)

    ret = run_subprocess(["bioimageio", "validate", str(zf_path)], env=env)
    assert ret.returncode == 0


def test_cli_update_format(unet2d_nuclei_broad_before_latest, tmp_path):
    in_path = tmp_path / "rdf.yaml"
    save_raw_resource_description(load_raw_resource_description(unet2d_nuclei_broad_before_latest), in_path)
    assert in_path.exists()
    path = tmp_path / "rdf_new.yaml"
    ret = run_subprocess(["bioimageio", "update-format", str(in_path), str(path)])
    assert ret.returncode == 0
    assert path.exists()


def test_update_rdf(unet2d_nuclei_broad_base_path, tmp_path):
    in_path = unet2d_nuclei_broad_base_path / "rdf.yaml"
    assert in_path.exists()
    update_path = tmp_path / "update.yaml"
    assert yaml is not None
    yaml.dump(dict(name="updated", outputs=[{"name": "updated", "halo": ["KEEP", "DROP", 0, 9, 9]}]), update_path)
    out_path = tmp_path / "output.yaml"
    ret = run_subprocess(["bioimageio", "update-rdf", str(in_path), str(update_path), str(out_path)])
    assert ret.returncode == 0
    actual = yaml.load(out_path)
    assert actual["name"] == "updated"
    assert actual["outputs"][0]["name"] == "updated"
    assert actual["outputs"][0]["halo"] == [0, 0, 9, 9]
