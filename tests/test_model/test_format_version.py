def test_format_version_matches_library():
    from bioimageio.spec import __version__
    from bioimageio.spec.model import ModelDescr

    version_wo_post = __version__.split("post")[0]
    assert ModelDescr.implemented_format_version == version_wo_post, (
        ModelDescr.implemented_format_version,
        __version__,
    )
