from typing import Sequence

from marshmallow import missing

from bioimageio.spec import v0_1
from bioimageio.spec.shared.common import get_args
from . import converters, nodes, raw_nodes, schema
from ..shared.model_loader_utils import ModelLoaderBase


class ModelLoader(ModelLoaderBase):
    preceding_model_loader = v0_1.utils.ModelLoader
    converters = converters
    schema = schema
    raw_nodes = raw_nodes
    nodes = nodes


load_raw_model = ModelLoader.load_raw_model
load_model = ModelLoader.load_model


def get_nn_instance(
    node: nodes.Model, weight_order: Sequence[nodes.WeightsFormat] = get_args(nodes.WeightsFormat), **kwargs
):
    assert NotImplementedError("weight_order")
    if isinstance(node, nodes.Model):
        if not isinstance(node.source, nodes.ImportedSource):
            raise ValueError(
                f"Encountered unexpected node.source type {type(node.source)}. "
                f"`get_nn_instance` requires _UriNodeTransformer and _SourceNodeTransformer to be applied beforehand."
            )

        joined_kwargs = {} if node.kwargs is missing else dict(node.kwargs)
        joined_kwargs.update(kwargs)
        return node.source(**joined_kwargs)
    else:
        raise TypeError(node)
