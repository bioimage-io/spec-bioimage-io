import collections.abc
from multiprocessing import RawValue
from typing import Annotated, Any, Literal, Union
import annotated_types

from pydantic import HttpUrl, Extra, TypeAdapter, model_validator
from pydantic_core.core_schema import ValidationInfo
from bioimageio.spec.dataset.v0_2 import Dataset
from bioimageio.spec.model.v0_4 import Model

from bioimageio.spec.shared.utils import ensure_raw
from bioimageio.spec.shared.fields import Field
from bioimageio.spec.shared.nodes import Node
from bioimageio.spec.shared.types_ import RawMapping, RawValue
from ..general.v0_2 import (
    ResourceDescriptionBase,
    LatestFormatVersion,
    FormatVersion,
    LATEST_FORMAT_VERSION,
    ResourceDescription,
)


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

    model_config = {**Node.model_config, **dict(extra=Extra.allow)}
    """pydantic model config set to allow additional keys"""

    id: str
    """the collection entrie's sub-ID.
    Later referencing of an entry should be done as <collection's base ID>/<entrie's sub-ID>"""

    rdf_source: Union[HttpUrl, None] = None
    """resource description file (RDF) source to load entry from"""

    @property
    def rdf_update(self) -> dict[str, RawValue]:
        return self.model_extra or {}

    entry_validator: ClassVar[TypeAdapter] = TypeAdapter(Union[Model, Dataset, ResourceDescription])

    @model_validator(mode="before")
    @classmethod
    def check_entry(cls, data: RawMapping, info: ValidationInfo) -> RawMapping:
        extra = {k: v for k, v in data.items() if k != "rdf_source"}
        if data.get("rdf_source") is None:
            # without external rdf_source we expect a valid resource description
            entry_data = dict(info.context["collection_base_content"])
            entry_data.update(extra)
            entry_validator = TypeAdapter()
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
        tuple[CollectionEntry, ...],
        annotated_types.Len(min_length=1),
    ]
    """Collection entries"""

    def __init__(self, *, _context: Union[dict[str, Any], None] = None, **data: Any) -> None:
        context = _context or {}
        context["collection_base_content"] = {k: ensure_raw(v) for k, v in data.items() if k != "collection"}
        super().__init__(_context=context, **data)

    def get_collection_base_content(self) -> dict[str, RawValue]:
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
                    data["collection"] += data[group]
                    data["collection"][-1]["type"] = group

            config = data.get("config")
            if config and isinstance(config, dict):
                id_ = config.pop("id", data.get("id"))
                if id_ is not None:
                    data["id"] = id_

        return super().convert_from_older_format(data)
