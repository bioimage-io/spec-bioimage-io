import os
import subprocess
import zipfile

from bioimageio.spec.io_ import load_raw_resource_description, save_raw_resource_description
from bioimageio.spec.shared import yaml


def test_cli_validate_model(unet2d_nuclei_broad_latest_path):
    ret = subprocess.run(["bioimageio", "validate", str(unet2d_nuclei_broad_latest_path)])
    assert ret.returncode == 0


def test_cli_validate_model_url():
    ret = subprocess.run(
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
    ret = subprocess.run(
        [
            "bioimageio",
            "validate",
            "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/rdf.yaml",
        ],
        env=env,
    )
    assert ret.returncode == 0


def test_cli_validate_model_doi():
    ret = subprocess.run(["bioimageio", "validate", "10.5281/zenodo.5744489"])
    assert ret.returncode == 0


def test_cli_validate_model_package(unet2d_nuclei_broad_latest_path, tmpdir):
    zf_path = tmpdir / "package.zip"
    with zipfile.ZipFile(zf_path, "w") as zf:
        zf.write(unet2d_nuclei_broad_latest_path, "rdf.yaml")

    ret = subprocess.run(["bioimageio", "validate", str(zf_path)])
    assert ret.returncode == 0


def test_cli_validate_model_package_wo_cache(unet2d_nuclei_broad_latest_path, tmpdir):
    env = os.environ.copy()
    env["BIOIMAGEIO_USE_CACHE"] = "false"

    zf_path = tmpdir / "package.zip"
    with zipfile.ZipFile(zf_path, "w") as zf:
        zf.write(unet2d_nuclei_broad_latest_path, "rdf.yaml")

    ret = subprocess.run(["bioimageio", "validate", str(zf_path)], env=env)
    assert ret.returncode == 0


def test_cli_update_format(unet2d_nuclei_broad_before_latest, tmp_path):
    in_path = tmp_path / "rdf.yaml"
    save_raw_resource_description(load_raw_resource_description(unet2d_nuclei_broad_before_latest), in_path)
    assert in_path.exists()
    path = tmp_path / "rdf_new.yaml"
    ret = subprocess.run(["bioimageio", "update-format", str(in_path), str(path)])
    assert ret.returncode == 0
    assert path.exists()


def test_update_rdf(unet2d_nuclei_broad_base_path, tmp_path):
    in_path = unet2d_nuclei_broad_base_path / "rdf.yaml"
    assert in_path.exists()
    update_path = tmp_path / "update.yaml"
    yaml.dump(dict(name="updated", outputs=[{"name": "updated", "halo": ["KEEP", "DROP", 0, 9, 9]}]), update_path)
    out_path = tmp_path / "output.yaml"
    ret = subprocess.run(["bioimageio", "update-rdf", str(in_path), str(update_path), str(out_path)])
    assert ret.returncode == 0
    actual = yaml.load(out_path)
    assert actual["name"] == "updated"
    assert actual["outputs"][0]["name"] == "updated"
    assert actual["outputs"][0]["halo"] == [0, 0, 9, 9]
