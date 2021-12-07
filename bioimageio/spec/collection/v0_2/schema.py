from marshmallow import RAISE

from bioimageio.spec.rdf.v0_2.schema import RDF
from bioimageio.spec.shared import fields
from bioimageio.spec.shared.schema import SharedBioImageIOSchema, WithUnknown
from . import raw_nodes

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore


class _BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes = raw_nodes


class CollectionEntry(_BioImageIOSchema, WithUnknown):
    id_ = fields.String(required=True, data_key="id")
    source = fields.URL(required=True)
    links = fields.List(fields.String())


class Collection(_BioImageIOSchema, RDF):
    class Meta:
        unknown = RAISE

    bioimageio_description = f"""# BioImage.IO Collection Resource Description File Specification {get_args(raw_nodes.FormatVersion)[-1]}
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing collections of other resources.
These fields are typically stored in YAML files which we call Collection Resource Description Files or `collection RDF`.

The collection RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.
"""
    application = fields.List(fields.Union([fields.Nested(CollectionEntry()), fields.Nested(RDF())]))
    collection = fields.List(fields.Union([fields.Nested(CollectionEntry()), fields.Nested(RDF())]))
    model = fields.List(fields.Union([fields.Nested(CollectionEntry()), fields.Nested(RDF())]))
    dataset = fields.List(fields.Union([fields.Nested(CollectionEntry()), fields.Nested(RDF())]))
    notebook = fields.List(fields.Union([fields.Nested(CollectionEntry()), fields.Nested(RDF())]))
