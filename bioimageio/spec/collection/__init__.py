# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- collection v0_2: `bioimageio.spec.collection.v0_2.CollectionDescr` [user documentation](../../../user_docs/collection_descr_v0-2.md)
- collection v0_3: `bioimageio.spec.collection.v0_3.CollectionDescr` [user documentation](../../../user_docs/collection_descr_v0-3.md)
"""
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from . import v0_2 as v0_2, v0_3 as v0_3
from .v0_3 import CollectionDescr as CollectionDescr

AnyCollectionDescr = Annotated[
    Union[v0_2.CollectionDescr, v0_3.CollectionDescr], Discriminator("format_version")
]
"""Union of any released collection desription"""
# autogen: stop
