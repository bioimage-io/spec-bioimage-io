import collections.abc
from typing import Any, ClassVar, Dict, List, Literal, Optional, Sequence, Union

from pydantic import (
    Field,
    PrivateAttr,
    TypeAdapter,
    field_validator,
    model_validator,
)
from pydantic import (
    HttpUrl as HttpUrl,
)
from pydantic_core import PydanticUndefined
from pydantic_core.core_schema import ValidationInfo
from typing_extensions import Annotated, Self

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.constants import ALERT
from bioimageio.spec._internal.field_warning import warn
from bioimageio.spec._internal.types import BioimageioYamlContent, NotEmpty, YamlValue
from bioimageio.spec._internal.validation_context import InternalValidationContext
from bioimageio.spec.application.v0_2 import Application as Application
from bioimageio.spec.dataset.v0_2 import Dataset as Dataset
from bioimageio.spec.dataset.v0_2 import DatasetId as DatasetId
from bioimageio.spec.generic.v0_2 import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec.generic.v0_2 import Attachments as Attachments
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import Badge as Badge
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import FileSource as FileSource
from bioimageio.spec.generic.v0_2 import Generic as Generic
from bioimageio.spec.generic.v0_2 import GenericBase
from bioimageio.spec.generic.v0_2 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_2 import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_2 import ResourceId as ResourceId
from bioimageio.spec.model.v0_4 import Model as Model
from bioimageio.spec.notebook.v0_2 import Notebook as Notebook

EntryNode = Union[Annotated[Union[Model, Dataset, Application, Notebook], Field(discriminator="type")], Generic]


class CollectionEntryBase(Node, extra="allow"):
    entry_adapter: ClassVar[TypeAdapter[Any]]

    rdf_source: Annotated[
        Union[HttpUrl, RelativeFilePath, None],
        warn(None, "Cannot statically validate remote resource description.", ALERT),
    ] = None
    """resource description file (RDF) source to load entry from"""

    id: Optional[ResourceId] = None
    """Collection entry sub id overwriting `rdf_source.id`.
    The full collection entry's id is the collection's base id, followed by this sub id and separated by a slash '/'."""

    @property
    def rdf_update(self) -> Dict[str, YamlValue]:
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

    @model_validator(mode="after")
    def set_entry(self, info: ValidationInfo) -> Self:
        if self.rdf_source is not None:
            return self  # todo: add resolve_rdf_source callback

        if self.id is None:
            raise ValueError("Missing `id`")

        context = info.context
        if context is None:
            return self

        entry_data: Dict[str, Any] = context["collection_base_content"]
        base_id: Any = entry_data.pop("id", None)
        if not isinstance(base_id, (str, int, float, bool)):
            return self  # invalid base id

        entry_data.update(self.rdf_update)
        entry_data["id"] = f"{base_id}/{self.id}"

        type_ = entry_data.get("type")
        if type_ == "collection":
            raise ValueError("Collections may not be nested!")

        self._entry = self.entry_adapter.validate_python(entry_data)
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


class Collection(GenericBase, extra="allow", title="bioimage.io collection specification"):
    """A bioimage.io collection describes several other bioimage.io resources.
    Note that collections cannot be nested; resources listed under `collection` may not be collections themselves.
    """

    type: Literal["collection"] = "collection"

    collection: NotEmpty[List[CollectionEntry]]
    """Collection entries"""

    @field_validator("collection")
    @classmethod
    def check_unique_ids(cls, value: NotEmpty[List[CollectionEntry]]) -> NotEmpty[List[CollectionEntry]]:
        cls.check_unique_ids_impl(value)
        return value

    @staticmethod
    def check_unique_ids_impl(value: NotEmpty[Sequence[CollectionEntryBase]]):
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

    @classmethod
    def _update_context(cls, context: InternalValidationContext, data: BioimageioYamlContent) -> None:
        super()._update_context(context, data)
        collection_base_content = {k: v for k, v in data.items() if k != "collection"}
        assert (
            "collection_base_content" not in context or context["collection_base_content"] == collection_base_content
        ), context
        context["collection_base_content"] = collection_base_content

    @staticmethod
    def move_groups_to_collection_field(data: BioimageioYamlContent) -> None:
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
    def convert_from_older_format(cls, data: BioimageioYamlContent, context: InternalValidationContext) -> None:
        cls.move_groups_to_collection_field(data)
        super().convert_from_older_format(data, context)
