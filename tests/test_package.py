from pathlib import Path


def test_packaging(unet2d_path: Path):
    from bioimageio.spec import save_bioimageio_package

    package_path = save_bioimageio_package(unet2d_path)
    assert package_path.exists()
