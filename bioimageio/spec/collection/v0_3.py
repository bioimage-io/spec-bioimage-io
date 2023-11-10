from typing import ClassVar, List, Literal, Union

from pydantic import Field, TypeAdapter, field_validator
from pydantic import HttpUrl as HttpUrl
from typing_extensions import Annotated

from bioimageio.spec._internal.types import BioimageioYamlContent, NotEmpty
from bioimageio.spec._internal.validation_context import InternalValidationContext
from bioimageio.spec.application.v0_2 import Application as Application02
from bioimageio.spec.application.v0_3 import Application as Application03
from bioimageio.spec.collection import v0_2
from bioimageio.spec.dataset.v0_2 import Dataset as Dataset02
from bioimageio.spec.dataset.v0_3 import Dataset as Dataset03
from bioimageio.spec.generic.v0_2 import Generic as Generic02
from bioimageio.spec.generic.v0_3 import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec.generic.v0_3 import Attachment as Attachment
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import Badge as Badge
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import FileSource as FileSource
from bioimageio.spec.generic.v0_3 import Generic, GenericBase
from bioimageio.spec.generic.v0_3 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3 import RelativeFilePath as RelativeFilePath
from bioimageio.spec.model.v0_4 import Model as Model04
from bioimageio.spec.model.v0_5 import Model as Model05
from bioimageio.spec.notebook.v0_2 import Notebook as Notebook02
from bioimageio.spec.notebook.v0_3 import Notebook as Notebook03

_AnyApplication = Annotated[Union[Application02, Application03], Field(discriminator="format_version")]
_AnyDataset = Annotated[Union[Dataset02, Dataset03], Field(discriminator="format_version")]
_AnyModel = Annotated[Union[Model04, Model05], Field(discriminator="format_version")]
_AnyNotebook = Annotated[Union[Notebook02, Notebook03], Field(discriminator="format_version")]

EntryNode = Union[
    Annotated[Union[_AnyApplication, _AnyDataset, _AnyModel, _AnyNotebook], Field(discriminator="type")],
    Generic02,
    Generic,
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


class Collection(GenericBase, extra="allow", title="bioimage.io collection specification"):
    """A bioimage.io collection resource description file (collection RDF) describes a collection of bioimage.io
    resources.
    The resources listed in a collection RDF have types other than 'collection'; collections cannot be nested.
    """

    type: Literal["collection"] = "collection"

    @classmethod
    def _update_context(cls, context: InternalValidationContext, data: BioimageioYamlContent) -> None:
        super()._update_context(context, data)
        collection_base_content = {k: v for k, v in data.items() if k != "collection"}
        assert "collection_base_content" not in context or context["collection_base_content"] == collection_base_content
        context["collection_base_content"] = collection_base_content

    collection: NotEmpty[List[CollectionEntry]]
    """Collection entries"""

    @field_validator("collection")
    @classmethod
    def check_unique_ids(cls, value: NotEmpty[List[CollectionEntry]]) -> NotEmpty[List[CollectionEntry]]:
        v0_2.Collection.check_unique_ids_impl(value)
        return value

    @classmethod
    def convert_from_older_format(cls, data: BioimageioYamlContent, context: InternalValidationContext) -> None:
        v0_2.Collection.move_groups_to_collection_field(data)
        super().convert_from_older_format(data, context)
