def test_load_raw_v0_1(unet2d_nuclei_broad_v0_1_path):
    from bioimageio.spec.v0_1 import load_raw_node

    raw_model = load_raw_node(unet2d_nuclei_broad_v0_1_path)
    assert (unet2d_nuclei_broad_v0_1_path.parent / raw_model.documentation).exists()


def test_load_v0_1(unet2d_nuclei_broad_v0_1_path):
    from bioimageio.spec.v0_1 import load_node

    model = load_node(unet2d_nuclei_broad_v0_1_path)
    assert model.documentation.exists()
