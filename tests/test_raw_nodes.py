import pathlib
from datetime import datetime

import pytest


def test_uri():
    from bioimageio.spec.shared.raw_nodes import URI

    uri_from_string = URI("https://john.doe@www.example.com:123/forum/questions/?tag=networking&order=newest#top")
    uri = URI(
        scheme="https",
        authority="john.doe@www.example.com:123",
        path="/forum/questions/",
        query="tag=networking&order=newest",
        fragment="top",
    )

    assert str(uri_from_string) == str(uri)
    assert uri_from_string == uri


def test_uri_is_relative_path():
    from bioimageio.spec.shared.raw_nodes import URI

    uri_from_string = URI("forum/questions/")
    uri = URI(path="forum/questions/")

    assert str(uri_from_string) == str(uri)
    assert uri_from_string == uri


def test_uri_is_absolute_path():
    from bioimageio.spec.shared.raw_nodes import URI

    with pytest.raises(ValueError):
        URI("/forum/questions/")

    with pytest.raises(ValueError):
        URI(path="/forum/questions/")


def test_uri_is_url():
    from bioimageio.spec.shared.raw_nodes import URI

    url = "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/test_input.npy"
    uri = URI(url)
    assert str(uri) == url


def test_general_rdf_accepts_unknown_fields():
    from bioimageio.spec.rdf.raw_nodes import RDF

    RDF(
        format_version="0.2.0",
        name="test_rdf",
        authors=[],
        cite=[],
        description="description text",
        documentation=pathlib.Path("README.md"),
        links=[],
        tags=[],
        unknown_weird_test_field="shouldn't be here",
    )


def test_model_does_not_accept_unknown_fields():
    from bioimageio.spec.model.raw_nodes import Model

    model_kwargs = dict(
        authors=[],
        cite=[],
        description="description text",
        documentation=pathlib.Path("README.md"),
        format_version="0.3.2",
        inputs=[],
        license="MIT",
        name="test_model",
        outputs=[],
        tags=[],
        test_inputs=[],
        test_outputs=[],
        timestamp=datetime.now(),
        weights={},
    )
    # check that model_kwargs are valid
    Model(**model_kwargs)
    with pytest.raises(TypeError):
        Model(**model_kwargs, unknown_weird_test_field="shouldn't be here")  # noqa
