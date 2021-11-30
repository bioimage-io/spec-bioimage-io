def test_cite_entry():
    from bioimageio.spec.rdf.schema import CiteEntry

    data = {
        "text": "Title",
        "doi": "https://doi.org/10.1109/5.771073",
        "url": "https://ieeexplore.ieee.org/document/771073",
    }

    CiteEntry().load(data)
