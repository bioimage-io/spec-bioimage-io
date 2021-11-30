from bioimageio.spec.shared import fields


def test_cite_entry():
    from bioimageio.spec.rdf.schema import CiteEntry

    data = {
        "text": "Title",
        "doi": "https://doi.org/10.1109/5.771073",
        "url": "https://ieeexplore.ieee.org/document/771073",
    }

    CiteEntry().load(data)


def test_cite_field():
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
