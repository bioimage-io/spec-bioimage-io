from __future__ import annotations

import collections.abc
from types import MappingProxyType
from typing import Any, ClassVar, Dict, Literal, Optional, Tuple, Type, Union

import annotated_types
from pydantic import HttpUrl, model_validator
from pydantic_core.core_schema import ValidationInfo
from typing_extensions import Annotated

from bioimageio.spec.application.v0_2 import Application
from bioimageio.spec.notebook.v0_2 import Notebook
from bioimageio.spec.dataset.v0_2 import Dataset
from bioimageio.spec.generic.v0_2 import (
    Generic,
    LATEST_FORMAT_VERSION,
    FormatVersion,
    LatestFormatVersion,
    ResourceDescriptionBase,
    ResourceDescriptionBaseNoSource,
)
from bioimageio.spec.model.v0_4 import Model
from bioimageio.spec.shared.nodes import Node
from bioimageio.spec.shared.types import RawMapping, RawValue, RelativeFilePath
from bioimageio.spec._internal._utils._various import ensure_raw
from bioimageio.spec._internal._warn import ALERT, warn

__all__ = ["Collection", "CollectionEntry", "LatestFormatVersion", "FormatVersion", "LATEST_FORMAT_VERSION"]


class CollectionEntry(Node):
    """A valid resource description (RD).
    The entry RD is based on the collection description itself.
    Fields are added/overwritten by the content of `rdf_source` if `rdf_source` is specified,
    and finally added/overwritten by any fields specified directly in the entry.
    Except for the `id` field, fields are overwritten entirely, their content is not merged!
    The final `id` for each collection entry is composed of the collection's `id`
    and the entry's 'sub-'`id`, specified remotely as part of `rdf_source` or superseeded in-place,
    such that the `final_entry_id = <collection_id>/<entry_id>`"""

    model_config = {**Node.model_config, **dict(extra="allow")}
    """pydantic model config set to allow additional keys"""

    rdf_source: Annotated[
        Union[HttpUrl, RelativeFilePath, None],
        warn(None, ALERT, "Cannot statically validate remote resource description."),
    ] = None
    """resource description file (RDF) source to load entry from"""

    @property
    def rdf_update(self) -> Dict[str, RawValue]:
        return self.model_extra or {}

    entry_classes: ClassVar[MappingProxyType[str, Type[ResourceDescriptionBaseNoSource]]] = MappingProxyType(
        dict(model=Model, dataset=Dataset, application=Application, notebook=Notebook)
    )

    @model_validator(mode="before")
    @classmethod
    def check_entry(cls, data: RawMapping, info: ValidationInfo) -> RawMapping:
        in_place_fields = {k: v for k, v in data.items() if k not in ("rdf_source", "id")}
        if data.get("rdf_source") is None:
            # without external rdf_source we expect a valid resource description
            entry_data: Dict[str, Any] = dict(info.context["collection_base_content"])  # type: ignore
            base_id: Any = entry_data.pop("id", None)
            entry_data.update(in_place_fields)
            if isinstance(data.get("id"), (str, int, float)) and isinstance(base_id, (str, int, float)):
                entry_data["id"] = f"{base_id}/{data['id']}"

            type_ = entry_data.get("type")
            if type_ == "collection":
                raise ValueError(f"Collections may not be nested!")

            entry_class = cls.entry_classes.get(type_, Generic) if isinstance(type_, str) else Generic
            entry_class.model_validate(entry_data, context=info.context)
        else:
            # Cannot validate entry without resolving 'rdf_source'.
            # To validate, specify the content of 'rdf_source' as extra fields.
            # warning is issued on 'rdf_source' field
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
