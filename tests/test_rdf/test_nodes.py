import pytest
from pydantic import HttpUrl
from pydantic import ValidationError

from bioimageio.spec.shared.fields import RelativePath


def test_attachments():
    from bioimageio.spec.rdf.v0_2.nodes import Attachments

    a = Attachments(files=(RelativePath(__file__), HttpUrl("example.com")))
    assert a.files is not None
    assert a.files[1] == "https://example.com"


def test_author():
    from bioimageio.spec.rdf.v0_2.nodes import Author

    a = Author(
        name="Me", affiliation="Paradise", email="me@example.com", github_user="ghuser", orcid="0000-0001-2345-6789"
    )
    assert a.name == "Me"
    with pytest.raises(ValidationError):
        Author(affiliation="Paradise", email="me@example.com", github_user="ghuser", orcid="0000-0001-2345-6789")

    with pytest.raises(ValidationError):
        Author(
            name="Me", affiliation="Paradise", email="me@example.com", github_user="ghuser", orcid="0000-0001-2345-6788"
        )


def test_maintainer():
    from bioimageio.spec.rdf.v0_2.nodes import Maintainer

    m = Maintainer(
        name="Me", affiliation="Paradise", email="me@example.com", github_user="ghuser", orcid="0000-0001-2345-6789"
    )
    assert m.github_user == "ghuser"
    with pytest.raises(ValidationError):
        Maintainer(name="Me", affiliation="Paradise", email="me@example.com", orcid="0000-0001-2345-6789")


test_maintainer()
