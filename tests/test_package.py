import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from bioimageio.spec.model import v0_5


def test_save_bioimageio_package(unet2d_path: Path):
    from bioimageio.spec import save_bioimageio_package

    package_path = save_bioimageio_package(unet2d_path)
    assert package_path.exists()


def test_save_bioimageio_package_as_folder(unet2d_path: Path):
    from bioimageio.spec import load_description, save_bioimageio_package_as_folder

    with TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)

        package_folder = tmp_dir / "package"
        _ = save_bioimageio_package_as_folder(unet2d_path, output_path=package_folder)

        # load package
        model = load_description(package_folder)
        assert isinstance(model, v0_5.ModelDescr)

        # alter package
        doc = model.documentation
        assert isinstance(doc, v0_5.RelativeFilePath)
        new_doc = f"copy_{doc}"
        shutil.move(str(package_folder / str(doc)), str(package_folder / new_doc))
        model.documentation = package_folder / new_doc

        # export altered package
        altered_package = tmp_dir / "altered_package"
        altered_package = save_bioimageio_package_as_folder(
            model, output_path=altered_package, weights_priority_order=["onnx"]
        )
        assert (altered_package / new_doc).exists(), altered_package / new_doc

        # load altered package
        reloaded_model = load_description(altered_package)
        assert isinstance(reloaded_model, v0_5.ModelDescr)
        assert str(reloaded_model.documentation).startswith("copy_")
