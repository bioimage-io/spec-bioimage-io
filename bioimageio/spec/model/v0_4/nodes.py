from pathlib import Path
from typing import Literal, get_args
from bioimageio.spec.rdf.v0_2.nodes import Author, _RdfBase, _RdfBaseWoSource
from bioimageio.spec.shared.fields import Field

LatestFormatVersion = Literal["0.4.9"]
FormatVersion = Literal[
    "0.4.0", "0.4.1", "0.4.2", "0.4.3", "0.4.4", "0.4.5", "0.4.6", "0.4.7", "0.4.8", LatestFormatVersion
]
WeightsFormat = Literal[
    "pytorch_state_dict", "torchscript", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"
]

LATEST_FORMAT_VERSION: LatestFormatVersion = get_args(LatestFormatVersion)[0]


class Model(_RdfBaseWoSource):
    """Specification of the fields used in a BioImage.IO-compliant RDF that describes AI models with pretrained weights.

    These fields are typically stored in a YAML file which we call a model resource description file (model RDF).
    Like any RDF, a model RDF can be downloaded from or uploaded to the bioimage.io website and is produced or consumed
    by BioImage.IO-compatible consumers (e.g. image analysis software or another website).
    """

    model_config = _RdfBaseWoSource.model_config | dict(
        title=f"BioImage.IO Model Resource Description File Specification {LATEST_FORMAT_VERSION}"
    )
    format_version: LatestFormatVersion = Field(
        LATEST_FORMAT_VERSION,
        description=f"""Version of the BioImage.IO model Resource Description File (RDF) specification used.
This is important for any consumer software to understand how to parse the fields.
The recommended behavior for the implementation is to keep backward compatibility and throw an error if the RDF content
has an unsupported format version. The current format version described here is {LATEST_FORMAT_VERSION}""",
    )
