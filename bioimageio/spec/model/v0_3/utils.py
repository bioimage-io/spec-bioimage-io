import dataclasses
import os
import pathlib
from copy import deepcopy
from typing import Dict, List, Optional, Sequence, Tuple, TypeVar, Union

from marshmallow import missing

from bioimageio.spec.shared.common import BIOIMAGEIO_CACHE_PATH, NoOverridesDict
from bioimageio.core.resource_io.io_ import IO_Base
from bioimageio.spec.shared.raw_nodes import ResourceDescription as RawResourceDescription
from bioimageio.core.resource_io.utils import URI_Node, resolve_uri
from . import base_nodes, converters, nodes, raw_nodes, schema
from .converters import AUTO_CONVERTED_DOCUMENTATION_FILE_NAME
from .. import v0_1


class IO(IO_Base):
    preceding_io_class = v0_1.utils.IO
    converters = converters
    schema = schema
    raw_nodes = raw_nodes
    nodes = nodes

    @classmethod
    def load_raw_resource_description(cls, source: Union[os.PathLike, str, dict, URI_Node]) -> RawResourceDescription:
        raw_rd = super().load_raw_resource_description(source)
        assert isinstance(raw_rd, raw_nodes.Model)
        doc = (raw_rd.config or {}).get(AUTO_CONVERTED_DOCUMENTATION_FILE_NAME)
        if doc is not None:
            # write doc to temporary path (we also do not know root_path here)
            doc_path = (
                BIOIMAGEIO_CACHE_PATH / "auto-convert" / str(hash(cls.serialize_raw_resource_description(raw_rd)))
            )
            doc_path.mkdir(parents=True, exist_ok=True)
            doc_path = doc_path / AUTO_CONVERTED_DOCUMENTATION_FILE_NAME
            doc_path.write_text(doc)
            raw_rd.documentation = doc_path

        return raw_rd



def filter_resource_description(
    raw_rd: raw_nodes.Model, weights_priority_order: Optional[Sequence[base_nodes.WeightsFormat]] = None
) -> raw_nodes.Model:
    # filter weights
    raw_rd = deepcopy(raw_rd)
    for wfp in weights_priority_order or []:
        if wfp in raw_rd.weights:
            raw_rd.weights = {wfp: raw_rd.weights[wfp]}
            break
    else:
        raise ValueError(f"Not found any of the specified weights formats ({weights_priority_order})")

    return raw_rd
