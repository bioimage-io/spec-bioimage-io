from tempfile import TemporaryFile

from bioimageio.spec.shared import yaml


def test_validate_valid_model(unet2d_nuclei_broad_any_path):
    from bioimageio.spec.__main__ import _validate

    rdf_source = unet2d_nuclei_broad_any_path

    assert _validate(rdf_source, auto_convert=True, auto_convert_inner=False) == 0
    assert _validate(rdf_source, auto_convert=False, auto_convert_inner=False) == 0


def test_validate_invalid_model(unet2d_nuclei_broad_latest_path):
    from bioimageio.spec.__main__ import _validate

    data = yaml.load(unet2d_nuclei_broad_latest_path)
    del data["test_inputs"]  # invalidate data
    with TemporaryFile(mode="w") as f:
        yaml.dump(data, f)

        assert _validate(f.name, auto_convert=True, auto_convert_inner=False) == 1
        assert _validate(f.name, auto_convert=False, auto_convert_inner=False) == 1
