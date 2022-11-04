import pytest
from marshmallow import ValidationError

from bioimageio.spec.shared import yaml
from bioimageio.spec.workflow import raw_nodes


def test_workflow_rdf_stardist_example(stardist_workflow_rdf):
    from bioimageio.spec.workflow.schema import Workflow

    data = yaml.load(stardist_workflow_rdf)

    workflow = Workflow().load(data)
    assert isinstance(workflow, raw_nodes.Workflow)
    assert workflow.steps[0].op == "zero_mean_unit_variance"


def test_workflow_rdf_hpa_example(hpa_workflow_rdf):
    from bioimageio.spec.workflow.schema import Workflow

    data = yaml.load(hpa_workflow_rdf)

    workflow = Workflow().load(data)
    assert isinstance(workflow, raw_nodes.Workflow)
    assert workflow.outputs_spec[0].name == "cells"


def test_dummy_workflow_rdf(dummy_workflow_rdf):
    from bioimageio.spec.workflow.schema import Workflow

    data = yaml.load(dummy_workflow_rdf)

    workflow = Workflow().load(data)
    assert isinstance(workflow, raw_nodes.Workflow)


def test_invalid_kwarg_name_duplicate(dummy_workflow_rdf):
    from bioimageio.spec.workflow.schema import Workflow

    data = yaml.load(dummy_workflow_rdf)
    data["options_spec"].append(data["options_spec"][0])

    with pytest.raises(ValidationError) as e:
        Workflow().load(data)

    assert e.value.messages == {"inputs_spec/options_spec": ["Duplicate input/option name 'threshold' not allowed."]}
