import os
import pathlib
import tempfile
from typing import Generic, Optional


try:
    from typing import Literal, get_args, get_origin, Protocol
except ImportError:
    from typing_extensions import Literal, get_args, get_origin, Protocol  # type: ignore


try:
    from ruamel.yaml import YAML
except ImportError:
    yaml: Optional["YAML"] = None
else:
    yaml = YAML(typ="safe")


DOI_REGEX = r"^10[.][0-9]{4,9}\/[-._;()\/:A-Za-z0-9]+$"

BIOIMAGEIO_CACHE_PATH = pathlib.Path(
    os.getenv("BIOIMAGEIO_CACHE_PATH", pathlib.Path(tempfile.gettempdir()) / "bioimageio_cache")
)


def get_format_version_module(type_: str, format_version: str):
    assert "." in format_version
    import bioimageio.spec

    version_mod_name = "v" + "_".join(format_version.split(".")[:2])
    try:
        return getattr(getattr(bioimageio.spec, type_), version_mod_name)
    except AttributeError:
        raise ValueError(
            f"Invalid RDF format version {format_version} for RDF type {type_}. "
            f"Submodule bioimageio.spec.{type_}{version_mod_name} does not exist."
        )


def get_patched_format_version(type_: str, format_version: str):
    """return latest patched format version for given type and major/minor of format_version"""
    version_mod = get_format_version_module(type_, format_version)
    return version_mod.format_version


def get_latest_format_version_module(type_: str):
    import bioimageio.spec

    try:
        return getattr(bioimageio.spec, type_)
    except AttributeError:
        raise ValueError(f"Invalid RDF type {type_}")


def get_latest_format_version(type_: str):
    return get_latest_format_version_module(type_).format_version


def get_class_name_from_type(type_: str):
    if type_ == "rdf":
        return "RDF"
    else:
        return type_.title()


def get_args_flat(tp):
    flat_args = []
    for a in get_args(tp):
        orig = get_origin(a)
        if orig is Literal or orig is Generic:
            flat_args += list(get_args(a))
        else:
            flat_args.append(a)

    return tuple(flat_args)


def nested_default_dict_as_nested_dict(nested_dd):
    if isinstance(nested_dd, dict):
        return {key: (nested_default_dict_as_nested_dict(value)) for key, value in nested_dd.items()}
    elif isinstance(nested_dd, list):
        return [nested_default_dict_as_nested_dict(value) for value in nested_dd]
    else:
        return nested_dd
