from bioimageio.spec.shared.common import get_args


def test_weights_formats_have_raw_nodes():
    from bioimageio.spec.model import raw_nodes, schema

    weights_formats = [wf for wf in get_args(raw_nodes.WeightsFormat)]
    weights_entry_class_names = [wf.title().replace("_", "") + "WeightsEntry" for wf in weights_formats]

    # all defined weights formats need their schema and nodes implemented...
    for wecn in weights_entry_class_names:
        assert hasattr(schema, wecn), wecn
        assert hasattr(raw_nodes, wecn), wecn

    # every WeightEntry schema needs to validate its corresponding weights_format
    for wf, wecn in zip(weights_formats, weights_entry_class_names):
        comparable = getattr(schema, wecn)().fields["weights_format"].validate.comparable
        assert comparable == wf, (comparable, wf)
