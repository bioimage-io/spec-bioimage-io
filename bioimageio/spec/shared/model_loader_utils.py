from __future__ import annotations

import os
import pathlib
import typing
import warnings

from marshmallow import ValidationError, missing

from . import get_dict_and_root_path_from_yaml_source, nodes, raw_nodes
from .common import Literal, Protocol, get_args, yaml
from .raw_nodes import Node
from .schema import SharedBioImageIOSchema
from .utils import resolve_raw_node_to_node

# placeholders for versioned classes
ModelSchema = typing.TypeVar("ModelSchema", bound=SharedBioImageIOSchema)
RawModelNode = typing.TypeVar("RawModelNode", bound=raw_nodes.Node)
ModelNode = typing.TypeVar("ModelNode", bound=nodes.Node)


# placeholders for versioned modules
class ConvertersModule(Protocol):
    def maybe_update_model_minor(self, data: dict) -> dict:
        raise NotImplementedError

    def maybe_update_model_patch(self, data: dict) -> dict:
        raise NotImplementedError


class RawNodesModule(Protocol):
    ModelFormatVersion: typing.Type[Literal]
    Model: typing.Type[RawModelNode]


class NodesModule(Protocol):
    Model: typing.Type[RawModelNode]


class SchemaModule(Protocol):
    Model: typing.Type[ModelSchema]


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
    preceding_model_loader: typing.ClassVar[typing.Optional[ModelLoaderBase]]
    converters: typing.ClassVar[ConvertersModule]
    schema: typing.ClassVar[SchemaModule]
    raw_nodes: typing.ClassVar[RawNodesModule]
    nodes: typing.ClassVar[RawNodesModule]

    @classmethod
    def load_raw_model(
        cls, source: typing.Union[os.PathLike, str, dict], update_to_current_format: bool = False
    ) -> RawNodesModule.Model:
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
            raw_model = cls.load_raw_model_from_dict(data)
            assert isinstance(raw_model, cls.raw_nodes.Model)
        elif cls.preceding_model_loader is None:
            raise NotImplementedError(f"format version {'.'.join(map(str, data_version_wo_patch))}")
        else:
            raw_model = cls.preceding_model_loader.load_raw_model(data)

        return raw_model

    @classmethod
    def serialize_raw_model(cls, raw_model: RawModelNode) -> dict:
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
            serialized = cls.preceding_model_loader.serialize_raw_model(raw_model)

        return serialized

    @classmethod
    def save_raw_model(cls, raw_model: RawModelNode, path: pathlib.Path):
        warnings.warn("only saving serialized rdf, no associated resources.")
        if path.suffix != ".yaml":
            warnings.warn("saving with '.yaml' suffix is strongly encouraged.")

        serialized = cls.serialize_raw_model(raw_model)
        yaml.dump(serialized, path)

    @classmethod
    def load_model(
        cls,
        source: typing.Union[RawModelNode, os.PathLike, str, dict],
        root_path: typing.Optional[os.PathLike] = None,
        update_to_current_format: bool = True,
    ):
        if isinstance(source, (os.PathLike, str, dict)):
            data, root_path_from_source = get_dict_and_root_path_from_yaml_source(source)
            if root_path is None:
                root_path = root_path_from_source
            elif (
                root_path_from_source is not None
                and pathlib.Path(root_path).resolve() != root_path_from_source.resolve()
            ):
                raise ValueError(
                    f"root_path does not match source: {root_path} != {root_path_from_source}. (Leave out root_path!)"
                )

            raw_model = (cls.load_raw_model(data, update_to_current_format),)
        else:
            assert isinstance(source, Node)
            raw_model = source

        if root_path is None:
            raise TypeError("Require root_path if source is dict or raw_nodes.Model to resolve relative file paths.")

        model: cls.nodes.Model = resolve_raw_node_to_node(
            raw_node=raw_model, root_path=pathlib.Path(root_path), nodes_module=cls.nodes
        )
        assert isinstance(model, cls.nodes.Model)
        return model

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
