def test_load_raw_model(unet2d_nuclei_broad_any):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_nuclei_broad_any)
    assert raw_model


def test_load_raw_model_fixed_shape(unet2d_fixed_shape):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_fixed_shape)
    assert raw_model


def test_load_raw_model_diff_output_shape(unet2d_diff_output_shape):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_diff_output_shape)
    assert raw_model


def test_load_raw_model_multi_tensor(unet2d_multi_tensor):
    from bioimageio.spec import load_raw_resource_description

    raw_model = load_raw_resource_description(unet2d_multi_tensor)
    assert raw_model
