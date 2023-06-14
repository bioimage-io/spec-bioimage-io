from typing import Any, Literal, get_args
from bioimageio.spec.general.v0_2 import ResourceDescriptionBaseNoSource
from bioimageio.spec.shared.fields import Field
from bioimageio.spec.shared.types_ import RawMapping

LatestFormatVersion = Literal["0.4.9"]
FormatVersion = Literal[
    "0.4.0", "0.4.1", "0.4.2", "0.4.3", "0.4.4", "0.4.5", "0.4.6", "0.4.7", "0.4.8", LatestFormatVersion
]
WeightsFormat = Literal[
    "pytorch_state_dict", "torchscript", "keras_hdf5", "tensorflow_js", "tensorflow_saved_model_bundle", "onnx"
]

LATEST_FORMAT_VERSION: LatestFormatVersion = get_args(LatestFormatVersion)[0]


class Model(ResourceDescriptionBaseNoSource):
    """Specification of the fields used in a bioimage.io-compliant RDF that describes AI models with pretrained weights.

    These fields are typically stored in a YAML file which we call a model resource description file (model RDF).
    Like any RDF, a model RDF can be downloaded from or uploaded to the bioimage.io website and is produced or consumed
    by bioimage.io-compatible consumers (e.g. image analysis software or another website).
    """

    model_config = {
        **ResourceDescriptionBaseNoSource.model_config,
        **dict(title=f"bioimage.io Model Resource Description File Specification {LATEST_FORMAT_VERSION}"),
    }
    """pydantic model_config"""

    format_version: LatestFormatVersion = LATEST_FORMAT_VERSION
    """Version of the bioimage.io model Resource Description File (RDF) specification used.
    This is important for any consumer software to understand how to parse the fields.
    The recommended behavior for the implementation is to keep backward compatibility and throw an error if the RDF
    content has an unsupported format version.
    """

    @staticmethod
    def convert_model_from_v0_4_0_to_0_4_1(data: dict[str, Any]):
        # move dependencies from root to pytorch_state_dict weights entry
        deps = data.pop("dependencies", None)
        weights = data.get("weights", {})
        if deps and weights and isinstance(weights, dict):
            entry = weights.get("pytorch_state_dict")
            if entry and isinstance(entry, dict):
                entry["dependencies"] = deps

        data["format_version"] = "0.4.1"

    @staticmethod
    def convert_model_from_v0_4_4_to_0_4_5(data: dict[str, Any]) -> None:
        parent = data.pop("parent", None)
        if parent and "uri" in parent:
            data["parent"] = parent["uri"]

        data["format_version"] = "0.4.5"

    @classmethod
    def convert_from_older_format(cls, data: RawMapping) -> RawMapping:
        data = dict(data)
        fv = data.get("format_version", "0.3.0")
        if isinstance(fv, str):
            major_minor = tuple(map(int, fv.split(".")[:2]))
            if major_minor < (0, 4):
                raise NotImplementedError("model RDF conversion for format_version < 0.4 no longer supported.")
            elif major_minor > (0, 4):
                return data

        if data["format_version"] == "0.4.0":
            cls.convert_model_from_v0_4_0_to_0_4_1(data)

        if data["format_version"] in ("0.4.1", "0.4.2", "0.4.3", "0.4.4"):
            cls.convert_model_from_v0_4_4_to_0_4_5(data)

        if data["format_version"] in ("0.4.5", "0.4.6"):
            cls._remove_slashes_from_names(data)
            data["format_version"] = "0.4.7"

        if data["format_version"] in ("0.4.7", "0.4.8"):
            data["format_version"] = "0.4.9"

        # remove 'future' from config if no other than the used future entries exist
        config = data.get("config", {})
        if isinstance(config, dict) and config.get("future") == {}:
            del config["future"]

        # remove 'config' if now empty
        if data.get("config") == {}:
            del data["config"]

        return data
