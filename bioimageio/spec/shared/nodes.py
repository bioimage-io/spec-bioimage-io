from collections.abc import Callable
from typing import Any, Hashable, Union

import pydantic

# if pydantic.VERSION == "2.0b2":


class Node(
    pydantic.BaseModel,
):
    """Subpart of a resource description"""

    model_config = dict(
        extra=pydantic.Extra.forbid,
        frozen=True,
    )
    """pydantic model config"""

    @pydantic.field_validator("*", mode="after")
    def unique_sequence_entries(cls, value: Union[tuple[Hashable, ...], list[Hashable], Any]):
        if isinstance(value, (tuple, list)) and len(value) != len(set(value)):
            raise ValueError("Expected unique values")

        return value


# else:
# class Node(
#     pydantic.BaseModel,
#     extra=pydantic.Extra.forbid,
#     allow_mutation=False,
#     underscore_attrs_are_private=True,
#     validate_assignment=True,
# ):
#     pass


# class ResourceDescription(Node):
#     """Bare minimum for resource description nodes
#     This is not part of any specification for the BioImage.IO Model Zoo and, e.g.
#     not to be confused with the definition of the general RDF.
#     """

#     format_version: str = missing
#     name: str = missing
#     type: str = missing
#     version: Union[_Missing, packaging.version.Version] = missing
#     root_path: Union[pathlib.Path, URI] = pathlib.Path()  # note: `root_path` is not officially part of the spec,
#     #                                                    but any RDF has it as it is the folder containing the rdf.yaml
