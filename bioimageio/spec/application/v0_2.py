from typing import Literal, Optional

from pydantic import Field
from typing_extensions import Annotated

from bioimageio.spec._internal.types import ImportantFileSource
from bioimageio.spec.generic.v0_2 import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec.generic.v0_2 import AttachmentsDescr as AttachmentsDescr
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import Doi as Doi
from bioimageio.spec.generic.v0_2 import GenericDescrBase
from bioimageio.spec.generic.v0_2 import HttpUrl as HttpUrl
from bioimageio.spec.generic.v0_2 import LinkedResourceDescr as LinkedResourceDescr
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_2 import OrcidId as OrcidId
from bioimageio.spec.generic.v0_2 import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_2 import ResourceId as ResourceId
from bioimageio.spec.generic.v0_2 import Uploader as Uploader


class ApplicationDescr(GenericDescrBase, title="bioimage.io application specification"):
    """Bioimage.io description of an application."""

    type: Literal["application"] = "application"

    source: Annotated[
        Optional[ImportantFileSource],
        Field(description="URL or path to the source of the application"),
    ] = None
    """The primary source of the application"""
