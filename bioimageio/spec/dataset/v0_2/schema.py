from bioimageio.spec.rdf.v0_2.schema import RDF
from bioimageio.spec.shared.schema import SharedBioImageIOSchema
from . import raw_nodes

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore


class _BioImageIOSchema(SharedBioImageIOSchema):
    raw_nodes = raw_nodes


class Dataset(_BioImageIOSchema, RDF):
    bioimageio_description = f"""# BioImage.IO Dataset Resource Description File Specification {get_args(raw_nodes.FormatVersion)[-1]}
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing datasets.
These fields are typically stored in a YAML file which we call Dataset Resource Description File or `dataset RDF`.

The dataset RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.
"""
