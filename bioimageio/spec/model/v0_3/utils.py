import dataclasses
import os
import pathlib
from copy import deepcopy
from typing import Dict, List, Optional, Sequence, TypeVar, Union

from marshmallow import missing

from bioimageio.spec.shared.common import BIOIMAGEIO_CACHE_PATH, NoOverridesDict
from bioimageio.spec.shared.io_ import IO_Base
from bioimageio.spec.shared.raw_nodes import ResourceDescription as RawResourceDescription
from bioimageio.spec.shared.utils import URI_Node, resolve_uri
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

    @classmethod
    def _get_package_base_name(
        cls, raw_rd: raw_nodes.Model, weights_priority_order: Optional[Sequence[base_nodes.WeightsFormat]]
    ) -> str:
        package_base_name = super()._get_package_base_name(raw_rd, weights_priority_order)
        if weights_priority_order is not None:
            # add weights format to package file name
            for wf in weights_priority_order:
                if wf in raw_rd.weights:
                    package_base_name += f"_{wf}"
                    break
            else:
                raise ValueError(
                    f"None of the requested weights ({weights_priority_order}) "
                    f"found in model weights ({raw_rd.weights.keys()})"
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

        raw_rd, root_path = cls.ensure_raw_rd(source, root_path)
        assert isinstance(raw_rd, raw_nodes.Model)

        raw_rd = deepcopy(raw_rd)

        package = NoOverridesDict(
            key_exists_error_msg="Package content conflict for {key}"
        )  # todo: add check in model validation
        package["original_rdf.txt"] = cls.serialize_raw_resource_description(raw_rd)
        # todo: .txt -> .yaml once 'rdf.yaml' is only valid rdf file name in package

        _GenericRawNode = TypeVar("_GenericRawNode", bound=raw_nodes.RawNode)

        def get_path_in_package(fp: pathlib.Path, rpath: os.PathLike) -> pathlib.Path:
            try:
                name = fp.relative_to(rpath)
            except ValueError:  # fp not relative to root path, e.g. due to resolved url
                name = pathlib.Path(fp.name)
                if name in package:  # avoid name collision
                    for i in range(1000):
                        name = pathlib.Path(f"{fp.name}{i}")
                        if name not in package:
                            break
                    else:
                        raise RuntimeError(f"Cannot ad {fp.name} to package content")

            return name

        def incl_as_local(node: _GenericRawNode, field_name: str) -> _GenericRawNode:
            value = getattr(node, field_name)
            if value is not missing:
                if isinstance(value, list):
                    fps: List[pathlib.Path] = [resolve_uri(v, root_path=root_path) for v in value]
                    pps: List[pathlib.Path] = [get_path_in_package(fp, root_path) for fp in fps]
                    for pp, fp in zip(pps, fps):
                        package[pp] = fp

                    new_field_value: Union[pathlib.Path, List[pathlib.Path]] = pps
                else:
                    fp = resolve_uri(value, root_path=root_path)
                    pp = get_path_in_package(fp, root_path)
                    package[pp] = fp
                    new_field_value = pp

                node = dataclasses.replace(node, **{field_name: new_field_value})

            return node

        raw_rd = incl_as_local(raw_rd, "documentation")
        raw_rd = incl_as_local(raw_rd, "test_inputs")
        raw_rd = incl_as_local(raw_rd, "test_outputs")
        raw_rd = incl_as_local(raw_rd, "covers")

        # todo: improve dependency handling
        if raw_rd.dependencies is not missing:
            dep = incl_as_local(raw_rd.dependencies, "file")
            raw_rd = dataclasses.replace(raw_rd, dependencies=dep)

        if isinstance(raw_rd.source, raw_nodes.ImportableSourceFile):
            source = incl_as_local(raw_rd.source, "source_file")
            raw_rd = dataclasses.replace(raw_rd, source=source)

        # filter weights
        for wfp in weights_priority_order or []:
            if wfp in raw_rd.weights:
                weights = {wfp: raw_rd.weights[wfp]}
                break
        else:
            weights = raw_rd.weights

        # add weights
        local_weights = {}
        for wf, weights_entry in weights.items():
            weights_entry = incl_as_local(weights_entry, "source")
            local_files = []
            if weights_entry.attachments is not missing:
                for fa in weights_entry.attachments.get("files", []):
                    fa = resolve_uri(fa, root_path=root_path)
                    pp = get_path_in_package(fa, root_path)
                    package[pp] = fa
                    local_files.append(pp)

            if local_files:
                weights_entry.attachments["files"] = local_files

            local_weights[wf] = weights_entry

        raw_rd = dataclasses.replace(raw_rd, weights=local_weights)

        # attachments:files
        if raw_rd.attachments is not missing:
            local_files = []
            for fa in raw_rd.attachments.get("files", []):
                fa = resolve_uri(fa, root_path=root_path)
                pp = get_path_in_package(fa, root_path)
                package[pp] = fa
                local_files.append(pp)

            if local_files:
                raw_rd.attachments["files"] = local_files

        package["rdf.yaml"] = cls.serialize_raw_resource_description(raw_rd)
        return dict(package)
