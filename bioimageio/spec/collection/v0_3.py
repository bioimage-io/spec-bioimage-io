from typing import ClassVar, List, Literal, Union

from pydantic import Field, TypeAdapter, field_validator
from typing_extensions import Annotated

from bioimageio.spec._internal.types import BioimageioYamlContent, NotEmpty
from bioimageio.spec._internal.validation_context import InternalValidationContext
from bioimageio.spec.application.v0_2 import ApplicationDescr as ApplicationDescr02
from bioimageio.spec.application.v0_3 import ApplicationDescr as ApplicationDescr03
from bioimageio.spec.collection import v0_2
from bioimageio.spec.dataset.v0_2 import DatasetDescr as Dataset02
from bioimageio.spec.dataset.v0_3 import DatasetDescr as Dataset03
from bioimageio.spec.generic.v0_2 import GenericDescr as GenericDescr02
from bioimageio.spec.generic.v0_3 import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec.generic.v0_3 import AttachmentDescr as AttachmentDescr
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import FileDescr as FileDescr
from bioimageio.spec.generic.v0_3 import FileSource as FileSource
from bioimageio.spec.generic.v0_3 import GenericDescr, GenericDescrBase
from bioimageio.spec.generic.v0_3 import HttpUrl as HttpUrl
from bioimageio.spec.generic.v0_3 import LinkedResourceDescr as LinkedResourceDescr
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3 import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_3 import ResourceId as ResourceId
from bioimageio.spec.generic.v0_3 import Sha256 as Sha256
from bioimageio.spec.model.v0_4 import ModelDescr as ModelDescr04
from bioimageio.spec.model.v0_5 import ModelDescr as ModelDescr05
from bioimageio.spec.notebook.v0_2 import NotebookDescr as NotebookDescr02
from bioimageio.spec.notebook.v0_3 import NotebookDescr as NotebookDescr03

_AnyApplicationDescr = Annotated[Union[ApplicationDescr02, ApplicationDescr03], Field(discriminator="format_version")]
_AnyDatasetDescr = Annotated[Union[Dataset02, Dataset03], Field(discriminator="format_version")]
_AnyModelDescr = Annotated[Union[ModelDescr04, ModelDescr05], Field(discriminator="format_version")]
_AnyNotebookDescr = Annotated[Union[NotebookDescr02, NotebookDescr03], Field(discriminator="format_version")]

EntryNode = Union[
    Annotated[
        Union[_AnyApplicationDescr, _AnyDatasetDescr, _AnyModelDescr, _AnyNotebookDescr], Field(discriminator="type")
    ],
    GenericDescr02,
    GenericDescr,
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


class CollectionDescr(GenericDescrBase, extra="allow", title="bioimage.io collection specification"):
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
        v0_2.CollectionDescr.check_unique_ids_impl(value)
        return value

    @classmethod
    def convert_from_older_format(cls, data: BioimageioYamlContent, context: InternalValidationContext) -> None:
        v0_2.CollectionDescr.move_groups_to_collection_field(data)
        super().convert_from_older_format(data, context)
