import pytest
from marshmallow import ValidationError

from bioimageio.spec.shared import yaml
from bioimageio.spec.workflow import raw_nodes


def test_dummy_workflow_rdf(dummy_workflow_rdf):
    from bioimageio.spec.workflow.schema import Workflow

    data = yaml.load(dummy_workflow_rdf)

    workflow = Workflow().load(data)
    assert isinstance(workflow, raw_nodes.Workflow)


def test_invalid_kwarg_name_duplicate(dummy_workflow_rdf):
    from bioimageio.spec.workflow.schema import Workflow

    data = yaml.load(dummy_workflow_rdf)
    data["options"].append(data["options"][0])

    with pytest.raises(ValidationError) as e:
        Workflow().load(data)

    assert e.value.messages == {"inputs/options": ["Duplicate input/option name 'msg' not allowed."]}
