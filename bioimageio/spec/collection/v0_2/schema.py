from marshmallow import missing, validates

from bioimageio.spec.rdf.v0_2.schema import RDF
from bioimageio.spec.shared import fields
from bioimageio.spec.shared.schema import SharedBioImageIOSchema, WithUnknown
from . import raw_nodes

try:
    from typing import List, Union, get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore


class _BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes = raw_nodes


class CollectionEntry(_BioImageIOSchema, WithUnknown):
    field_name_unknown_dict = "rdf_update"
    rdf_source = fields.Union([fields.URL(), fields.DOI()])


class Collection(_BioImageIOSchema, WithUnknown, RDF):
    bioimageio_description = f"""# BioImage.IO Collection Resource Description File Specification {get_args(raw_nodes.FormatVersion)[-1]}
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing collections of other resources.
These fields are typically stored in a YAML file which we call Collection Resource Description File or `collection RDF`.

The collection RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.
"""
    collection = fields.List(
        fields.Nested(CollectionEntry()),
        bioimageio_description="Collection entries. Each entry needs to specify a valid RDF with an id. "
        "Each collection entry RDF is based on the collection RDF itself, "
        "updated by rdf_source content if rdf_source is specified, "
        "and updated by any fields specified directly in the entry. "
        "In this context 'update' refers to overwriting RDF root fields by name."
        "Except for the `id` field, which appends to the collection RDF `id` "
        "such that full_collection_entry_id=<collection_id>/<entry_id>",
        required=True,
    )

    @validates("collection")
    def unique_ids(self, value: List[Union[dict, raw_nodes.CollectionEntry]]):
        ids = [
            (v.get("id", missing), v.get("rdf_source", missing))
            if isinstance(v, dict)
            else (v.rdf_update.get("id", missing), v.rdf_source)
            for v in value
        ]
        # skip check for id only specified in remote source
        ids = [vid for vid, vs in ids if not (vid is missing and vs is not missing)]

        if missing in ids:
            raise ValueError(f"Missing ids in collection entries")

        non_string_ids = [v for v in ids if not isinstance(v, str)]
        if non_string_ids:
            raise ValueError(f"Non-string ids in collection: {non_string_ids}")

        seen = set()
        duplicates = []
        for v in ids:
            if v in seen:
                duplicates.append(v)
            else:
                seen.add(v)

        if duplicates:
            raise ValueError(f"Duplicate ids in collection: {duplicates}")
