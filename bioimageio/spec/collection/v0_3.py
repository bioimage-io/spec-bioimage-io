from typing import Any, ClassVar, Dict, Literal, Tuple, Union

from pydantic import ConfigDict, Field, TypeAdapter, field_validator
from typing_extensions import Annotated

from bioimageio.spec.application.v0_2 import AnyApplication
from bioimageio.spec.collection import v0_2
from bioimageio.spec.dataset.v0_3 import AnyDataset
from bioimageio.spec.generic.v0_3 import (
    AnyGeneric,
    GenericBase,
)
from bioimageio.spec.model.v0_5 import AnyModel
from bioimageio.spec.notebook.v0_3 import AnyNotebook
from bioimageio.spec.shared.types import NonEmpty, RawDict
from bioimageio.spec.shared.validation import ValContext

__all__ = ["Collection", "CollectionEntry", "AnyCollection"]

EntryNode = Union[
    Annotated[Union[AnyModel, AnyDataset, AnyApplication, AnyNotebook], Field(discriminator="type")], AnyGeneric
]


class CollectionEntry(v0_2.CollectionEntryBase):
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
    """A bioimage.io collection resource description file (collection RDF) describes a collection of bioimage.io
    resources.
    The resources listed in a collection RDF have types other than 'collection'; collections cannot be nested.
    """

    model_config = ConfigDict(
        {
            **GenericBase.model_config,
            **ConfigDict(extra="allow", title="bioimage.io collection specification"),
        }
    )
    type: Literal["collection"] = "collection"

    @classmethod
    def _update_context_and_data(cls, context: ValContext, data: Dict[str, Any]) -> None:
        super()._update_context_and_data(context, data)
        assert "collection_base_content" not in context
        context["collection_base_content"] = {k: v for k, v in data.items() if k != "collection"}

    collection: NonEmpty[Tuple[CollectionEntry, ...]]
    """Collection entries"""

    @field_validator("collection")
    @classmethod
    def check_unique_ids(cls, value: NonEmpty[Tuple[CollectionEntry, ...]]) -> NonEmpty[Tuple[CollectionEntry, ...]]:
        v0_2.Collection.check_unique_ids_impl(value)
        return value

    @classmethod
    def convert_from_older_format(cls, data: RawDict, context: ValContext) -> None:
        v0_2.Collection.move_groups_to_collection_field(data)
        super().convert_from_older_format(data, context)


AnyCollection = Annotated[Union[v0_2.Collection, Collection], Field(discriminator="format_version")]
