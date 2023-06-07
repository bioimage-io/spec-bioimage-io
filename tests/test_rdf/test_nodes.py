from pydantic import ValidationError
import pytest


def test_author():
    from bioimageio.spec.rdf.v0_2.nodes import Author

    author = Author(
        name="Me", affiliation="Paradise", email="me@example.com", github_user="ghuser", orcid="0000-0001-2345-6789"
    )
    assert author.name == "Me"
    with pytest.raises(ValidationError):
        Author(affiliation="Paradise", email="me@example.com", github_user="ghuser", orcid="0000-0001-2345-6789")  # type: ignore

    with pytest.raises(ValidationError):
        Author(
            name="Me", affiliation="Paradise", email="me@example.com", github_user="ghuser", orcid="0000-0001-2345-6788"
        )
