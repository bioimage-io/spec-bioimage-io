import collections.abc
import string
from pathlib import Path

import imageio
from loguru import logger
from packaging.version import Version

from .._internal.io import (
    BioimageioYamlContent,
    extract_file_name,
    interprete_file_source,
)
from .._internal.type_guards import is_list
from ._v0_2_converter import convert_from_older_format as convert_from_older_format_v0_2


def convert_from_older_format(data: BioimageioYamlContent) -> None:
    """convert raw RDF data of an older format where possible"""
    # check if we have future format version
    fv_raw = data.get("format_version", "0.2.0")
    if fv_raw is None or not isinstance(fv_raw, str):
        fv = None
    else:
        try:
            fv = Version(fv_raw)
        except Exception:
            fv = None

    if fv is None:
        return

    if fv < Version("0.3"):
        convert_from_older_format_v0_2(data)

        convert_attachments(data)
        convert_cover_images(data)

        _ = data.pop("download_url", None)
        _ = data.pop("rdf_source", None)

        if "name" in data and isinstance(data["name"], str):
            data["name"] = "".join(
                c if c in string.ascii_letters + string.digits + "_+- ()" else " "
                for c in data["name"]
            )[:128]

    if fv < Version("0.3.4"):
        convert_plain_covers_and_docs_and_icon(data)

    data["format_version"] = "0.3.4"


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

        if not fname.endswith((".tif", ".tiff")):
            continue

        try:
            image = imageio.imread(c)
            c_path = (Path(".bioimageio_converter_cache") / fname).with_suffix(".png")
            imageio.imwrite(c_path, image)
            covers[i] = str(c_path.absolute())
        except Exception as e:
            logger.warning("failed to convert tif cover image: {}", e)


def convert_plain_covers_and_docs_and_icon(data: BioimageioYamlContent) -> None:
    doc = data.get("documentation")
    if isinstance(doc, str):
        data["documentation"] = {"source": doc}

    covers = data.get("covers")
    if is_list(covers):
        for i in range(len(covers)):
            c = covers[i]
            if isinstance(c, str):
                covers[i] = {"source": c}

    icon = data.get("icon")
    if isinstance(icon, str) and len(icon) > 2:
        data["icon"] = {"source": icon}
