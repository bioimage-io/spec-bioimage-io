import os
import pathlib
from functools import singledispatch
from typing import Optional, Sequence, Tuple

from marshmallow import ValidationError

from bioimageio.spec.shared import BIOIMAGEIO_CACHE_PATH, yaml
from bioimageio.spec.shared.transformers import download_uri_to_local_path, resolve_raw_node_to_node, resolve_uri
from . import nodes, raw_nodes, schema
from .converters import maybe_convert_model

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args

download_uri_node_to_local_path = download_uri_to_local_path


@singledispatch
def load_raw_model(source, root_path: Optional[pathlib.Path] = None) -> Tuple[raw_nodes.Model, pathlib.Path]:
    raise TypeError(source)


@load_raw_model.register
def _(source: dict, root_path: Optional[pathlib.Path] = None) -> Tuple[raw_nodes.Model, pathlib.Path]:
    data = maybe_convert_model(source)
    tree: raw_nodes.Model = schema.Model().load(data)

    return tree, root_path


@load_raw_model.register
def _(source: os.PathLike, root_path: Optional[pathlib.Path] = None) -> Tuple[raw_nodes.Model, pathlib.Path]:
    source = pathlib.Path(source)

    suffixes = source.suffixes
    if len(suffixes) < 2 or suffixes[-1] not in (".yml", ".yaml") or source.suffixes[-2] != ".model":
        raise ValidationError(f"invalid suffixes {''.join(suffixes)} for source {source}")

    data = yaml.load(source)

    return load_raw_model(data, root_path=root_path)


@load_raw_model.register
def _(source: str, root_path: Optional[pathlib.Path] = None) -> Tuple[raw_nodes.Model, pathlib.Path]:
    if pathlib.Path(source).exists():
        # assume source is file path
        source = pathlib.Path(source)
    else:
        # assume source is uri
        source = resolve_uri(source, root_path=root_path or BIOIMAGEIO_CACHE_PATH)
        root_path = source.parent

    return load_raw_model(source, root_path=root_path)


def load_model(source, root_path: Optional[pathlib.Path] = None):
    return resolve_raw_node_to_node(*load_raw_model(source, root_path=root_path), nodes_module=nodes)


def get_nn_instance(
    node: nodes.Model, weight_order: Sequence[nodes.WeightsFormat] = get_args(nodes.WeightsFormat), **kwargs
):
    assert NotImplementedError("weight_order")
    if isinstance(node, nodes.Model):
        if not isinstance(node.source, nodes.ImportedSource):
            raise ValueError(
                f"Encountered unexpected node.source type {type(node.source)}. "
                f"`get_instance` requires _UriNodeTransformer and _SourceNodeTransformer to be applied beforehand."
            )

        joined_kwargs = dict(node.kwargs)
        joined_kwargs.update(kwargs)
        return node.source(**joined_kwargs)
    else:
        raise TypeError(node)
