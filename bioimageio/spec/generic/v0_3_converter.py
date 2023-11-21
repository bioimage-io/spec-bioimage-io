import collections.abc

from bioimageio.spec._internal.types import BioimageioYamlContent
from bioimageio.spec._internal.validation_context import InternalValidationContext
from bioimageio.spec.generic import v0_2_converter


def convert_from_older_format(data: BioimageioYamlContent, context: InternalValidationContext) -> None:
    """convert raw RDF data of an older format where possible"""
    # check if we have future format version
    fv = data.get("format_version", "0.2.0")
    if not isinstance(fv, str) or fv.count(".") != 2 or tuple(map(int, fv.split(".")[:2])) > (0, 3):
        return

    v0_2_converter.convert_from_older_format(data, context)

    convert_attachments(data)

    _ = data.pop("download_url", None)
    _ = data.pop("rdf_source", None)

    data["format_version"] = "0.3.0"


def convert_attachments(data: BioimageioYamlContent) -> None:
    a = data.get("attachments")
    if isinstance(a, collections.abc.Mapping):
        data["attachments"] = tuple({"source": file} for file in a.get("files", []))  # type: ignore