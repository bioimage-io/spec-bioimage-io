def test_format_version_matches_library():
    from bioimageio.spec import __version__
    from bioimageio.spec.model import ModelDescr

    lib_format_version = ".".join(__version__.split(".")[:3])
    assert ModelDescr.implemented_format_version == lib_format_version, (
        ModelDescr.implemented_format_version,
        __version__,
    )
