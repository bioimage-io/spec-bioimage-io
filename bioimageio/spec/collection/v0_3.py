from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union, cast, get_args

from pydantic import PrivateAttr, model_validator
from typing_extensions import Self

from bioimageio import spec
from bioimageio.spec import application, dataset, generic, model, notebook
from bioimageio.spec._internal.base_nodes import InvalidDescription, Node
from bioimageio.spec._internal.constants import ALERT
from bioimageio.spec._internal.field_warning import issue_warning
from bioimageio.spec._internal.io_utils import open_bioimageio_yaml
from bioimageio.spec._internal.types import FileSource, NotEmpty, YamlValue
from bioimageio.spec._internal.validation_context import validation_context_var
from bioimageio.spec.collection import v0_2
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import Doi as Doi
from bioimageio.spec.generic.v0_3 import FileDescr as FileDescr
from bioimageio.spec.generic.v0_3 import (
    GenericDescrBase,
    _author_conv,  # pyright: ignore[reportPrivateUsage]
    _maintainer_conv,  # pyright: ignore[reportPrivateUsage]
)
from bioimageio.spec.generic.v0_3 import HttpUrl as HttpUrl
from bioimageio.spec.generic.v0_3 import LinkedResourceDescr as LinkedResourceDescr
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3 import ResourceId as ResourceId
from bioimageio.spec.generic.v0_3 import Sha256 as Sha256

EntryDescr = Union[
    application.v0_2.ApplicationDescr,
    application.v0_3.ApplicationDescr,
    dataset.v0_2.DatasetDescr,
    dataset.v0_3.DatasetDescr,
    model.v0_4.ModelDescr,
    model.v0_5.ModelDescr,
    notebook.v0_2.NotebookDescr,
    notebook.v0_3.NotebookDescr,
    generic.v0_2.GenericDescr,
    generic.v0_3.GenericDescr,
]


class CollectionEntry(Node, extra="allow"):
    """A collection entry description is based on the collection description itself.
    Fields are added/overwritten by the content of `descr_source` if `descr_source` is set,
    and finally added/overwritten by any fields specified directly in the entry.
    Except for the `id` field, fields are overwritten entirely, their content is not merged!
    The final `id` for each collection entry is composed of the collection's `id`
    and the entry's 'sub-'`id`, specified externally in `descr_source` or superseeded in-place,
    such that the `final_entry_id = <collection_id>/<entry_id>`"""

    entry_source: Optional[FileSource] = None
    """an external source this entry description is based on"""

    id: Optional[ResourceId] = None
    """Collection entry sub id overwriting `rdf_source.id`.
    The full collection entry's id is the collection's base id, followed by this sub id and separated by a slash '/'."""

    _descr: Optional[EntryDescr] = PrivateAttr(None)

    @property
    def entry_update(self) -> Dict[str, YamlValue]:
        return self.model_extra or {}

    @property
    def descr(self) -> Optional[EntryDescr]:
        if self._descr is None:
            issue_warning(
                "Collection entry description not set. Is this entry part of a Collection? "
                "A collection entry only has its `descr` set if it is part of a valid collection description.",
                value=None,
                severity=ALERT,
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
        context = validation_context_var.get()
        common_entry_content = {
            k: v for k, v in self.model_dump(mode="json", exclude_unset=True).items() if k not in ("id", "collection")
        }
        common_badges = common_entry_content.pop("badges", None)  # `badges` not valid for model entries
        base_id: Optional[ResourceId] = self.id

        seen_entry_ids: Dict[str, int] = {}

        for i, entry in enumerate(self.collection):
            entry_data: Dict[str, Any] = dict(common_entry_content)
            # set entry specific root as it might be adapted in the presence of an external entry source
            entry_root = context.root
            entry_file_name = context.file_name

            if entry.entry_source is not None:
                if not context.perform_io_checks:
                    issue_warning(
                        "Skipping IO relying validation for collection[{i}]",
                        value=entry.entry_source,
                        msg_context=dict(i=i),
                    )
                    continue

                external_data = open_bioimageio_yaml(entry.entry_source)
                # add/overwrite common collection entry content with external source
                entry_data.update(external_data.content)
                entry_root = external_data.original_root
                entry_file_name = external_data.original_file_name

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
                raise ValueError(f"collection[{i}].type may not be 'collection'; collections may not be nested!")

            if type_ != "model" and common_badges is not None and "badges" not in entry_data:
                # set badges from the collection root for non-model resources if not set for this specific entry
                entry_data["badges"] = common_badges

            entry_descr = spec.build_description(
                entry_data, context=context.replace(root=entry_root, file_name=entry_file_name)
            )
            assert entry_descr.validation_summary is not None
            if isinstance(entry_descr, InvalidDescription):
                raise ValueError(
                    f"Invalid collection entry collection[{i}]:\n{entry_descr.validation_summary.format(hide_source=True, root_loc=('collection', i))}"
                )
            elif isinstance(entry_descr, get_args(EntryDescr)):  # TODO: use EntryDescr as union (py>=3.10)
                entry._descr = entry_descr  # type: ignore
            else:
                raise ValueError(
                    f"{entry_descr.type} {entry_descr.format_version} entries "
                    f"are not allowed in {self.type} {self.format_version}."
                )
        return self

    @model_validator(mode="before")
    @classmethod
    def _convert(cls, data: Dict[str, Any], /) -> Dict[str, Any]:
        if (
            data.get("type") == "collection"
            and isinstance(fv := data.get("format_version"), str)
            and fv.startswith("0.2.")
        ):
            old = v0_2.CollectionDescr.load(data)
            if isinstance(old, InvalidDescription):
                return data

            return cast(
                Dict[str, Any],
                (cls if TYPE_CHECKING else dict)(
                    attachments=[] if old.attachments is None else [FileDescr(source=f) for f in old.attachments.files],
                    authors=[_author_conv.convert_as_dict(a) for a in old.authors],  # type: ignore
                    badges=old.badges,
                    cite=old.cite,
                    collection=[
                        (CollectionEntry if TYPE_CHECKING else dict)(
                            entry_source=entry.rdf_source, id=entry.id, **(entry.model_extra or {})
                        )
                        for entry in old.collection
                    ],
                    config=old.config,
                    covers=old.covers,
                    description=old.description,
                    documentation=old.documentation,
                    format_version="0.3.0",
                    git_repo=cast(Optional[HttpUrl], old.git_repo),
                    icon=old.icon,
                    id=old.id,
                    license=old.license,  # type: ignore
                    links=old.links,
                    maintainers=[_maintainer_conv.convert_as_dict(m) for m in old.maintainers],  # type: ignore
                    name=old.name,
                    tags=old.tags,
                    type=old.type,
                    version=old.version,
                    **(old.model_extra or {}),
                ),
            )

        return data
