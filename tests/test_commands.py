from tempfile import TemporaryFile

from bioimageio.spec.shared import yaml


def test_validate_valid_model(unet2d_nuclei_broad_any_path):
    from bioimageio.spec.commands import validate

    rdf_source = unet2d_nuclei_broad_any_path

    assert validate(rdf_source, update_format=True, update_format_inner=False) == 0
    assert validate(rdf_source, update_format=False, update_format_inner=False) == 0


def test_validate_invalid_model(unet2d_nuclei_broad_latest_path):
    from bioimageio.spec.commands import validate

    data = yaml.load(unet2d_nuclei_broad_latest_path)
    del data["test_inputs"]  # invalidate data
    with TemporaryFile(mode="w") as f:
        yaml.dump(data, f)

        assert validate(f.name, update_format=True, update_format_inner=False) == 1
        assert validate(f.name, update_format=False, update_format_inner=False) == 1
