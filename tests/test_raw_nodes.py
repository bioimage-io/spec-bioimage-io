import pytest

from bioimageio.spec import raw_nodes


def test_uri():
    uri_from_string = raw_nodes.URI(
        "https://john.doe@www.example.com:123/forum/questions/?tag=networking&order=newest#top"
    )
    uri = raw_nodes.URI(
        scheme="https",
        authority="john.doe@www.example.com:123",
        path="/forum/questions/",
        query="tag=networking&order=newest",
        fragment="top",
    )

    assert str(uri_from_string) == str(uri)
    assert uri_from_string == uri


def test_uri_is_relative_path():
    uri_from_string = raw_nodes.URI("forum/questions/")
    uri = raw_nodes.URI(path="forum/questions/")

    assert str(uri_from_string) == str(uri)
    assert uri_from_string == uri


def test_uri_is_absolute_path():
    with pytest.raises(ValueError):
        raw_nodes.URI("/forum/questions/")

    with pytest.raises(ValueError):
        raw_nodes.URI(path="/forum/questions/")


def test_general_rdf_accepts_unknown_fields():
    from bioimageio.spec.raw_nodes import RDF

    RDF(unknown_weird_test_field="shouldn't be here")


def test_model_does_not_accept_unknown_fields():
    from bioimageio.spec.raw_nodes import Model

    with pytest.raises(TypeError):
        Model(unknown_weird_test_field="shouldn't be here")
