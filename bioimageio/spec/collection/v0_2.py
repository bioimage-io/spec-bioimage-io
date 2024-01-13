import collections.abc
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union

from pydantic import (
    Field,
    PrivateAttr,
    TypeAdapter,
    ValidationError,
    model_validator,
)
from pydantic_core import PydanticUndefined
from typing_extensions import Annotated, Self

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.field_warning import issue_warning
from bioimageio.spec._internal.io_utils import open_bioimageio_yaml
from bioimageio.spec._internal.types import BioimageioYamlContent, NotEmpty, YamlValue
from bioimageio.spec.application.v0_2 import ApplicationDescr as ApplicationDescr02
from bioimageio.spec.dataset.v0_2 import DatasetDescr as DatasetDescr
from bioimageio.spec.dataset.v0_2 import DatasetId as DatasetId
from bioimageio.spec.generic.v0_2 import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec.generic.v0_2 import AttachmentsDescr as AttachmentsDescr
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import FileSource as FileSource
from bioimageio.spec.generic.v0_2 import GenericDescr as GenericDescr02
from bioimageio.spec.generic.v0_2 import GenericDescrBase
from bioimageio.spec.generic.v0_2 import HttpUrl as HttpUrl
from bioimageio.spec.generic.v0_2 import LinkedResourceDescr as LinkedResourceDescr
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_2 import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_2 import ResourceId as ResourceId
from bioimageio.spec.model.v0_4 import ModelDescr as ModelDescr
from bioimageio.spec.notebook.v0_2 import NotebookDescr as NotebookDescr02

EntryDescr = Union[
    Annotated[Union[ModelDescr, DatasetDescr, ApplicationDescr02, NotebookDescr02], Field(discriminator="type")],
    GenericDescr02,
]


class CollectionEntry(Node, extra="allow"):
    """A valid resource description (RD).
    The entry RD is based on the collection description itself.
    Fields are added/overwritten by the content of `rdf_source` if `rdf_source` is specified,
    and finally added/overwritten by any fields specified directly in the entry.
    Except for the `id` field, fields are overwritten entirely, their content is not merged!
    The final `id` for each collection entry is composed of the collection's `id`
    and the entry's 'sub-'`id`, specified remotely as part of `rdf_source` or superseeded in-place,
    such that the `final_entry_id = <collection_id>/<entry_id>`"""

    entry_adapter: ClassVar[TypeAdapter[EntryDescr]] = TypeAdapter(EntryDescr)

    rdf_source: Union[HttpUrl, RelativeFilePath, None] = None
    """resource description file (RDF) source to load entry from"""

    id: Optional[ResourceId] = None
    """Collection entry sub id overwriting `rdf_source.id`.
    The full collection entry's id is the collection's base id, followed by this sub id and separated by a slash '/'."""

    _descr: EntryDescr = PrivateAttr()

    @property
    def rdf_update(self) -> Dict[str, YamlValue]:
        return self.model_extra or {}

    @property
    def descr(self) -> EntryDescr:
        if self._descr is PydanticUndefined:
            raise RuntimeError(
                "Collection entry description cannot be accessed. Is this entry part of a Collection? "
                "A collection entry is only valid within a collection resource description."
            )

        return self._descr


class CollectionDescr(GenericDescrBase, extra="allow", title="bioimage.io collection specification"):
    """A bioimage.io collection describes several other bioimage.io resources.
    Note that collections cannot be nested; resources listed under `collection` may not be collections themselves.
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
            if entry.rdf_source is not None:
                if not self._stored_validation_context.perform_io_checks:
                    issue_warning(
                        "Skipping IO relying validation for collection[{i}]",
                        value=entry.rdf_source,
                        val_context=self._stored_validation_context,
                        msg_context=dict(i=i),
                    )
                    continue

                external_data = open_bioimageio_yaml(entry.rdf_source, root=self._stored_validation_context.root)
                # add/overwrite common collection entry content with external source
                entry_data.update(external_data.content)

            # add/overwrite common+external entry content with in-place entry update
            entry_data.update(entry.rdf_update)

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
                raise ValueError(f"collection[{i}] has invalid entry type; collections may not be nested!")

            try:
                entry_descr = entry.entry_adapter.validate_python(entry_data)
            except ValidationError as e:
                raise ValueError(f"Invalid collection entry collection[{i}]") from e
            else:
                entry._descr = entry_descr  # pyright: ignore[reportPrivateUsage]

        return self

    @model_validator(mode="before")
    @classmethod
    def move_groups_to_collection_field(cls, data: BioimageioYamlContent) -> BioimageioYamlContent:
        if data.get("format_version") not in ("0.2.0", "0.2.1"):
            return data

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

        return data
