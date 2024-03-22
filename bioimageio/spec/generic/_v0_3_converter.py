import collections.abc
import string
from pathlib import Path

import imageio
from loguru import logger

from .._internal.io import (
    BioimageioYamlContent,
    extract_file_name,
    interprete_file_source,
)
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
    convert_cover_images(data)

    _ = data.pop("download_url", None)
    _ = data.pop("rdf_source", None)

    if "name" in data and isinstance(data["name"], str):
        data["name"] = "".join(
            c if c in string.ascii_letters + string.digits + "_- ()" else " "
            for c in data["name"]
        )[:128]

    data["format_version"] = "0.3.0"


def convert_attachments(data: BioimageioYamlContent) -> None:
    a = data.get("attachments")
    if isinstance(a, collections.abc.Mapping):
        data["attachments"] = tuple({"source": file} for file in a.get("files", []))  # type: ignore


def convert_cover_images(data: BioimageioYamlContent) -> None:
    covers = data.get("covers")
    if not isinstance(covers, list):
        return

    for i in range(len(covers)):
        c = covers[i]
        if not isinstance(c, str):
            continue

        src = interprete_file_source(c)
        fname = extract_file_name(src)

        if not (fname.endswith(".tif") or fname.endswith(".tiff")):
            continue

        try:
            image = imageio.imread(c)
            c_path = (Path(".bioimageio_converter_cache") / fname).with_suffix(".png")
            imageio.imwrite(c_path, image)
            covers[i] = str(c_path.absolute())
        except Exception as e:
            logger.warning("failed to convert tif cover image: {}", e)
