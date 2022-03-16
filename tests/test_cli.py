import os
import subprocess
import zipfile

from bioimageio.spec.io_ import load_raw_resource_description, save_raw_resource_description


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
    env["BIOIMAGEIO_NO_CACHE"] = "True"
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


def test_cli_update_format(unet2d_nuclei_broad_before_latest, tmp_path):
    in_path = tmp_path / "rdf.yaml"
    save_raw_resource_description(load_raw_resource_description(unet2d_nuclei_broad_before_latest), in_path)
    assert in_path.exists()
    path = tmp_path / "rdf_new.yaml"
    ret = subprocess.run(["bioimageio", "update-format", str(in_path), str(path)])
    assert ret.returncode == 0
    assert path.exists()
