from marshmallow import INCLUDE

from bioimageio.spec.rdf.v0_2.schema import RDF
from bioimageio.spec.shared import fields
from bioimageio.spec.shared.schema import SharedBioImageIOSchema
from . import raw_nodes


class _BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes = raw_nodes


class CollectionEntry(_BioImageIOSchema):
    class Meta:
        unknown = INCLUDE

    id_ = fields.String(required=True, data_key="id")
    source = fields.URL(required=True)
    links = fields.List(fields.String())


class Collection(_BioImageIOSchema, RDF):
    application = fields.List(fields.Union([fields.Nested(CollectionEntry()), fields.Nested(RDF())]))
    collection = fields.List(fields.Union([fields.Nested(CollectionEntry()), fields.Nested(RDF())]))
    model = fields.List(fields.Union([fields.Nested(CollectionEntry()), fields.Nested(RDF())]))
    dataset = fields.List(fields.Union([fields.Nested(CollectionEntry()), fields.Nested(RDF())]))
    notebook = fields.List(fields.Union([fields.Nested(CollectionEntry()), fields.Nested(RDF())]))
