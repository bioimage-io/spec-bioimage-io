def test_v0_1(rf_config_path_v0_1):
    from bioimageio.spec.v0_1 import schema

    schema.Model()

    rf_config_path_v0_1
