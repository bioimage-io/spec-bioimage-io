import os
import pathlib
import warnings
from functools import singledispatch
from typing import Optional, Sequence, Union

from marshmallow import ValidationError, missing

from bioimageio.spec.shared import BIOIMAGEIO_CACHE_PATH, yaml
from bioimageio.spec.shared.common import get_args
from bioimageio.spec.shared.transformers import download_uri_to_local_path, resolve_raw_node_to_node, resolve_uri
from . import nodes, raw_nodes, schema
from .converters import maybe_convert_model


download_uri_node_to_local_path = download_uri_to_local_path


@singledispatch
def load_raw_model(source) -> raw_nodes.Model:
    raise TypeError(source)


@load_raw_model.register
def _(source: dict) -> raw_nodes.Model:
    data = maybe_convert_model(source)
    tree: raw_nodes.Model = schema.Model().load(data)
    return tree


@load_raw_model.register
def _(source: os.PathLike) -> raw_nodes.Model:
    source = pathlib.Path(source)

    if source.suffix not in (".yml", ".yaml"):
        raise ValidationError(f"invalid suffix {source.suffix} for source {source}")
    elif source.suffix == ".yml":
        warnings.warn(
            "suffix '.yml' is not recommended and will raise a ValidationError in the future. Use '.yaml' instead "
            "(https://yaml.org/faq.html)"
        )

    data = yaml.load(source)

    return load_raw_model(data)


@load_raw_model.register
def _(source: str) -> raw_nodes.Model:
    if pathlib.Path(source).exists():
        # assume source is file path
        source = pathlib.Path(source)
    else:
        # assume source is uri
        source = resolve_uri(source, root_path=BIOIMAGEIO_CACHE_PATH)

    return load_raw_model(source)


def load_model(source: Union[os.PathLike, str, dict], root_path: Optional[os.PathLike] = None) -> nodes.Model:
    if root_path is None:
        if isinstance(source, dict):
            raise TypeError("Require root_path if source is dict to resolve relative paths")

        if isinstance(source, str):
            try:  # is source a path as a string?
                if not pathlib.Path(source).exists():  # only assume source is a path if path exists
                    raise FileNotFoundError(source)
            except (TypeError, FileNotFoundError):
                # assume source is uri
                source = resolve_uri(source, root_path=BIOIMAGEIO_CACHE_PATH)

        if isinstance(source, os.PathLike):
            root_path = pathlib.Path(source).parent
        else:
            raise TypeError(f"Expected pathlib.Path, os.PathLike, str or dict, but got {type(source)}")

    root_path = pathlib.Path(root_path)

    return resolve_raw_node_to_node(load_raw_model(source), root_path=root_path, nodes_module=nodes)


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
