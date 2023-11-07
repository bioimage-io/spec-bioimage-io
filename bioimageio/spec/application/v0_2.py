from typing import Literal, Optional

from pydantic import Field
from pydantic import HttpUrl as HttpUrl
from typing_extensions import Annotated

from bioimageio.spec._internal.types import FileSource as FileSource
from bioimageio.spec._internal.types import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_2 import Attachments as Attachments
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import Badge as Badge
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import GenericBase, WithGenericFormatVersion
from bioimageio.spec.generic.v0_2 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer


class Application(GenericBase, WithGenericFormatVersion, title="bioimage.io application specification"):
    """Bioimage.io description of an application."""

    type: Literal["application"] = "application"

    source: Annotated[Optional[FileSource], Field(description="URL or path to the source of the application")] = None
    """The primary source of the application"""
