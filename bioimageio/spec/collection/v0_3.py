from __future__ import annotations

from types import MappingProxyType
from typing import Any, ClassVar, Tuple, Type, Union

from pydantic import TypeAdapter

from bioimageio.spec import generic
from bioimageio.spec.application import AnyApplication
from bioimageio.spec.collection import v0_2
from bioimageio.spec.dataset import AnyDataset
from bioimageio.spec.model import AnyModel
from bioimageio.spec.notebook import AnyNotebook
from bioimageio.spec.shared.types import NonEmpty

__all__ = ["Collection", "CollectionEntry"]


class CollectionEntry(v0_2.CollectionEntry):
    """A valid resource description (RD).
    The entry RD is based on the collection description itself.
    Fields are added/overwritten by the content of `rdf_source` if `rdf_source` is specified,
    and finally added/overwritten by any fields specified directly in the entry.
    Except for the `id` field, fields are overwritten entirely, their content is not merged!
    The final `id` for each collection entry is composed of the collection's `id`
    and the entry's 'sub-'`id`, specified remotely as part of `rdf_source` or superseeded in-place,
    such that the `final_entry_id = <collection_id>/<entry_id>`"""

    entry_classes: ClassVar[
        MappingProxyType[str, Union[Type[generic.v0_2.GenericBaseNoSource], TypeAdapter[Any]]]
    ] = MappingProxyType(
        dict(
            model=TypeAdapter(AnyModel),
            dataset=TypeAdapter(AnyDataset),
            application=TypeAdapter(AnyApplication),
            notebook=TypeAdapter(AnyNotebook),
        )
    )


class Collection(generic.v0_3.GenericBase, v0_2.CollectionBase):
    """A bioimage.io collection resource description file (collection RDF) describes a collection of bioimage.io
    resources.
    The resources listed in a collection RDF have types other than 'collection'; collections cannot be nested.
    """

    collection: NonEmpty[Tuple[CollectionEntry, ...],]
    """Collection entries"""
