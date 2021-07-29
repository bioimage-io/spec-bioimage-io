from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile


def test_export_package(unet2d_nuclei_broad_v0_3_path):
    from bioimageio.spec import export_resource_package

    package_path = export_resource_package(unet2d_nuclei_broad_v0_3_path, weights_priority_order=["onnx"])
    assert isinstance(package_path, Path), package_path
    assert package_path.exists(), package_path

    from bioimageio.spec import load_raw_resource_description

    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        with ZipFile(package_path) as zf:
            zf.extractall(tmp_dir)

        raw_model = load_raw_resource_description(tmp_dir / "rdf.yaml")
        assert (tmp_dir / raw_model.documentation).exists()
