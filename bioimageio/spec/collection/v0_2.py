import collections.abc
from functools import partial
from types import MappingProxyType
from typing import Any, Dict, List, Literal, Optional, Union, get_args

from pydantic import (
    PrivateAttr,
    model_validator,
)
from typing_extensions import Self

from .._build_description import build_description_impl, get_rd_class_impl
from .._internal.common_nodes import InvalidDescr, Node
from .._internal.field_warning import issue_warning
from .._internal.io import BioimageioYamlContent, YamlValue
from .._internal.io_basics import AbsoluteFilePath as AbsoluteFilePath
from .._internal.io_utils import open_bioimageio_yaml
from .._internal.types import ApplicationId as ApplicationId
from .._internal.types import CollectionId as CollectionId
from .._internal.types import DatasetId as DatasetId
from .._internal.types import ModelId as ModelId
from .._internal.types import NotebookId as NotebookId
from .._internal.types import NotEmpty
from .._internal.url import HttpUrl as HttpUrl
from .._internal.validation_context import validation_context_var
from .._internal.warning_levels import ALERT
from ..application import ApplicationDescr_v0_2, ApplicationDescr_v0_3
from ..dataset import DatasetDescr_v0_2, DatasetDescr_v0_3
from ..generic import GenericDescr_v0_2, GenericDescr_v0_3
from ..generic.v0_2 import AttachmentsDescr as AttachmentsDescr
from ..generic.v0_2 import Author as Author
from ..generic.v0_2 import BadgeDescr as BadgeDescr
from ..generic.v0_2 import CiteEntry as CiteEntry
from ..generic.v0_2 import Doi as Doi
from ..generic.v0_2 import FileSource, GenericDescrBase
from ..generic.v0_2 import LinkedResource as LinkedResource
from ..generic.v0_2 import Maintainer as Maintainer
from ..generic.v0_2 import OrcidId as OrcidId
from ..generic.v0_2 import RelativeFilePath as RelativeFilePath
from ..generic.v0_2 import ResourceId as ResourceId
from ..generic.v0_2 import Uploader as Uploader
from ..generic.v0_2 import Version as Version
from ..model import ModelDescr_v0_4, ModelDescr_v0_5
from ..notebook import NotebookDescr_v0_2, NotebookDescr_v0_3

EntryDescr = Union[
    ApplicationDescr_v0_2,
    DatasetDescr_v0_2,
    GenericDescr_v0_2,
    ModelDescr_v0_4,
    NotebookDescr_v0_2,
]

_ENTRY_DESCR_MAP = MappingProxyType(
    {
        None: MappingProxyType(
            {
                "0.2": GenericDescr_v0_2,
                "0.3": GenericDescr_v0_3,
                None: GenericDescr_v0_2,
            }
        ),
        "generic": MappingProxyType(
            {
                "0.2": GenericDescr_v0_2,
                "0.3": GenericDescr_v0_3,
                None: GenericDescr_v0_2,
            }
        ),
        "application": MappingProxyType(
            {
                "0.2": ApplicationDescr_v0_2,
                "0.3": ApplicationDescr_v0_3,
                None: ApplicationDescr_v0_2,
            }
        ),
        "dataset": MappingProxyType(
            {
                "0.2": DatasetDescr_v0_2,
                "0.3": DatasetDescr_v0_3,
                None: DatasetDescr_v0_2,
            }
        ),
        "notebook": MappingProxyType(
            {
                "0.2": NotebookDescr_v0_2,
                "0.3": NotebookDescr_v0_3,
                None: NotebookDescr_v0_2,
            }
        ),
        "model": MappingProxyType(
            {
                "0.3": ModelDescr_v0_4,
                "0.4": ModelDescr_v0_4,
                "0.5": ModelDescr_v0_5,
                None: ModelDescr_v0_4,
            }
        ),
    }
)


class CollectionEntry(Node, extra="allow"):
    """A valid resource description (RD).
    The entry RD is based on the collection description itself.
    Fields are added/overwritten by the content of `rdf_source` if `rdf_source` is specified,
    and finally added/overwritten by any fields specified directly in the entry.
    Except for the `id` field, fields are overwritten entirely, their content is not merged!
    The final `id` for each collection entry is composed of the collection's `id`
    and the entry's 'sub-'`id`, specified remotely as part of `rdf_source` or superseeded in-place,
    such that the `final_entry_id = <collection_id>/<entry_id>`"""

    rdf_source: Optional[FileSource] = None
    """resource description file (RDF) source to load entry from"""

    id: Optional[Union[ResourceId, DatasetId, ApplicationId, ModelId, NotebookId]] = (
        None
    )
    """Collection entry sub id overwriting `rdf_source.id`.
    The full collection entry's id is the collection's base id, followed by this sub id and separated by a slash '/'."""

    _descr: Optional[EntryDescr] = PrivateAttr(None)

    @property
    def rdf_update(self) -> Dict[str, YamlValue]:
        return self.model_extra or {}

    @property
    def descr(self) -> Optional[EntryDescr]:
        if self._descr is None:
            issue_warning(
                "Collection entry description not set. Is this entry part of a"
                + " Collection? A collection entry only has its `descr` set if it is part"
                + " of a valid collection description.",
                value=None,
                severity=ALERT,
            )

        return self._descr


class CollectionDescr(
    GenericDescrBase, extra="allow", title="bioimage.io collection specification"
):
    """A bioimage.io collection describes several other bioimage.io resources.
    Note that collections cannot be nested; resources listed under `collection` may not be collections themselves.
    """

    type: Literal["collection"] = "collection"

    id: Optional[CollectionId] = None
    """Model zoo (bioimage.io) wide, unique identifier (assigned by bioimage.io)"""

    collection: NotEmpty[List[CollectionEntry]]
    """Collection entries"""

    @model_validator(mode="after")
    def finalize_entries(self) -> Self:
        context = validation_context_var.get()
        common_entry_content = {
            k: v
            for k, v in self.model_dump(mode="json", exclude_unset=True).items()
            if k not in ("id", "collection")
        }
        common_badges = common_entry_content.pop(
            "badges", None
        )  # `badges` not valid for model entries
        base_id: Optional[CollectionId] = self.id

        seen_entry_ids: Dict[str, int] = {}

        for i, entry in enumerate(self.collection):
            entry_data: Dict[str, Any] = dict(common_entry_content)
            # set entry specific root as it might be adapted in the presence of an external entry source
            entry_root = context.root
            entry_file_name = context.file_name

            if entry.rdf_source is not None:
                if not context.perform_io_checks:
                    issue_warning(
                        "Skipping IO relying validation for collection[{i}]",
                        value=entry.rdf_source,
                        msg_context=dict(i=i),
                    )
                    continue

                external_data = open_bioimageio_yaml(entry.rdf_source)
                # add/overwrite common collection entry content with external source
                entry_data.update(external_data.content)
                entry_root = external_data.original_root
                entry_file_name = external_data.original_file_name

            # add/overwrite common+external entry content with in-place entry update
            entry_data.update(entry.rdf_update)

            # also update explicitly specified `id` field data
            if entry.id is not None:
                entry_data["id"] = entry.id

            if "id" in entry_data:
                entry_id = str(entry_data["id"])
                if (seen_i := seen_entry_ids.get(entry_id)) is not None:
                    raise ValueError(
                        f"Dublicate `id` '{entry_data['id']}' in"
                        + f" collection[{seen_i}]/collection[{i}]"
                    )

                seen_entry_ids[entry_id] = i
            else:
                raise ValueError(f"Missing `id` for entry {i}")

            if base_id is not None:
                entry_data["id"] = f"{base_id}/{entry_data['id']}"

            type_ = entry_data.get("type")
            if type_ == "collection":
                raise ValueError(
                    f"collection[{i}] has invalid entry type; collections may not be"
                    + " nested!"
                )

            if (
                type_ != "model"
                and common_badges is not None
                and "badges" not in entry_data
            ):
                # set badges from the collection root for non-model resources if not set for this specific entry
                entry_data["badges"] = common_badges

            entry_descr = build_description_impl(
                entry_data,
                context=context.replace(root=entry_root, file_name=entry_file_name),
                get_rd_class=partial(
                    get_rd_class_impl, descriptions_map=_ENTRY_DESCR_MAP
                ),
            )
            assert entry_descr.validation_summary is not None
            if isinstance(entry_descr, InvalidDescr):
                raise ValueError(
                    "Invalid collection entry"
                    + f" collection[{i}]:\n"
                    + f"{entry_descr.validation_summary.format(hide_source=True, hide_env=True, root_loc=('collection', i))}"
                )
            elif isinstance(
                entry_descr, get_args(EntryDescr)
            ):  # TODO: use EntryDescr as union (py>=3.10)
                entry._descr = entry_descr  # type: ignore
            else:
                raise ValueError(
                    f"{entry_descr.type} {entry_descr.format_version} entries"
                    + f" are not allowed in {self.type} {self.format_version}."
                )

        return self

    @model_validator(mode="before")
    @classmethod
    def move_groups_to_collection_field(
        cls, data: BioimageioYamlContent
    ) -> BioimageioYamlContent:
        if data.get("format_version") not in ("0.2.0", "0.2.1"):
            return data

        if "collection" in data and data["collection"] is not None:
            if not isinstance(data["collection"], collections.abc.Sequence):
                raise ValueError(
                    "Expected `collection` to not be present, or to be a list"
                )

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


class LinkedCollection(Node):
    """Reference to a bioimage.io collection."""

    id: CollectionId
    """A valid collection `id` from the bioimage.io collection."""

    version_number: Optional[int] = None
    """version number (n-th published version, not the semantic version) of linked collection"""
