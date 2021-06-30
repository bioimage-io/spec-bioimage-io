from marshmallow import missing

from bioimageio.spec import v0_1
from bioimageio.spec.shared.io import IO_Base
from . import converters, nodes, raw_nodes, schema


class IO(IO_Base):
    preceding_io_class = v0_1.utils.IO
    converters = converters
    schema = schema
    raw_nodes = raw_nodes
    nodes = nodes


def get_nn_instance_from_source(
    node: nodes.Model,  # type: ignore  # Name "nodes.Model" is not defined ???
    **kwargs,
):
    if not isinstance(node, nodes.Model):  # type: ignore
        raise TypeError(node)

    if not isinstance(node.source, nodes.ImportedSource):  # type: ignore
        raise ValueError(
            f"Encountered unexpected node.source type {type(node.source)}. "  # type: ignore
            f"`get_nn_instance_from_source` requires _UriNodeTransformer and _SourceNodeTransformer to be applied beforehand."
        )

    joined_kwargs = {} if node.kwargs is missing else dict(node.kwargs)  # type: ignore
    joined_kwargs.update(kwargs)
    return node.source(**joined_kwargs)
