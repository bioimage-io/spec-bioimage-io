import dataclasses
import os
import pathlib
import re
import tempfile
import warnings
from collections import UserDict
from typing import Any, Dict, Generic, Optional


try:
    from typing import Literal, get_args, get_origin, Protocol
except ImportError:
    from typing_extensions import Literal, get_args, get_origin, Protocol  # type: ignore

import yaml as _yaml


class PyYAML:
    """ruamel.yaml.YAML replacement. This uses PyYAML's yaml 1.1 implementation with some manually added yaml 1.2 'fixes'"""

    def __init__(self, typ="safe"):
        if typ != "safe":
            raise NotImplementedError(typ)

        # floating point 'fix' for yaml 1.1 from https://stackoverflow.com/a/30462009
        self.loader = _yaml.SafeLoader
        self.loader.add_implicit_resolver(
            "tag:yaml.org,2002:float",
            re.compile(
                """^(?:
             [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
            |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
            |\\.[0-9_]+(?:[eE][-+][0-9]+)?
            |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
            |[-+]?\\.(?:inf|Inf|INF)
            |\\.(?:nan|NaN|NAN))$""",
                re.X,
            ),
            list("-+0123456789."),
        )

    def load(self, stream):
        if isinstance(stream, os.PathLike):
            with pathlib.Path(stream).open() as f:
                return _yaml.load(f, Loader=self.loader)
        else:
            return _yaml.load(stream, Loader=self.loader)

    @staticmethod
    def dump(data, stream):
        if isinstance(stream, os.PathLike):
            with pathlib.Path(stream).open("w") as f:
                return _yaml.dump(data, f)
        else:
            return _yaml.dump(data, stream)


pyyaml_yaml = PyYAML()

try:
    from ruamel.yaml import YAML
except ImportError:
    ruamel_yaml: Optional["YAML"] = None
    yaml = pyyaml_yaml
else:
    ruamel_yaml = YAML(typ="safe")
    yaml = ruamel_yaml


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


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class NoOverridesDict(UserDict):
    def __init__(self, *args, key_exists_error_msg: Optional[str] = None, allow_if_same_value: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_exists_error_message = (
            "key {key} already exists!" if key_exists_error_msg is None else key_exists_error_msg
        )
        self.allow_if_same_value = allow_if_same_value

    def __setitem__(self, key, value):
        if key in self and (not self.allow_if_same_value or value != self[key]):
            raise ValueError(self.key_exists_error_message.format(key=key, value=value))

        super().__setitem__(key, value)


@dataclasses.dataclass
class DataClassFilterUnknownKwargsMixin:
    @classmethod
    def get_known_kwargs(cls, kwargs: Dict[str, Any]):
        field_names = set(f.name for f in dataclasses.fields(cls))
        known_kwargs = {k: v for k, v in kwargs.items() if k in field_names}
        unknown_kwargs = {k: v for k, v in kwargs.items() if k not in field_names}
        warnings.warn(f"discarding unknown kwargs: {unknown_kwargs}")
        return known_kwargs


def nested_default_dict_as_nested_dict(nested_dd):
    return {
        key: (nested_default_dict_as_nested_dict(value) if isinstance(value, dict) else value)
        for key, value in nested_dd.items()
    }
