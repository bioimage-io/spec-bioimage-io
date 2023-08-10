import collections.abc
from typing import Any, ClassVar, Dict, Literal, Optional, Tuple, Union

from pydantic import ConfigDict, Field, HttpUrl, PrivateAttr, TypeAdapter, field_validator, model_validator
from pydantic_core import PydanticUndefined
from pydantic_core.core_schema import ValidationInfo
from typing_extensions import Annotated, Self

from bioimageio.spec._internal._warn import ALERT, warn
from bioimageio.spec.application.v0_2 import AnyApplication
from bioimageio.spec.dataset.v0_2 import AnyDataset
from bioimageio.spec.generic.v0_2 import (
    AnyGeneric,
    GenericBase,
)
from bioimageio.spec.model.v0_4 import AnyModel
from bioimageio.spec.notebook.v0_2 import AnyNotebook
from bioimageio.spec.shared.nodes import Node
from bioimageio.spec.shared.types import NonEmpty, RawDict, RawValue, RelativeFilePath
from bioimageio.spec.shared.validation import ValidationContext, validation_context_var

__all__ = ["Collection", "CollectionEntry", "AnyCollection"]

EntryNode = Union[
    Annotated[Union[AnyModel, AnyDataset, AnyApplication, AnyNotebook], Field(discriminator="type")], AnyGeneric
]


class CollectionEntryBase(Node):
    model_config = ConfigDict({**Node.model_config, **ConfigDict(extra="allow")})
    """pydantic model config set to allow additional keys"""

    entry_adapter: ClassVar[TypeAdapter[Any]]

    rdf_source: Annotated[
        Union[HttpUrl, RelativeFilePath, None],
        warn(None, ALERT, "Cannot statically validate remote resource description."),
    ] = None
    """resource description file (RDF) source to load entry from"""

    id: Optional[NonEmpty[str]] = None
    """Collection entry sub id overwriting `rdf_source.id`.
    The full collection entry's id is the collection's base id, followed by this sub id and separated by a slash '/'."""

    @property
    def rdf_update(self) -> Dict[str, RawValue]:
        return self.model_extra or {}

    @property
    def entry(self) -> Any:
        if self._entry is PydanticUndefined:
            raise RuntimeError(
                "Collection entry cannot be accessed. Is this entry part of a Collection? "
                "A collection entry is only valid within a collection resrouce description."
            )

        return self._entry

    _entry: Any = PrivateAttr()

    @model_validator(mode="after")  # type: ignore
    def set_entry(self) -> Self:
        if self.rdf_source is not None:
            return self  # todo: add resolve_rdf_source callback

        if self.id is None:
            raise ValueError("Missing `id`")

        context = validation_context_var.get()
        if context.collection_base_content is None:
            return self

        entry_data: Dict[str, Any] = context.collection_base_content
        base_id: Any = entry_data.pop("id", None)
        if not isinstance(base_id, (str, int, float, bool)):
            return self  # invalid base id

        entry_data.update(self.rdf_update)
        entry_data["id"] = f"{base_id}/{self.id}"

        type_ = entry_data.get("type")
        if type_ == "collection":
            raise ValueError("Collections may not be nested!")

        entry = self.entry_adapter.validate_python(entry_data)
        object.__setattr__(self, "_entry", entry)
        return self


class CollectionEntry(CollectionEntryBase):
    """A valid resource description (RD).
    The entry RD is based on the collection description itself.
    Fields are added/overwritten by the content of `rdf_source` if `rdf_source` is specified,
    and finally added/overwritten by any fields specified directly in the entry.
    Except for the `id` field, fields are overwritten entirely, their content is not merged!
    The final `id` for each collection entry is composed of the collection's `id`
    and the entry's 'sub-'`id`, specified remotely as part of `rdf_source` or superseeded in-place,
    such that the `final_entry_id = <collection_id>/<entry_id>`"""

    entry_adapter: ClassVar[TypeAdapter[EntryNode]] = TypeAdapter(EntryNode)
    _entry: EntryNode

    @property
    def entry(self) -> EntryNode:
        return self._entry


class Collection(GenericBase):
    """A bioimage.io collection describes several other bioimage.io resources.
    Note that collections cannot be nested; resources listed under `collection` may not be collections themselves.
    """

    model_config = ConfigDict(
        {
            **GenericBase.model_config,
            **ConfigDict(extra="allow", title="bioimage.io collection specification"),
        }
    )
    type: Literal["collection"] = "collection"

    @classmethod
    def _update_data_and_context(cls, data: Dict[str, Any]) -> None:
        super()._update_data_and_context(data)
        context = validation_context_var.get()
        assert context.collection_base_content is None
        context.collection_base_content = {k: v for k, v in data.items() if k != "collection"}

    collection: NonEmpty[Tuple[CollectionEntry, ...]]
    """Collection entries"""

    @field_validator("collection")
    @classmethod
    def check_unique_ids(cls, value: NonEmpty[Tuple[CollectionEntry, ...]]) -> NonEmpty[Tuple[CollectionEntry, ...]]:
        cls.check_unique_ids_impl(value)
        return value

    @staticmethod
    def check_unique_ids_impl(value: NonEmpty[Tuple[CollectionEntryBase, ...]]):
        seen: Dict[str, int] = {}
        for i, v in enumerate(value):
            if v.id is None:
                if v.rdf_source is not None:
                    continue  # cannot check id in rdf_source
                raise ValueError(f"Missing `id` field in collection[{i}]")
                # error: pydantic_core.InitErrorDetails = {
                #     "type": pydantic_core.PydanticCustomError("value_error", "Missing `id` field."),
                #     "loc": ("collection", i),
                #     "input": v,
                # }
                # raise pydantic_core.ValidationError("Collection", [error])

            if v.id in seen:
                raise ValueError(f"Dublicate `id` in collection[{v.id}]/collection[{i}]")
                # error = {
                #     "type": pydantic_core.PydanticCustomError(
                #         "value_error",
                #         "Duplicate `id` in collection[{previous_entry}].",
                #         dict(previous_entry=seen[v.id]),
                #     ),
                #     "loc": ("collection", i),
                #     "input": v,
                # }
                # raise pydantic_core.ValidationError("Collection", [error])

            seen[v.id] = i

    @staticmethod
    def move_groups_to_collection_field(data: RawDict) -> None:
        if data.get("format_version") not in ("0.2.0", "0.2.1"):
            return

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

    @classmethod
    def convert_from_older_format(cls, data: RawDict, raise_unconvertable: bool) -> None:
        cls.move_groups_to_collection_field(data)
        super().convert_from_older_format(data, raise_unconvertable)


AnyCollection = Collection
