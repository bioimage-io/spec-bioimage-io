import pathlib
import subprocess
import zipfile


def test_cli_validate_model(unet2d_nuclei_broad_latest_path):
    assert unet2d_nuclei_broad_latest_path.exists()
    ret = subprocess.run(["bioimageio", "validate", str(unet2d_nuclei_broad_latest_path)])
    assert ret.returncode == 0


def test_cli_validate_model_package(unet2d_nuclei_broad_latest_path, tmpdir):
    zf_path = pathlib.Path(tmpdir / "package.zip")
    with zipfile.ZipFile(zf_path, "w") as zf:
        zf.write(unet2d_nuclei_broad_latest_path, "rdf.yaml")

    assert zf_path.exists()
    ret = subprocess.run(["bioimageio", "validate", str(zf_path)])
    assert ret.returncode == 0
