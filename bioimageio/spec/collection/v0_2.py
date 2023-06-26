import collections.abc
from typing import Any, ClassVar, Dict, Literal, Optional, Tuple, Union

import annotated_types
from pydantic import HttpUrl, TypeAdapter, model_validator
from pydantic_core.core_schema import ValidationInfo
from typing_extensions import Annotated

from bioimageio.spec.dataset.v0_2 import Dataset
from bioimageio.spec.generic.v0_2 import (
    LATEST_FORMAT_VERSION,
    FormatVersion,
    GenericDescription,
    LatestFormatVersion,
    ResourceDescriptionBase,
    ResourceDescriptionType,
)
from bioimageio.spec.model.v0_4 import Model
from bioimageio.spec.shared.nodes import Node
from bioimageio.spec.shared.types import RawMapping, RawValue

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

    model_config = {**Node.model_config, "extra": "allow"}
    """pydantic model config set to allow additional keys"""

    id: str
    """the collection entrie's sub-ID.
    Later referencing of an entry should be done as <collection's base ID>/<entrie's sub-ID>"""

    rdf_source: Union[HttpUrl, None] = None
    """resource description file (RDF) source to load entry from"""

    @property
    def rdf_update(self) -> Dict[str, RawValue]:
        return self.model_extra or {}

    entry_validator: ClassVar = TypeAdapter(Union[Model, Dataset, GenericDescription])

    @model_validator(mode="before")
    @classmethod
    def check_entry(cls, data: RawMapping, info: ValidationInfo) -> RawMapping:
        extra = {k: v for k, v in data.items() if k != "rdf_source"}
        if data.get("rdf_source") is None:
            # without external rdf_source we expect a valid resource description
            entry_data = dict(info.context["collection_base_content"])
            entry_data.update(extra)
            cls.entry_validator.validate_python(data, context=info.context)
        else:
            # cannot validate entry without resolving 'rdf_source'
            # to validate, load 'rdf_content' as extra fields to CollectionEntry
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

    # def __init__(self, *, context: Union[dict[str, Any], None] = None, **data: Any) -> None:
    #     context = context or {}
    #     context["collection_base_content"] = {k: ensure_raw(v) for k, v in data.items() if k != "collection"}
    #     super().__init__(context=context, **data)

    @classmethod
    def model_validate(
        cls,
        obj: Union[ResourceDescriptionType, Dict[str, Any]],
        *,
        strict: Optional[bool] = None,
        from_attributes: Optional[bool] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ResourceDescriptionType:
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
