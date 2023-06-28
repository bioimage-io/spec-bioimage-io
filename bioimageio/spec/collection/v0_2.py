from __future__ import annotations

import collections.abc
from types import MappingProxyType
from typing import Any, ClassVar, Dict, Literal, Optional, Tuple, Type, TypedDict, Union, get_args

import annotated_types
from pydantic import HttpUrl, model_validator
from pydantic_core.core_schema import ValidationInfo
from typing_extensions import Annotated

from bioimageio.spec.dataset.v0_2 import Dataset
from bioimageio.spec.generic.v0_2 import (
    LATEST_FORMAT_VERSION,
    FormatVersion,
    GenericDescription,
    KnownGenericDescription,
    KnownGenericResourceType,
    LatestFormatVersion,
    ResourceDescriptionBase,
)
from bioimageio.spec.model.v0_4 import Model
from bioimageio.spec.shared.nodes import FrozenDictNode, Node
from bioimageio.spec.shared.types import RawMapping, RawValue, RelativeFilePath
from bioimageio.spec.shared.utils import ensure_raw
from bioimageio.spec.shared.validation import WatertightWarning, warn

__all__ = ["Collection", "CollectionEntry", "LatestFormatVersion", "FormatVersion", "LATEST_FORMAT_VERSION"]


class CollectionEntry(Node):
    """Each entry needs to specify a valid RDF with an `id`.
    Each entry RDF is based on the collection RDF itself.
    Fields are added/overwritten by the content of `rdf_source` if `rdf_source` is specified,
    and added/overwritten by any fields specified directly in the entry.
    Except for the `id` field, fields are overwritten entirely, their content is not merged!
    The `id` field in `rdf_source` is ignored and the final `id` for each collection entry
    is composed of the collection RDF `id` and the entry's 'sub-'`id` specified in-place
    such that `final_entry_id = <collection_id>/<entry_id>`"""

    model_config = {**Node.model_config, **dict(extra="allow")}
    """pydantic model config set to allow additional keys"""

    rdf_source: Annotated[
        Union[HttpUrl, RelativeFilePath, None],
        warn(None, WatertightWarning, "Cannot statically validate remote resource description."),
    ] = None
    """resource description file (RDF) source to load entry from"""

    @property
    def rdf_update(self) -> Dict[str, RawValue]:
        return self.model_extra or {}

    entry_classes: ClassVar[
        MappingProxyType[
            Literal["model", "dataset", KnownGenericResourceType], Type[Union[Model, Dataset, KnownGenericDescription]]
        ]
    ] = MappingProxyType(
        dict(model=Model, dataset=Dataset, **{t: KnownGenericDescription for t in get_args(KnownGenericResourceType)})
    )

    @model_validator(mode="before")
    @classmethod
    def check_entry(cls, data: RawMapping, info: ValidationInfo) -> RawMapping:
        in_place_fields = {k: v for k, v in data.items() if k not in ("rdf_source", "id")}
        if data.get("rdf_source") is None:
            # without external rdf_source we expect a valid resource description
            entry_data = dict(info.context["collection_base_content"])
            base_id = entry_data.pop("id", None)
            entry_data.update(in_place_fields)
            if isinstance(data.get("id"), (str, int, float)) and isinstance(base_id, (str, int, float)):
                entry_data["id"] = f"{base_id}/{data['id']}"

            if (type_ := entry_data.get("type")) in cls.entry_classes:
                entry_class = cls.entry_classes[type_]  # type: ignore
            else:
                entry_class = GenericDescription
            entry_class.model_validate(entry_data, context=info.context)
        else:
            # Cannot validate entry without resolving 'rdf_source'.
            # To validate, specify the content of rdf_source as extra fields.
            pass

        return data


class Collection(ResourceDescriptionBase):
    """A bioimage.io collection resource description file (collection RDF) describes a collection of bioimage.io
    resources.
    The resources listed in a collection RDF have types other than 'collection'; collections cannot be nested.
    """

    model_config = {
        **ResourceDescriptionBase.model_config,
        **dict(title=f"bioimage.io Collection RDF {LATEST_FORMAT_VERSION}"),
    }
    type: Literal["collection"] = "collection"

    collection: Annotated[
        Tuple[CollectionEntry, ...],
        annotated_types.MinLen(1),
    ]
    """Collection entries"""

    @classmethod
    def model_validate(
        cls,
        obj: Union[Any, Dict[str, Any]],
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Collection:
        if not isinstance(obj, dict):
            obj = dict(obj)

        context = context or {}
        context["collection_base_content"] = {k: ensure_raw(v) for k, v in obj.items() if k != "collection"}

        return super().model_validate(obj, strict=strict, from_attributes=from_attributes, context=context)

    def get_collection_base_content(self) -> Dict[str, RawValue]:
        """each collection entry is based on the collection content itself (without the 'collection' field)"""
        return self.model_dump(exclude={"collection"}, exclude_unset=True)

    @classmethod
    def convert_from_older_format(cls, data: RawMapping) -> RawMapping:
        data = dict(data)
        if data.get("format_version") in ("0.2.0", "0.2.1"):
            # move all type groups to the 'collection' field
            if "collection" in data:
                assert isinstance(data["collection"], collections.abc.Sequence)
                data["collection"] = list(data["collection"])
            else:
                data["collection"] = []

            for group in ["application", "model", "dataset", "notebook"]:
                if group in data:
                    data["collection"] += data[group]  # type: ignore
                    data["collection"][-1]["type"] = group

            config = data.get("config")
            if config and isinstance(config, dict):
                id_ = config.pop("id", data.get("id"))
                if id_ is not None:
                    data["id"] = id_

        return super().convert_from_older_format(data)

    # @validates("collection")
    # def unique_ids(self, value: List[Union[dict, raw_nodes.CollectionEntry]]):
    #     ids = [
    #         (v.get("id", missing), v.get("rdf_source", missing))
    #         if isinstance(v, dict)
    #         else (v.rdf_update.get("id", missing), v.rdf_source)
    #         for v in value
    #     ]
    #     # skip check for id only specified in remote source
    #     ids = [vid for vid, vs in ids if not (vid is missing and vs is not missing)]

    #     if missing in ids:
    #         raise ValueError(f"Missing ids in collection entries")

    #     non_string_ids = [v for v in ids if not isinstance(v, str)]
    #     if non_string_ids:
    #         raise ValueError(f"Non-string ids in collection: {non_string_ids}")

    #     seen = set()
    #     duplicates = []
    #     for v in ids:
    #         if v in seen:
    #             duplicates.append(v)
    #         else:
    #             seen.add(v)

    #     if duplicates:
    #         raise ValueError(f"Duplicate ids in collection: {duplicates}")
