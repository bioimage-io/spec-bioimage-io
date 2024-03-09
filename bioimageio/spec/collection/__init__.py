# autogen: start
"""
implementaions of all released minor versions are available in submodules:
- collection v0_2: `bioimageio.spec.collection.v0_2.CollectionDescr` [user documentation](../../../user_docs/collection_descr_v0-2.md)
- collection v0_3: `bioimageio.spec.collection.v0_3.CollectionDescr` [user documentation](../../../user_docs/collection_descr_v0-3.md)
"""
from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

from .v0_2 import CollectionDescr as CollectionDescr_v0_2
from .v0_3 import CollectionDescr as CollectionDescr
from .v0_3 import CollectionDescr as CollectionDescr_v0_3

AnyCollectionDescr = Annotated[
    Union[CollectionDescr_v0_2, CollectionDescr_v0_3], Discriminator("format_version")
]
"""Union of any released collection desription"""
# autogen: stop
