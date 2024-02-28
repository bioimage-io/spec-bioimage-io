from __future__ import annotations

import pathlib
from functools import partial
from pathlib import Path, PurePath, PurePosixPath
from typing import Any, Callable, Union
from urllib.parse import urlparse, urlsplit, urlunsplit

import pydantic
import requests.exceptions
from annotated_types import Predicate
from pydantic import (
    AfterValidator,
    AnyUrl,
    DirectoryPath,
    FilePath,
    GetCoreSchemaHandler,
    SerializerFunctionWrapHandler,
    TypeAdapter,
    WrapSerializer,
)
from pydantic_core import core_schema
from typing_extensions import Annotated, assert_never

from bioimageio.spec._internal.constants import (
    ALL_BIOIMAGEIO_YAML_NAMES,
    BIOIMAGEIO_YAML,
)
from bioimageio.spec._internal.field_warning import issue_warning
from bioimageio.spec._internal.packaging_context import packaging_context_var
from bioimageio.spec._internal.validation_context import validation_context_var


def validate_url_ok(url: str):
    if not validation_context_var.get().perform_io_checks:
        return url

    if url.startswith("https://colab.research.google.com/github/"):
        # head request for colab returns "Value error, 405: Method Not Allowed"
        # therefore we check if the source notebook exists at github instead
        val_url = url.replace(
            "https://colab.research.google.com/github/", "https://github.com/"
        )
    else:
        val_url = url

    try:
        response = requests.head(val_url)
    except (
        requests.exceptions.ChunkedEncodingError,
        requests.exceptions.ContentDecodingError,
        requests.exceptions.InvalidHeader,
        requests.exceptions.InvalidJSONError,
        requests.exceptions.InvalidSchema,
        requests.exceptions.InvalidURL,
        requests.exceptions.MissingSchema,
        requests.exceptions.StreamConsumedError,
        requests.exceptions.TooManyRedirects,
        requests.exceptions.UnrewindableBodyError,
        requests.exceptions.URLRequired,
    ) as e:
        raise ValueError(
            f"Invalid URL '{url}': {e}\nrequest: {e.request}\nresponse: {e.response}"
        )
    except requests.RequestException as e:
        issue_warning(
            "Failed to validate URL '{value}': {error}\nrequest: {request}\nresponse: {response}",
            value=url,
            msg_context={"error": str(e), "response": e.response, "request": e.request},
        )
    except Exception as e:
        issue_warning(
            "Failed to validate URL '{value}': {error}",
            value=url,
            msg_context={"error": str(e)},
        )
    else:
        if response.status_code == 302:  # found
            pass
        elif response.status_code in (301, 308):
            issue_warning(
                "URL redirected ({status_code}): consider updating {value} with new"
                " location: {location}",
                value=url,
                msg_context={
                    "status_code": response.status_code,
                    "location": response.headers.get("location"),
                },
            )
        elif response.status_code == 405:
            issue_warning(
                "{status_code}: {reason} {value}",
                value=url,
                msg_context={
                    "status_code": response.status_code,
                    "reason": response.reason,
                },
            )
        elif response.status_code != 200:
            raise ValueError(f"{response.status_code}: {response.reason} {url}")

    return url


_http_url_adapter = TypeAdapter(pydantic.HttpUrl)  # pyright: ignore[reportCallIssue]

HttpUrl = Annotated[
    str,
    AfterValidator(lambda value: str(_http_url_adapter.validate_python(value))),
    AfterValidator(validate_url_ok),
]
FileName = str
AbsoluteDirectory = Annotated[DirectoryPath, Predicate(Path.is_absolute)]
AbsoluteFilePath = Annotated[FilePath, Predicate(Path.is_absolute)]


class RelativePath:
    path: PurePosixPath
    absolute: Union[HttpUrl, AbsoluteDirectory, AbsoluteFilePath]
    """the absolute path (resolved at time of initialization with the root of the ValidationContext)"""

    def __init__(self, path: Union[str, Path, RelativePath]) -> None:
        super().__init__()
        if isinstance(path, RelativePath):
            self.path = path.path
            self.absolute = path.absolute
        else:
            if not isinstance(path, Path):
                path = Path(path)

            if path.is_absolute():
                raise ValueError(f"{path} is an absolute path")

            self.path = PurePosixPath(path.as_posix())
            self.absolute = self.get_absolute(validation_context_var.get().root)

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
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
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

    def get_absolute(
        self, root: Union[DirectoryPath, HttpUrl, pydantic.HttpUrl]
    ) -> Union[AbsoluteFilePath, HttpUrl]:
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
            path.insert(-1, rel_path)
        else:
            path.append(rel_path)

        return urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                "/".join(path),
                parsed.query,
                parsed.fragment,
            )
        )

    def exists(self) -> bool:
        try:
            self._exists_impl()
        except Exception:
            return False
        else:
            return True

    @staticmethod
    def _exists_locally(path: pathlib.Path):
        if not path.exists():
            raise ValueError(f"{path} not found")

    def _exists_impl(self) -> None:
        if isinstance(self.absolute, pathlib.Path):
            self._exists_locally(self.absolute)
        elif isinstance(self.absolute, str):
            _ = validate_url_ok(self.absolute)
        else:
            assert_never(self.absolute)

    @classmethod
    def _validate(cls, value: Union[pathlib.Path, str]):
        if isinstance(value, str) and (
            value.startswith("https://") or value.startswith("http://")
        ):
            raise ValueError(f"{value} looks like a URL, not a relative path")

        ret = cls(value)
        if ret.path.is_absolute():
            raise ValueError(f"{value} is an absolute path.")

        context = validation_context_var.get()
        if context.perform_io_checks:
            ret._exists_impl()

        return ret


class RelativeFilePath(RelativePath):
    absolute: Union[HttpUrl, AbsoluteFilePath]
    """the absolute file path (resolved at time of initialization with the root of the ValidationContext)"""

    @staticmethod
    def _exists_localy(path: pathlib.Path) -> None:
        if not path.is_file():
            raise ValueError(f"{path} does not point to an existing file")


class RelativeDirectory(RelativePath):
    absolute: Union[HttpUrl, AbsoluteDirectory]
    """the absolute directory (resolved at time of initialization with the root of the ValidationContext)"""

    @staticmethod
    def _exists_locally(path: pathlib.Path) -> None:
        if not path.is_dir():
            raise ValueError(f"{path} does not point to an existing directory")


FileSource = Union[HttpUrl, AbsoluteFilePath, RelativeFilePath, pydantic.HttpUrl]
PermissiveFileSource = Union[FileSource, str]


def is_valid_rdf_name(src: FileSource) -> bool:
    file_name = extract_file_name(src)
    for special in ALL_BIOIMAGEIO_YAML_NAMES:
        if file_name.endswith(special):
            return True

    return False


def ensure_is_valid_rdf_name(src: FileSource) -> FileSource:
    if not is_valid_rdf_name(src):
        raise ValueError(
            f"'{src}' does not have a valid filename to identify"
            f" '{BIOIMAGEIO_YAML}' (or equivalent) files."
        )

    return src


def wo_special_file_name(src: FileSource) -> FileSource:
    if is_valid_rdf_name(src):
        raise ValueError(
            f"'{src}' not allowed here as its filename is reserved to identify"
            f" '{BIOIMAGEIO_YAML}' (or equivalent) files."
        )

    return src


def _package(
    value: FileSource, handler: SerializerFunctionWrapHandler
) -> Union[FileSource, FileName]:
    ret = handler(value)

    if (packaging_context := packaging_context_var.get()) is None:
        return ret

    fsrcs = packaging_context.file_sources

    if isinstance(value, RelativeFilePath):
        src = value.absolute
    elif isinstance(value, (str, AnyUrl)):
        src = str(value)
    elif isinstance(value, Path):
        src = value.resolve()
    else:
        assert_never(value)

    fname = extract_file_name(src)
    assert not any(
        fname.endswith(special) for special in ALL_BIOIMAGEIO_YAML_NAMES
    ), fname
    if fname in fsrcs and fsrcs[fname] != src:
        for i in range(2, 20):
            fn, *ext = fname.split(".")
            alternative_file_name = ".".join([f"{fn}_{i}", *ext])
            if (
                alternative_file_name not in fsrcs
                or fsrcs[alternative_file_name] == src
            ):
                fname = alternative_file_name
                break
        else:
            raise RuntimeError(f"Too many file name clashes for {fname}")

    fsrcs[fname] = src
    return fname


IncludeInPackage: Callable[[], WrapSerializer] = partial(
    WrapSerializer, _package, when_used="unless-none"
)
ImportantFileSource = Annotated[
    FileSource, AfterValidator(wo_special_file_name), IncludeInPackage()
]


def extract_file_name(
    src: Union[pydantic.HttpUrl, HttpUrl, PurePath, RelativeFilePath],
) -> str:
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
