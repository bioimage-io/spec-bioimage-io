from __future__ import annotations

import warnings
from pathlib import Path
from typing import (
    Optional,
    Union,
)

from pydantic import (
    AnyUrl,
    PlainSerializer,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    WrapSerializer,
)
from typing_extensions import (
    Annotated,
    assert_never,
)

from .io import (
    FileDescr,
    FileSource,
    RelativeFilePath,
    extract_file_name,
    wo_special_file_name,
)
from .io_basics import (
    ALL_BIOIMAGEIO_YAML_NAMES,
    FileName,
    Sha256,
)
from .packaging_context import packaging_context_var
from .url import HttpUrl
from .validator_annotations import AfterValidator


def _package_serializer(
    source: FileSource, info: SerializationInfo
) -> Union[str, Path, FileName]:
    return _package(source, info, None)


def package_file_descr_serializer(
    value: FileDescr, handler: SerializerFunctionWrapHandler, info: SerializationInfo
):
    ret = handler(
        value,
        info,  # pyright: ignore[reportArgumentType]  # taken from pydantic docs
    )
    ret["source"] = _package(value.source, info, sha256=value.sha256)
    return ret


def _package(
    source: FileSource, info: SerializationInfo, sha256: Optional[Sha256]
) -> Union[str, Path, FileName]:
    if (packaging_context := packaging_context_var.get()) is None:
        # convert to standard python obj
        # note: pydantic keeps returning Rootmodels (here `HttpUrl`) as-is, but if
        #   this function returns one RootModel, paths are "further serialized" by
        #   returning the 'root' attribute, which is incorrect.
        #   see https://github.com/pydantic/pydantic/issues/8963
        #   TODO: follow up on https://github.com/pydantic/pydantic/issues/8963
        if isinstance(source, Path):
            unpackaged = source
        elif isinstance(source, HttpUrl):
            unpackaged = source
        elif isinstance(source, RelativeFilePath):
            unpackaged = Path(source.path)
        elif isinstance(source, AnyUrl):
            unpackaged = str(source)
        else:
            assert_never(source)

        if info.mode_is_json():
            # convert to json value  # TODO: remove and let pydantic do this?
            if isinstance(unpackaged, (Path, HttpUrl)):
                unpackaged = str(unpackaged)
            elif isinstance(unpackaged, str):
                pass
            else:
                assert_never(unpackaged)
        else:
            warnings.warn(
                "dumping with mode='python' is currently not fully supported for "
                + "fields that are included when packaging; returned objects are "
                + "standard python objects"
            )

        return unpackaged  # return unpackaged file source

    fname = extract_file_name(source)
    if fname == packaging_context.bioimageio_yaml_file_name:
        raise ValueError(
            f"Reserved file name '{packaging_context.bioimageio_yaml_file_name}' "
            + "not allowed for a file to be packaged"
        )

    fsrcs = packaging_context.file_sources
    assert not any(fname.endswith(special) for special in ALL_BIOIMAGEIO_YAML_NAMES), (
        fname
    )
    if fname in fsrcs and fsrcs[fname].source != source:
        for i in range(2, 20):
            fn, *ext = fname.split(".")
            alternative_file_name = ".".join([f"{fn}_{i}", *ext])
            if (
                alternative_file_name not in fsrcs
                or fsrcs[alternative_file_name].source == source
            ):
                fname = alternative_file_name
                break
        else:
            raise ValueError(f"Too many file name clashes for {fname}")

    fsrcs[fname] = FileDescr(source=source, sha256=sha256)
    return fname


include_in_package = PlainSerializer(_package_serializer, when_used="unless-none")
"""DEPRECATED serializer for `source` fields without corresponding `sha256` field."""

include_when_packaging = WrapSerializer(
    package_file_descr_serializer, when_used="unless-none"
)
"""Pydantic serializer that marks the annotated `FileDescr` to be included when packaging
(saving a bioimageio zip package)."""

FileSource_ = Annotated[
    FileSource,
    AfterValidator(wo_special_file_name),
    include_in_package,
]
"""A file source that is included when packaging the resource."""

FileDescr_ = Annotated[
    FileDescr, AfterValidator(wo_special_file_name), include_when_packaging
]
"""A `FileDescr` whose **source** is included when packaging the resource."""
