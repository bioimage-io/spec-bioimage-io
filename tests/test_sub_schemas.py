import pytest

from bioimageio.spec.shared import fields


def test_cite_entry():
    from bioimageio.spec.rdf.schema import CiteEntry

    data = {
        "text": "Title",
        "doi": "https://doi.org/10.1109/5.771073",
        "url": "https://ieeexplore.ieee.org/document/771073",
    }

    CiteEntry().load(data)


def test_cite_field_option1():
    from bioimageio.spec.rdf.schema import CiteEntry

    data = [
        {
            "text": "Title",
            "doi": "https://doi.org/10.1109/5.771073",
            "url": "https://ieeexplore.ieee.org/document/771073",
        }
    ] * 2

    cite_field = fields.List(fields.Nested(CiteEntry()), required=True)
    cite_field.deserialize(data)


def test_cite_field_option2():
    from bioimageio.spec.rdf.schema import CiteEntry

    data = [
        {
            "text": "Title",
            "doi": "https://doi.org/10.1109/5.771073",
            "url": "https://ieeexplore.ieee.org/document/771073",
        }
    ] * 2

    cite_field = fields.Nested(CiteEntry(many=True), required=True)
    out = cite_field.deserialize(data)
    assert len(out) == 2


@pytest.skip("we (arbitrarily) don't allow this. Test for reference only. see fields.Nested for details")
def test_cite_field_option3():
    from bioimageio.spec.rdf.schema import CiteEntry

    data = [
        {
            "text": "Title",
            "doi": "https://doi.org/10.1109/5.771073",
            "url": "https://ieeexplore.ieee.org/document/771073",
        }
    ] * 2

    cite_field = fields.Nested(CiteEntry(many=True), many=True, required=True)
    out = cite_field.deserialize(data)
    assert len(out) == 2
