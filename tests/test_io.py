def test_get_resource_package_content(unet2d_nuclei_broad_latest, unet2d_nuclei_broad_url):
    from bioimageio.spec import get_resource_package_content

    from_local_content = get_resource_package_content(unet2d_nuclei_broad_latest)
    from_remote_content = get_resource_package_content(unet2d_nuclei_broad_url)
    local_keys = set(from_local_content)
    remote_keys = set(from_remote_content)
    assert local_keys == remote_keys
