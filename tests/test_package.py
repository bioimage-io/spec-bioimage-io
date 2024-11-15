import io
import shutil
from pathlib import Path

from deepdiff import DeepDiff

from bioimageio.spec.model import v0_5


def test_package(unet2d_path: Path):
    from bioimageio.spec import dump_description, load_description

    descr = load_description(unet2d_path)
    rdf1 = dump_description(descr)
    zip = descr.package()
    descr2 = load_description(zip)
    rdf2 = dump_description(descr2)

    # assert expected differences
    assert (
        rdf1["weights"]["pytorch_state_dict"].pop("source")  # type: ignore
        == "https://zenodo.org/records/3446812/files/unet2d_weights.torch"
    )
    assert (
        rdf2["weights"]["pytorch_state_dict"].pop("source")  # type: ignore
        == "unet2d_weights.torch"
    )

    diff = DeepDiff(rdf1, rdf2)
    assert not diff, diff.pretty()


def test_save_bioimageio_package(unet2d_path: Path):
    from bioimageio.spec import save_bioimageio_package

    package_path = save_bioimageio_package(unet2d_path)
    assert package_path.exists()


def test_save_bioimageio_package_to_stream(unet2d_path: Path):
    from bioimageio.spec import save_bioimageio_package_to_stream

    output_stream = io.BytesIO()
    stream = save_bioimageio_package_to_stream(unet2d_path, output_stream=output_stream)
    assert isinstance(stream, io.BytesIO)
    assert stream == output_stream


def test_save_bioimageio_package_to_stream_default(unet2d_path: Path):
    from bioimageio.spec import save_bioimageio_package_to_stream

    stream = save_bioimageio_package_to_stream(unet2d_path)
    assert isinstance(stream, io.BytesIO)


def test_save_bioimageio_package_as_folder(unet2d_path: Path, tmp_path: Path):
    from bioimageio.spec import load_description, save_bioimageio_package_as_folder

    package_folder = tmp_path / "package"
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
    altered_package = tmp_path / "altered_package"
    altered_package = save_bioimageio_package_as_folder(
        model, output_path=altered_package, weights_priority_order=["onnx"]
    )
    assert (altered_package / new_doc).exists(), altered_package / new_doc

    # load altered package
    reloaded_model = load_description(altered_package)
    assert isinstance(reloaded_model, v0_5.ModelDescr)
    assert str(reloaded_model.documentation).startswith("copy_")
