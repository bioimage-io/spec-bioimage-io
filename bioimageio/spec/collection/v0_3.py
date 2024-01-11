from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

from pydantic import Field, PrivateAttr, TypeAdapter, ValidationError, model_validator
from pydantic_core import PydanticUndefined
from typing_extensions import Annotated, Self

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.field_warning import issue_warning
from bioimageio.spec._internal.io_utils import open_bioimageio_yaml
from bioimageio.spec._internal.types import BioimageioYamlContent, NotEmpty, YamlValue
from bioimageio.spec._internal.validation_context import InternalValidationContext
from bioimageio.spec.application.v0_2 import ApplicationDescr as ApplicationDescr02
from bioimageio.spec.application.v0_3 import ApplicationDescr as ApplicationDescr03
from bioimageio.spec.collection import v0_2
from bioimageio.spec.dataset.v0_2 import DatasetDescr as Dataset02
from bioimageio.spec.dataset.v0_3 import DatasetDescr as Dataset03
from bioimageio.spec.generic.v0_2 import GenericDescr as GenericDescr02
from bioimageio.spec.generic.v0_3 import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import Doi as Doi
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

EntryDescr = Union[
    Annotated[
        Union[_AnyApplicationDescr, _AnyDatasetDescr, _AnyModelDescr, _AnyNotebookDescr], Field(discriminator="type")
    ],
    GenericDescr02,
    GenericDescr,
]


class CollectionEntry(Node, extra="allow"):
    """A collection entry description is based on the collection description itself.
    Fields are added/overwritten by the content of `descr_source` if `descr_source` is set,
    and finally added/overwritten by any fields specified directly in the entry.
    Except for the `id` field, fields are overwritten entirely, their content is not merged!
    The final `id` for each collection entry is composed of the collection's `id`
    and the entry's 'sub-'`id`, specified externally in `descr_source` or superseeded in-place,
    such that the `final_entry_id = <collection_id>/<entry_id>`"""

    entry_adapter: ClassVar[TypeAdapter[EntryDescr]] = TypeAdapter(EntryDescr)

    entry_source: Union[HttpUrl, RelativeFilePath, None] = None
    """an external source this entry description is based on"""

    id: Optional[ResourceId] = None
    """Collection entry sub id overwriting `rdf_source.id`.
    The full collection entry's id is the collection's base id, followed by this sub id and separated by a slash '/'."""

    _descr: EntryDescr = PrivateAttr()

    @property
    def entry_update(self) -> Dict[str, YamlValue]:
        return self.model_extra or {}

    @property
    def descr(self) -> EntryDescr:
        if self._descr is PydanticUndefined:
            raise RuntimeError(
                "Collection entry description cannot be accessed. Is this entry part of a Collection? "
                "A collection entry is only valid as part of a collection description."
            )

        return self._descr


class CollectionDescr(GenericDescrBase, extra="allow", title="bioimage.io collection specification"):
    """A bioimage.io collection resource description file (collection RDF) describes a collection of bioimage.io
    resources.
    The resources listed in a collection RDF have types other than 'collection'; collections cannot be nested.
    """

    type: Literal["collection"] = "collection"

    collection: NotEmpty[List[CollectionEntry]]
    """Collection entries"""

    @model_validator(mode="after")
    def finalize_entries(self) -> Self:
        common_entry_content = {k: v for k, v in self if k not in ("id", "collection")}
        base_id: Optional[ResourceId] = self.id

        seen_entry_ids: Dict[str, int] = {}

        for i, entry in enumerate(self.collection):
            entry_data: Dict[str, Any] = dict(common_entry_content)
            if entry.entry_source is not None:
                if not self._internal_validation_context["perform_io_checks"]:
                    issue_warning(
                        "Skipping IO relying validation for collection[{i}]",
                        value=entry.entry_source,
                        val_context=self._internal_validation_context,
                        msg_context=dict(i=i),
                    )
                    continue

                external_data = open_bioimageio_yaml(entry.entry_source)
                # add/overwrite common collection entry content with external source
                entry_data.update(external_data.content)

            # add/overwrite common+external entry content with in-place entry update
            entry_data.update(entry.entry_update)

            # also update explicitly specified `id` field data
            if entry.id is not None:
                entry_data["id"] = entry.id

            if "id" in entry_data:
                if (seen_i := seen_entry_ids.get(entry_data["id"])) is not None:
                    raise ValueError(f"Dublicate `id` '{entry_data['id']}' in collection[{seen_i}]/collection[{i}]")

                seen_entry_ids[entry_data["id"]] = i
            else:
                raise ValueError(f"Missing `id` for entry {i}")

            if base_id is not None:
                entry_data["id"] = f"{base_id}/{entry_data['id']}"

            type_ = entry_data.get("type")
            if type_ == "collection":
                raise ValueError(f"collection[{i}] has invalid type; collections may not be nested!")

            try:
                entry_descr = entry.entry_adapter.validate_python(entry_data)
            except ValidationError as e:
                raise ValueError(f"Invalid entry at collection[{i}]") from e
            else:
                entry._descr = entry_descr  # pyright: ignore[reportPrivateUsage]

        return self

    @classmethod
    def convert_from_older_format(cls, data: BioimageioYamlContent, context: InternalValidationContext) -> None:
        v0_2.CollectionDescr.move_groups_to_collection_field(data)
        super().convert_from_older_format(data, context)
