import dataclasses
import pathlib
from datetime import datetime
from typing import Any, Dict

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


def test_replace_uri_wo_uri_string():
    from bioimageio.spec.shared.raw_nodes import URI

    uri_string = "https://john.doe@www.example.com:123/forum/questions/?tag=networking&order=newest#top"
    uri_string = uri_string.replace("top", "bottom")

    uri = URI(
        scheme="https",
        authority="john.doe@www.example.com:123",
        path="/forum/questions/",
        query="tag=networking&order=newest",
        fragment="top",
    )
    uri = dataclasses.replace(uri, fragment="bottom")
    assert uri_string == str(uri)


def test_uri_is_relative_path():
    from bioimageio.spec.shared.raw_nodes import URI

    # todo: figure out if it is important to keep a trailing slash.
    #  atm uri_from_string removes it (using urllib.parse.urlparse)
    # uri_from_string = URI("file:forum/questions/")
    # uri = URI(scheme="file", path="forum/questions/")

    uri_from_string = URI("file:forum/questions")
    uri = URI(scheme="file", path="forum/questions")

    assert str(uri_from_string) == str(uri)
    assert uri_from_string == uri


def test_uri_is_url():
    from bioimageio.spec.shared.raw_nodes import URI

    url = "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/test_input.npy"
    uri = URI(url)
    assert str(uri) == url


def test_uri_truediv():
    from bioimageio.spec.shared.raw_nodes import URI

    url = "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad?download=1"
    rel_path = "test_input.npy"
    expected = URI(
        f"https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/{rel_path}?download=1"
    )
    uri = URI(url)
    assert expected == uri / rel_path
    assert expected == uri / rel_path  # ensure we did not change uri in-place


def test_uri_parent():
    from bioimageio.spec.shared.raw_nodes import URI

    url = "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/test_input.npy?download=1"
    expected = URI(
        "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad?download=1"
    )
    uri = URI(url)
    assert expected == uri.parent
    assert expected == uri.parent  # ensure we did not change uri in-place


def test_general_rdf_accepts_unknown_fields():
    from bioimageio.spec.rdf.raw_nodes import RDF

    rdf = RDF(
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
    assert rdf.name == "test_rdf"


def test_model_does_not_accept_unknown_fields():
    from bioimageio.spec.model.raw_nodes import Model

    model_kwargs: Dict[str, Any] = dict(
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
        Model(**model_kwargs, unknown_weird_test_field="shouldn't be here")  # type: ignore
