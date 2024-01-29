from typing import Literal, Optional, cast

from typing_extensions import Self

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.types import DatasetId as DatasetId
from bioimageio.spec._internal.utils import assert_all_params_set_explicitly
from bioimageio.spec.dataset import v0_2
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import Doi as Doi
from bioimageio.spec.generic.v0_3 import FileDescr as FileDescr
from bioimageio.spec.generic.v0_3 import GenericDescrBase
from bioimageio.spec.generic.v0_3 import HttpUrl as HttpUrl
from bioimageio.spec.generic.v0_3 import LinkedResourceDescr as LinkedResourceDescr
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3 import ResourceId as ResourceId
from bioimageio.spec.generic.v0_3 import Sha256 as Sha256


class DatasetDescr(GenericDescrBase, title="bioimage.io dataset specification"):
    """A bioimage.io dataset resource description file (dataset RDF) describes a dataset relevant to bioimage
    processing.
    """

    type: Literal["dataset"] = "dataset"

    source: Optional[HttpUrl] = None
    """"URL to the source of the dataset."""

    @classmethod
    def convert_from(cls, other: v0_2.DatasetDescr) -> Self:
        if isinstance(other, v0_2.DatasetDescr):  # pyright: ignore[reportUnnecessaryIsInstance]
            return assert_all_params_set_explicitly(cls)(
                attachments=[] if other.attachments is None else [FileDescr(source=f) for f in other.attachments.files],
                authors=[Author.convert_from(a) for a in other.authors],
                badges=other.badges,
                cite=other.cite,
                config=other.config,
                covers=other.covers,
                description=other.description,
                documentation=other.documentation,
                format_version="0.3.0",
                git_repo=cast(Optional[HttpUrl], other.git_repo),
                icon=other.icon,
                id=other.id,
                license=other.license,  # type: ignore
                links=other.links,
                maintainers=[Maintainer.convert_from(m) for m in other.maintainers],
                name=other.name,
                source=other.source,
                tags=other.tags,
                type=other.type,
                version=other.version,
                **(other.model_extra or {}),
            )
        else:
            return super().convert_from(other)


class LinkedDatasetDescr(Node):
    """Reference to a bioimage.io dataset."""

    id: DatasetId
    """A valid dataset `id` from the bioimage.io collection."""
