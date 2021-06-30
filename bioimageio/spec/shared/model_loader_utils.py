# type: ignore  # all sorts of unbound types :)
from __future__ import annotations

import dataclasses
import os
import pathlib
import warnings
from copy import deepcopy
from io import StringIO
from types import ModuleType
from typing import Any, ClassVar, Dict, Generic, Optional, Sequence, TYPE_CHECKING, Tuple, Type, TypeVar, Union
from zipfile import ZipFile

from marshmallow import ValidationError, missing

from . import get_dict_and_root_path_from_yaml_source, nodes, raw_nodes
from .common import BIOIMAGEIO_CACHE_PATH, Literal, Protocol, NoOverridesDict, get_args, yaml
from .raw_nodes import ImportablePath, Node, URI
from .schema import SharedBioImageIOSchema
from .utils import GenericNode, resolve_raw_node_to_node, resolve_uri


if TYPE_CHECKING:
    import bioimageio.spec as current_spec

# placeholders for versioned classes
ModelSchema = TypeVar("ModelSchema", bound=SharedBioImageIOSchema)
RawModelNode = TypeVar("RawModelNode", bound=raw_nodes.Node)
ModelNode = TypeVar("ModelNode", bound=nodes.Node)


# placeholders for versioned modules
class ConvertersModule(Protocol):
    def maybe_update_model_minor(self, data: dict) -> dict:
        raise NotImplementedError

    def maybe_update_model_patch(self, data: dict) -> dict:
        raise NotImplementedError


class RawNodesModule(Protocol):
    ModelFormatVersion: Any
    Model: Type[RawModelNode]


class NodesModule(Protocol):
    Model: Type[RawModelNode]


class SchemaModule(Protocol):
    Model: Type[ModelSchema]


# an alternative meta class approach to describe the class properties:
# class ModelLoaderBaseMeta(ABCMeta):
#     """
#     defines abstract class properties for ModelLoaderBase
#
#     note: as derived classes may be defined and instantiated without setting these abstract class properties they raise
#     NotImplementedError.
#     """
#
#     @property
#     @abstractmethod
#     def preceding_model_loader(self) -> typing.Optional[ModelLoaderBase]:
#         raise NotImplementedError(f"{self}.preceding_model_loader")
#
#     @property
#     @abstractmethod
#     def converters(self) -> ConvertersModule:
#         raise NotImplementedError(f"{self}.converters")
#
#     @property
#     @abstractmethod
#     def schema(self) -> SchemaModule:
#         raise NotImplementedError(f"{self}.schema")
#
#     @property
#     @abstractmethod
#     def raw_nodes(self) -> RawNodesModule:
#         raise NotImplementedError(f"{self}.raw_nodes")
#
#     @property
#     @abstractmethod
#     def nodes(self) -> RawNodesModule:
#         raise NotImplementedError(f"{self}.nodes")


# class ModelLoaderBase(metaclass=ModelLoaderBaseMeta):
class ModelLoaderBase:
    preceding_model_loader: ClassVar[Optional[ModelLoaderBase]]
    converters: ClassVar[ConvertersModule]
    schema: ClassVar[SchemaModule]
    raw_nodes: ClassVar[RawNodesModule]
    nodes: ClassVar[RawNodesModule]

    @classmethod
    def load_raw_model(
        cls, source: Union[os.PathLike, str, dict], update_to_current_format: bool = False
    ) -> RawModelNode:
        data, root_path = get_dict_and_root_path_from_yaml_source(source)

        format_version = data.get("format_version")

        if format_version is None:
            raise ValidationError("missing 'format_version'")

        data_version_wo_patch = cls.get_version_tuple_wo_patch(format_version)
        current_version_wo_patch = cls.get_current_format_version_wo_patch()
        if data_version_wo_patch > current_version_wo_patch:
            raise ValueError(
                f"You are attempting to load a model in format version {'.'.join(map(str, data_version_wo_patch))}.x "
                f"with the model spec {'.'.join(map(str, current_version_wo_patch))}"
            )
        elif data_version_wo_patch == current_version_wo_patch or update_to_current_format:
            if update_to_current_format:
                data = cls.maybe_update_model_minor(data)

            data = cls.converters.maybe_update_model_patch(data)
            raw_model: RawModelNode = cls.load_raw_model_from_dict(data)
            assert isinstance(raw_model, cls.raw_nodes.Model)
        elif cls.preceding_model_loader is None:
            raise NotImplementedError(f"format version {'.'.join(map(str, data_version_wo_patch))}")
        else:
            raw_model = cls.preceding_model_loader.load_raw_model(data)

        return raw_model

    @classmethod
    def serialize_raw_model_to_dict(cls, raw_model: RawModelNode) -> dict:
        if raw_model.format_version is missing:
            raise ValidationError("missing 'format_version'")

        data_version_wo_patch = cls.get_version_tuple_wo_patch(raw_model.format_version)
        current_version_wo_patch = cls.get_current_format_version_wo_patch()
        if data_version_wo_patch > current_version_wo_patch:
            raise ValueError(
                f"You are attempting to save a model in format version {'.'.join(map(str, data_version_wo_patch))}.x "
                f"with the model spec {'.'.join(map(str, current_version_wo_patch))}"
            )
        elif data_version_wo_patch == current_version_wo_patch:
            serialized = cls.schema.Model().dump(raw_model)
            assert isinstance(serialized, dict)
        elif cls.preceding_model_loader is None:
            raise NotImplementedError(f"format version {'.'.join(map(str, data_version_wo_patch))}")
        else:
            serialized = cls.preceding_model_loader.serialize_raw_model_to_dict(raw_model)

        return serialized

    @classmethod
    def save_raw_model(cls, raw_model: RawModelNode, path: pathlib.Path):
        warnings.warn("only saving serialized rdf, no associated resources.")
        if path.suffix != ".yaml":
            warnings.warn("saving with '.yaml' suffix is strongly encouraged.")

        serialized = cls.serialize_raw_model_to_dict(raw_model)
        yaml.dump(serialized, path)

    @classmethod
    def serialize_raw_model(cls, raw_model: Union[dict, RawModelNode]) -> str:
        if not isinstance(raw_model, dict):
            raw_model = cls.serialize_raw_model_to_dict(raw_model)

        with StringIO() as stream:
            yaml.dump(raw_model, stream)
            return stream.getvalue()

    @classmethod
    def export_package(
        cls,
        source: Union[RawModelNode, os.PathLike, str, dict],
        root_path: Optional[os.PathLike] = None,
        update_to_current_format: bool = False,
        weights_formats_priorities: Optional[Sequence[current_spec.raw_nodes.WeightsFormat]] = None,
    ) -> pathlib.Path:
        """
        weights_formats_priorities: If given only the first weights format present in the model is included.
                                    If none of the prioritized weights formats is found all are included.
        """
        raw_model, root_path = cls.ensure_raw_model(source, root_path, update_to_current_format)
        data_version_wo_patch = cls.get_version_tuple_wo_patch(raw_model.format_version)
        current_version_wo_patch = cls.get_current_format_version_wo_patch()
        if data_version_wo_patch > current_version_wo_patch:
            raise ValueError(
                f"You are attempting to package a model in format version {'.'.join(map(str, data_version_wo_patch))}.x "
                f"with the model spec {'.'.join(map(str, current_version_wo_patch))}"
            )
        elif data_version_wo_patch == current_version_wo_patch:
            package_path = cls._make_package_wo_conversions(
                raw_model, root_path, weights_formats_priorities=weights_formats_priorities
            )
        elif cls.preceding_model_loader is None:
            raise NotImplementedError(f"format version {'.'.join(map(str, data_version_wo_patch))}")
        else:
            package_path = cls.preceding_model_loader.export_package(raw_model, root_path, update_to_current_format)

        return package_path

    @classmethod
    def _make_package_wo_conversions(
        cls, raw_model: RawModelNode, root_path: pathlib.Path, weights_formats_priorities: Optional[Sequence[str]]
    ):
        package_file_name = raw_model.name
        if raw_model.version is not missing:
            package_file_name += f"_{raw_model.version}"

        package_file_name = package_file_name.replace(" ", "_").replace(".", "_")

        package_path = (BIOIMAGEIO_CACHE_PATH / package_file_name).with_suffix(".zip")
        max_cached_packages_with_same_name = 100
        for p in range(max_cached_packages_with_same_name):
            if package_path.exists():
                package_path = (BIOIMAGEIO_CACHE_PATH / f"{package_file_name}p{p}").with_suffix(".zip")
            else:
                break
        else:
            raise FileExistsError(
                f"Already caching {max_cached_packages_with_same_name} versions of {BIOIMAGEIO_CACHE_PATH / package_file_name}!"
            )
        package_content = cls.get_package_content(
            deepcopy(raw_model), root_path=root_path, weights_formats_priorities=weights_formats_priorities
        )
        cls.make_zip(package_path, package_content)
        return package_path

    @classmethod
    def get_package_content(
        cls,
        raw_model: current_spec.raw_nodes.Model,
        root_path: pathlib.Path,
        weights_formats_priorities: Optional[Sequence[str]],
    ) -> Dict[str, Union[str, pathlib.Path]]:
        package = NoOverridesDict(
            key_exists_error_msg="Package content conflict for {key}"
        )  # todo: add check in model validation
        package["original_rdf.txt"] = cls.serialize_raw_model(raw_model)

        def incl_as_local(node: GenericNode, field_name: str) -> GenericNode:
            value = getattr(node, field_name)
            if value is not missing:
                if isinstance(value, list):
                    fps = [resolve_uri(v, root_path=root_path) for v in value]
                    for fp in fps:
                        package[fp.name] = fp

                    new_field_value = [pathlib.Path(fp.name) for fp in fps]
                else:
                    fp = resolve_uri(value, root_path=root_path)
                    package[fp.name] = fp
                    new_field_value = pathlib.Path(fp.name)

                node = dataclasses.replace(node, **{field_name: new_field_value})

            return node

        raw_model = incl_as_local(raw_model, "documentation")
        raw_model = incl_as_local(raw_model, "test_inputs")
        raw_model = incl_as_local(raw_model, "test_outputs")
        raw_model = incl_as_local(raw_model, "covers")

        # todo: improve dependency handling
        if raw_model.dependencies is not missing:
            manager, fp = raw_model.dependencies.split(":")
            fp = resolve_uri(fp, root_path=root_path)
            package[fp.name] = fp
            raw_model = dataclasses.replace(raw_model, dependencies=f"{manager}:{fp.name}")

        if isinstance(raw_model.source, ImportablePath):
            source = incl_as_local(raw_model.source, "filepath")
            raw_model = dataclasses.replace(raw_model, source=source)

        # filter weights
        for wfp in weights_formats_priorities or []:
            if wfp in raw_model.weights:
                weights = {wfp: raw_model.weights[wfp]}
                break
        else:
            weights = raw_model.weights

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

        raw_model = dataclasses.replace(raw_model, weights=local_weights)

        # attachments:files
        if raw_model.attachments is not missing:
            local_files = []
            for fa in raw_model.attachments.get("files", []):
                fa = resolve_uri(fa, root_path=root_path)
                package[fa.name] = fa
                local_files.append(fa.name)

            if local_files:
                raw_model.attachments["files"] = local_files

        package["rdf.yaml"] = cls.serialize_raw_model(raw_model)
        return dict(package)

    @classmethod
    def make_zip(cls, path: pathlib.Path, content: Dict[str, Union[str, pathlib.Path]]):
        with ZipFile(path, "w") as myzip:
            for arc_name, file_or_str_content in content.items():
                if isinstance(file_or_str_content, str):
                    myzip.writestr(arc_name, file_or_str_content)
                else:
                    myzip.write(file_or_str_content, arcname=arc_name)

    @classmethod
    def load_model(
        cls,
        source: Union[RawModelNode, os.PathLike, str, dict],
        root_path: Optional[os.PathLike] = None,
        update_to_current_format: bool = True,
    ):
        raw_model, root_path = cls.ensure_raw_model(source, root_path, update_to_current_format)
        data_version_wo_patch = cls.get_version_tuple_wo_patch(raw_model.format_version)
        current_version_wo_patch = cls.get_current_format_version_wo_patch()
        if data_version_wo_patch > current_version_wo_patch:
            raise ValueError(
                f"You are attempting to load a model in format version {'.'.join(map(str, data_version_wo_patch))}.x "
                f"with the model spec {'.'.join(map(str, current_version_wo_patch))}"
            )
        elif data_version_wo_patch == current_version_wo_patch:
            model: ModelNode = resolve_raw_node_to_node(
                raw_node=raw_model, root_path=pathlib.Path(root_path), nodes_module=cls.nodes
            )
            assert isinstance(model, cls.nodes.Model)
        elif cls.preceding_model_loader is None:
            raise NotImplementedError(f"format version {'.'.join(map(str, data_version_wo_patch))}")
        else:
            model = cls.preceding_model_loader.load_model(raw_model, root_path, update_to_current_format)

        return model

    @classmethod
    def ensure_raw_model(cls, raw_model, root_path: Optional[os.PathLike], update_to_current_format: bool):
        if isinstance(raw_model, (os.PathLike, str, dict)):
            data, root_path_from_source = get_dict_and_root_path_from_yaml_source(raw_model)
            if root_path is None:
                root_path = root_path_from_source
            elif (
                root_path_from_source is not None
                and pathlib.Path(root_path).resolve() != root_path_from_source.resolve()
            ):
                raise ValueError(
                    f"root_path does not match source: {root_path} != {root_path_from_source}. (Leave out root_path!)"
                )

            raw_model = cls.load_raw_model(data, update_to_current_format)
        else:
            assert isinstance(raw_model, Node)
            raw_model = raw_model

        if root_path is None:
            raise TypeError("Require root_path if source is dict or raw_nodes.Model to resolve relative file paths.")

        return raw_model, root_path

    @classmethod
    def maybe_update_model_minor(cls, data: dict):
        if cls.preceding_model_loader is not None:
            data = cls.preceding_model_loader.maybe_update_model_minor(data)
            data = cls.preceding_model_loader.maybe_update_model_patch(data)

        return cls.converters.maybe_update_model_minor(data)

    @classmethod
    def maybe_update_model_patch(cls, data: dict):
        return cls.converters.maybe_update_model_patch(data)

    @classmethod
    def load_raw_model_from_dict(cls, data: dict):
        raw_model: cls.raw_nodes.Model = cls.schema.Model().load(data)
        assert isinstance(raw_model, cls.raw_nodes.Model)
        return raw_model

    @staticmethod
    def get_version_tuple_wo_patch(version: str):
        try:
            fvs = version.split(".")
            return int(fvs[0]), int(fvs[1])
        except Exception:
            raise ValidationError(f"invalid format_version '{version}'")

    @classmethod
    def get_current_format_version_wo_patch(cls):
        return cls.get_version_tuple_wo_patch(get_args(cls.raw_nodes.ModelFormatVersion)[-1])
