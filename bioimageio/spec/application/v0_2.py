from typing import Literal

from pydantic import HttpUrl as HttpUrl

from bioimageio.spec._internal.types import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_2 import Attachments as Attachments
from bioimageio.spec.generic.v0_2 import Author as Author
from bioimageio.spec.generic.v0_2 import Badge as Badge
from bioimageio.spec.generic.v0_2 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_2 import GenericBase
from bioimageio.spec.generic.v0_2 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_2 import Maintainer as Maintainer


class Application(GenericBase, frozen=True, title="bioimage.io application specification"):
    """Bioimage.io description of an application."""

    type: Literal["application"] = "application"
