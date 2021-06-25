import dataclasses
from types import ModuleType

from bioimageio.spec.shared.common import get_args
from bioimageio.spec import raw_nodes, schema, nodes


def test_weights_formats_have_raw_nodes():
    weights_formats = [wf for wf in get_args(raw_nodes.WeightsFormat)]
    weights_entry_class_names = [wf.title().replace("_", "") + "WeightsEntry" for wf in weights_formats]

    # all defined weights formats need their schema and nodes implemented...
    for wecn in weights_entry_class_names:
        assert hasattr(schema, wecn), wecn
        assert hasattr(raw_nodes, wecn), wecn
        assert hasattr(nodes, wecn), wecn

    # every WeightEntry schema needs to validate its corresponding weights_format
    for wf, wecn in zip(weights_formats, weights_entry_class_names):
        comparable = getattr(schema, wecn).weights_format.validate.comparable
        assert comparable == wf, (comparable, wf)

    # every WeightEntry node needs to annotate its corresponding weights_format
    def check_weights_format_annotation(nodes_module: ModuleType):
        for wf, wecn in zip(weights_formats, weights_entry_class_names):
            raw_literal = [f for f in dataclasses.fields(getattr(nodes_module, wecn)) if f.name == "weights_format"][
                0
            ].type
            args = get_args(raw_literal)
            assert len(args) == 1, args
            assert args[0] == wf, (args[0], wf)

    check_weights_format_annotation(raw_nodes)
    check_weights_format_annotation(nodes)
