from __future__ import annotations

import collections.abc
from types import MappingProxyType
from typing import Any, ClassVar, Dict, Literal, Optional, Tuple, Type, Union

from pydantic import ConfigDict, HttpUrl, TypeAdapter, model_validator
from pydantic_core.core_schema import ValidationInfo
from typing_extensions import Annotated

from bioimageio.spec._internal._warn import ALERT, warn
from bioimageio.spec.application.v0_2 import Application
from bioimageio.spec.dataset.v0_2 import Dataset
from bioimageio.spec.generic.v0_2 import (
    Generic,
    GenericBase,
    GenericBaseNoSource,
)
from bioimageio.spec.model.v0_4 import Model
from bioimageio.spec.notebook.v0_2 import Notebook
from bioimageio.spec.shared.nodes import Node
from bioimageio.spec.shared.types import NonEmpty, RawDict, RawMapping, RawValue, RelativeFilePath
from bioimageio.spec.shared.validation import ValidationContext, _validation_context_var

__all__ = ["Collection", "CollectionEntry"]


class CollectionEntry(Node):
    """A valid resource description (RD).
    The entry RD is based on the collection description itself.
    Fields are added/overwritten by the content of `rdf_source` if `rdf_source` is specified,
    and finally added/overwritten by any fields specified directly in the entry.
    Except for the `id` field, fields are overwritten entirely, their content is not merged!
    The final `id` for each collection entry is composed of the collection's `id`
    and the entry's 'sub-'`id`, specified remotely as part of `rdf_source` or superseeded in-place,
    such that the `final_entry_id = <collection_id>/<entry_id>`"""

    model_config = ConfigDict({**Node.model_config, **ConfigDict(extra="allow")})
    """pydantic model config set to allow additional keys"""

    rdf_source: Annotated[
        Union[HttpUrl, RelativeFilePath, None],
        warn(None, ALERT, "Cannot statically validate remote resource description."),
    ] = None
    """resource description file (RDF) source to load entry from"""

    @property
    def rdf_update(self) -> Dict[str, RawValue]:
        return self.model_extra or {}

    entry_classes: ClassVar[
        MappingProxyType[str, Union[Type[GenericBaseNoSource], TypeAdapter[Any]]]
    ] = MappingProxyType(dict(model=Model, dataset=Dataset, application=Application, notebook=Notebook))

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
                raise ValueError("Collections may not be nested!")

            entry_class = cls.entry_classes.get(type_, Generic) if isinstance(type_, str) else Generic
            if isinstance(entry_class, TypeAdapter):
                entry_class.validate_python(entry_data, context=info.context)
            else:
                entry_class.model_validate(entry_data, context=info.context)
        else:
            # Cannot validate entry without resolving 'rdf_source'.
            # To validate, specify the content of 'rdf_source' as extra fields.
            # warning is issued on 'rdf_source' field
            pass

        return data


class CollectionBase(Node):
    model_config = ConfigDict(
        {
            **GenericBase.model_config,
            **ConfigDict(extra="allow", title="bioimage.io collection specification"),
        }
    )
    type: Literal["collection"] = "collection"

    @classmethod
    def _get_context_and_update_data(
        cls, data: Dict[str, Any], context: Optional[ValidationContext] = None
    ) -> ValidationContext:
        if context is None:
            context = _validation_context_var.get()
        context = context.model_copy(
            update=dict(collection_base_content={k: v for k, v in data.items() if k != "collection"})
        )
        return super()._get_context_and_update_data(data, context)

    @classmethod
    def convert_from_older_format(cls, data: RawDict) -> None:
        if data.get("format_version") in ("0.2.0", "0.2.1"):
            # move all type groups to the 'collection' field
            if "collection" in data and data["collection"] is not None:
                if not isinstance(data["collection"], collections.abc.Sequence):
                    raise ValueError("Expected `collection` to not be present, or to be a list")

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

        super().convert_from_older_format(data)

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


class Collection(GenericBase, CollectionBase):
    """A bioimage.io collection resource description file (collection RDF) describes a collection of bioimage.io
    resources.
    The resources listed in a collection RDF have types other than 'collection'; collections cannot be nested.
    """

    collection: NonEmpty[Tuple[CollectionEntry, ...],]
    """Collection entries"""
