import dataclasses
import os
import pathlib
from copy import deepcopy
from typing import Dict, List, Optional, Sequence, TypeVar, Union

from marshmallow import missing

from bioimageio.spec.shared.common import NoOverridesDict
from bioimageio.spec.shared.io_ import IO_Base
from bioimageio.spec.shared.utils import resolve_uri
from . import base_nodes, converters, nodes, raw_nodes, schema
from .. import v0_1


class IO(IO_Base):
    preceding_io_class = v0_1.utils.IO
    converters = converters
    schema = schema
    raw_nodes = raw_nodes
    nodes = nodes

    @classmethod
    def _get_package_base_name(
        cls, raw_node: raw_nodes.Model, weights_priority_order: Optional[Sequence[base_nodes.WeightsFormat]]
    ) -> str:
        package_base_name = super()._get_package_base_name(raw_node, weights_priority_order)
        if weights_priority_order is not None:
            # add weights format to package file name
            for wf in weights_priority_order:
                if wf in raw_node.weights:
                    package_base_name += f"_{wf}"
                    break
            else:
                raise ValueError(
                    f"None of the requested weights ({weights_priority_order}) "
                    f"found in model weights ({raw_node.weights.keys()})"
                )

        return package_base_name

    @classmethod
    def get_resource_package_content(
        cls,
        source: Union[raw_nodes.Model, os.PathLike, str, dict],
        root_path: os.PathLike,
        *,
        update_to_current_format: bool = False,
        weights_priority_order: Optional[Sequence[base_nodes.WeightsFormat]] = None,
    ) -> Dict[str, Union[str, pathlib.Path]]:

        raw_node, root_path = cls.ensure_raw_node(source, root_path)
        assert isinstance(raw_node, raw_nodes.Model)

        raw_node = deepcopy(raw_node)

        package = NoOverridesDict(
            key_exists_error_msg="Package content conflict for {key}"
        )  # todo: add check in model validation
        package["original_rdf.txt"] = cls.serialize_raw_node(raw_node)
        # todo: .txt -> .yaml once 'rdf.yaml' is only valid rdf file name in package

        _GenericRawNode = TypeVar("_GenericRawNode", bound=raw_nodes.RawNode)

        def incl_as_local(node: _GenericRawNode, field_name: str) -> _GenericRawNode:
            value = getattr(node, field_name)
            if value is not missing:
                if isinstance(value, list):
                    fps = [resolve_uri(v, root_path=root_path) for v in value]
                    for fp in fps:
                        package[fp.name] = fp

                    new_field_value: Union[pathlib.Path, List[pathlib.Path]] = [pathlib.Path(fp.name) for fp in fps]
                else:
                    fp = resolve_uri(value, root_path=root_path)
                    package[fp.name] = fp
                    new_field_value = pathlib.Path(fp.name)

                node = dataclasses.replace(node, **{field_name: new_field_value})

            return node

        raw_node = incl_as_local(raw_node, "documentation")
        raw_node = incl_as_local(raw_node, "test_inputs")
        raw_node = incl_as_local(raw_node, "test_outputs")
        raw_node = incl_as_local(raw_node, "covers")

        # todo: improve dependency handling
        if raw_node.dependencies is not missing:
            dep = incl_as_local(raw_node.dependencies, "file")
            raw_node = dataclasses.replace(raw_node, dependencies=dep)

        if isinstance(raw_node.source, raw_nodes.ImportableSourceFile):
            source = incl_as_local(raw_node.source, "source_file")
            raw_node = dataclasses.replace(raw_node, source=source)

        # filter weights
        for wfp in weights_priority_order or []:
            if wfp in raw_node.weights:
                weights = {wfp: raw_node.weights[wfp]}
                break
        else:
            weights = raw_node.weights

        # add weights
        local_weights = {}
        for wf, weights_entry in weights.items():
            weights_entry = incl_as_local(weights_entry, "source")
            local_files = []
            if weights_entry.attachments is not missing:
                for fa in weights_entry.attachments.get("files", []):
                    fa = resolve_uri(fa, root_path=root_path)
                    package[fa.name] = fa
                    local_files.append(fa.name)

            if local_files:
                weights_entry.attachments["files"] = local_files

            local_weights[wf] = weights_entry

        raw_node = dataclasses.replace(raw_node, weights=local_weights)

        # attachments:files
        if raw_node.attachments is not missing:
            local_files = []
            for fa in raw_node.attachments.get("files", []):
                fa = resolve_uri(fa, root_path=root_path)
                package[fa.name] = fa
                local_files.append(fa.name)

            if local_files:
                raw_node.attachments["files"] = local_files

        package["rdf.yaml"] = cls.serialize_raw_node(raw_node)
        return dict(package)
