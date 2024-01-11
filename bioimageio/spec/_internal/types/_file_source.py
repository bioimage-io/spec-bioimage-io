from __future__ import annotations

import pathlib
from pathlib import Path, PurePath, PurePosixPath
from typing import Any, Union
from urllib.parse import urlparse, urlsplit, urlunsplit

import pydantic
import requests
from annotated_types import Predicate
from pydantic import (
    AfterValidator,
    AnyUrl,
    DirectoryPath,
    FilePath,
    GetCoreSchemaHandler,
    ValidationInfo,
)
from pydantic_core import core_schema
from typing_extensions import Annotated

from bioimageio.spec._internal.field_warning import issue_warning
from bioimageio.spec._internal.validation_context import get_internal_validation_context


def validate_url_ok(url: pydantic.HttpUrl, info: ValidationInfo):
    context = get_internal_validation_context(info.context)
    if not context["perform_io_checks"]:
        return url

    response = requests.head(str(url))
    if response.status_code in (301, 308):
        issue_warning(
            "URL redirected ({status_code}): consider updating {value} with new location: {location}",
            value=url,
            val_context=context,
            msg_context={"status_code": response.status_code, "location": response.headers.get("location")},
        )
    elif response.status_code != 200:
        raise ValueError(f"{response.status_code}: {response.reason} {url}")

    return url


HttpUrl = Annotated[pydantic.HttpUrl, AfterValidator(validate_url_ok)]


class RelativePath:
    path: PurePosixPath

    def __init__(self, path: Union[str, Path, RelativePath]) -> None:
        super().__init__()
        if isinstance(path, RelativePath):
            self.path = path.path
        else:
            if not isinstance(path, Path):
                path = Path(path)

            if path.is_absolute():
                raise ValueError(f"{path} is an absolute path.")

            self.path = PurePosixPath(path.as_posix())

    @property
    def __members(self):
        return (self.path,)

    def __eq__(self, __value: object) -> bool:
        return type(__value) is type(self) and self.__members == __value.__members

    def __hash__(self) -> int:
        return hash(self.__members)

    def __str__(self) -> str:
        return self.path.as_posix()

    def __repr__(self) -> str:
        return f"RelativePath('{self.path.as_posix()}')"

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.union_schema(
                [
                    core_schema.is_instance_schema(cls),
                    core_schema.is_instance_schema(pathlib.Path),
                    core_schema.str_schema(),
                ]
            ),
            serialization=core_schema.to_string_ser_schema(),
        )

    def get_absolute(self, root: Union[DirectoryPath, HttpUrl]) -> Union[FilePath, HttpUrl]:
        if isinstance(root, pathlib.Path):
            return (root / self.path).absolute()

        parsed = urlsplit(str(root))
        path = list(parsed.path.strip("/").split("/"))
        rel_path = self.path.as_posix().strip("/")
        if (
            parsed.netloc == "zenodo.org"
            and parsed.path.startswith("/api/records/")
            and parsed.path.endswith("/content")
        ):
            path.insert(-2, rel_path)
        else:
            path.append(rel_path)

        return AnyUrl(urlunsplit((parsed.scheme, parsed.netloc, "/".join(path), parsed.query, parsed.fragment)))

    def _check_exists(self, root: Union[DirectoryPath, HttpUrl]) -> None:
        if isinstance((p := self.get_absolute(root)), pathlib.Path) and not p.exists():
            raise ValueError(f"{p} does not exist")

    @classmethod
    def _validate(cls, value: Union[pathlib.Path, str], info: ValidationInfo):
        if isinstance(value, str) and (value.startswith("https://") or value.startswith("http://")):
            raise ValueError(f"{value} looks like a URL, not a relative path")

        ret = cls(value)
        if ret.path.is_absolute():
            raise ValueError(f"{value} is an absolute path.")

        context = get_internal_validation_context(info.context)
        if context["perform_io_checks"]:
            ret._check_exists(context["root"])

        return ret


class RelativeFilePath(RelativePath):
    def _check_exists(self, root: Union[DirectoryPath, HttpUrl]) -> None:
        if isinstance((p := self.get_absolute(root)), pathlib.Path) and not p.is_file():
            raise ValueError(f"{p} does not point to an existing file")


class RelativeDirectory(RelativePath):
    def _check_exists(self, root: Union[DirectoryPath, HttpUrl]) -> None:
        if isinstance((p := self.get_absolute(root)), pathlib.Path) and not p.is_dir():
            raise ValueError(f"{p} does not point to an existing directory")


FileName = str
AbsoluteFilePath = Annotated[FilePath, Predicate(Path.is_absolute)]
FileSource = Union[HttpUrl, AbsoluteFilePath, RelativeFilePath]
PermissiveFileSource = Union[FileSource, str]
StrictFileSource = Union[HttpUrl, AbsoluteFilePath]


def extract_file_name(src: Union[HttpUrl, PurePath, RelativeFilePath]) -> str:
    if isinstance(src, RelativeFilePath):
        return src.path.name
    elif isinstance(src, PurePath):
        return src.name
    else:
        url = urlparse(str(src))
        if (
            url.scheme == "https"
            and url.hostname == "zenodo.org"
            and url.path.startswith("/api/records/")
            and url.path.endswith("/content")
        ):
            return url.path.split("/")[-2]
        else:
            return url.path.split("/")[-1]
