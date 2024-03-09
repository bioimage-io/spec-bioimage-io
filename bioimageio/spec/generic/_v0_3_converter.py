import collections.abc

from .._internal.io import BioimageioYamlContent
from ._v0_2_converter import convert_from_older_format as convert_from_older_format_v0_2


def convert_from_older_format(data: BioimageioYamlContent) -> None:
    """convert raw RDF data of an older format where possible"""
    # check if we have future format version
    fv = data.get("format_version", "0.2.0")
    if (
        not isinstance(fv, str)
        or fv.count(".") != 2
        or tuple(map(int, fv.split(".")[:2])) > (0, 3)
    ):
        return

    convert_from_older_format_v0_2(data)

    convert_attachments(data)

    _ = data.pop("download_url", None)
    _ = data.pop("rdf_source", None)

    data["format_version"] = "0.3.0"


def convert_attachments(data: BioimageioYamlContent) -> None:
    a = data.get("attachments")
    if isinstance(a, collections.abc.Mapping):
        data["attachments"] = tuple({"source": file} for file in a.get("files", []))  # type: ignore
