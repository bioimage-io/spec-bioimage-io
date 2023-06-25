from inspect import getmembers

import pytest

from bioimageio.spec.shared import fields
from bioimageio import spec


@pytest.mark.parametrize(
    "schema_raw_nodes_pair",
    [
        (spec.model.schema, spec.model.raw_nodes),
        (spec.model.v0_3.schema, spec.model.v0_3.raw_nodes),
        (spec.model.v0_4.schema, spec.model.v0_4.raw_nodes),
        (spec.rdf.schema, spec.rdf.raw_nodes),
        (spec.rdf.v0_2.schema, spec.rdf.v0_2.raw_nodes),
    ],
)
def test_model_spec(schema_raw_nodes_pair):
    schema, raw_nodes = schema_raw_nodes_pair
    from bioimageio.spec.shared.schema import SharedBioImageIOSchema
    from bioimageio.spec.shared.raw_nodes import RawNode

    schema_names = {
        name for name, cls in getmembers(schema) if isinstance(cls, type) and issubclass(cls, SharedBioImageIOSchema)
    }
    # remove SharedBioImageIOSchema from schema names
    schema_names -= {SharedBioImageIOSchema.__name__}
    assert schema_names  # did we get any?

    node_names = {name for name, cls in getmembers(raw_nodes) if isinstance(cls, type) and issubclass(cls, RawNode)}
    # remove any node_names that are fields
    field_names = {
        name for name, cls in getmembers(fields) if isinstance(cls, type) and issubclass(cls, fields.DocumentedField)
    }
    assert field_names  # did we get any?
    node_names -= field_names
    # if present, ignore raw_nodes.ImportableModule and raw_nodes.ImportableSourceFile which are coming from
    # fields.ImportableSource
    node_names -= {n for n in {"ImportableModule", "ImportableSourceFile"} if hasattr(raw_nodes, n)}

    assert node_names  # did we get any?

    assert node_names, schema_names
