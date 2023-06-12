from pathlib import Path
from typing import Literal, get_args
from bioimageio.spec.rdf.v0_2.nodes import Author, RdfBase
from bioimageio.spec.shared.fields import Field

LatestFormatVersion = Literal["0.4.9"]
FormatVersion = Literal[
    "0.4.0", "0.4.1", "0.4.2", "0.4.3", "0.4.4", "0.4.5", "0.4.6", "0.4.7", "0.4.8", LatestFormatVersion
]
WeightsFormat = Literal[
    "pytorch_state_dict", "torchscript", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"
]

LATEST_FORMAT_VERSION: LatestFormatVersion = get_args(LatestFormatVersion)[0]


class Model(RdfBase):
    format_version: LatestFormatVersion = Field(
        LATEST_FORMAT_VERSION,
        description=f"""Version of the BioImage.IO model Resource Description File (RDF) specification used.
This is important for any consumer software to understand how to parse the fields.
The recommended behavior for the implementation is to keep backward compatibility and throw an error if the RDF content
has an unsupported format version. The current format version described here is {LATEST_FORMAT_VERSION}""",
    )
