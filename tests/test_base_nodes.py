def test_node_inheritance():
    from bioimageio.spec.shared.base_nodes import NodeBase
    from bioimageio.spec.shared.nodes import Node
    from bioimageio.spec.shared.raw_nodes import RawNode

    node = Node()
    assert isinstance(node, NodeBase)
    assert not isinstance(node, RawNode)
    raw_node = RawNode()
    assert isinstance(raw_node, NodeBase)
    assert not isinstance(raw_node, Node)

