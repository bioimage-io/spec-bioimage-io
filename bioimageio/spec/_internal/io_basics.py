import hashlib
import os
import zipfile
from contextlib import nullcontext
from functools import partial
from pathlib import Path
from typing import Any, ClassVar, Optional, Protocol, Type, Union, runtime_checkable
from zipfile import ZipFile

import pydantic
import zipp  # pyright: ignore[reportMissingTypeStubs]
from annotated_types import Predicate
from pydantic import RootModel, StringConstraints
from typing_extensions import Annotated

from .root_url import RootHttpUrl
from .validated_string import ValidatedString

FileName = str
FilePath = Annotated[pydantic.FilePath, pydantic.Field(title="FilePath")]
AbsoluteDirectory = Annotated[
    pydantic.DirectoryPath,
    Predicate(Path.is_absolute),
    pydantic.Field(title="AbsoluteDirectory"),
]
AbsoluteFilePath = Annotated[
    pydantic.FilePath,
    Predicate(Path.is_absolute),
    pydantic.Field(title="AbsoluteFilePath"),
]

BIOIMAGEIO_YAML = "rdf.yaml"
ALTERNATIVE_BIOIMAGEIO_YAML_NAMES = ("bioimageio.yaml", "model.yaml")
ALL_BIOIMAGEIO_YAML_NAMES = (BIOIMAGEIO_YAML,) + ALTERNATIVE_BIOIMAGEIO_YAML_NAMES

ZipPath = zipp.Path  # not zipfile.Path due to https://bugs.python.org/issue40564


class Sha256(ValidatedString):
    """A SHA-256 hash value"""

    root_model: ClassVar[Type[RootModel[Any]]] = RootModel[
        Annotated[
            str,
            StringConstraints(
                strip_whitespace=True, to_lower=True, min_length=64, max_length=64
            ),
        ]
    ]


class BytesReaderP(Protocol):
    def read(self, size: int = -1, /) -> bytes: ...

    @property
    def closed(self) -> bool: ...

    def readable(self) -> bool: ...

    def seek(self, offset: int, whence: int = os.SEEK_SET, /) -> int: ...

    def seekable(self) -> bool: ...

    def tell(self) -> int: ...


@runtime_checkable
class BytesReaderIntoP(BytesReaderP, Protocol):
    def readinto(self, b: Union[bytearray, memoryview]) -> int: ...


Suffix = str


class BytesReader(BytesReaderP):
    def __init__(
        self,
        /,
        reader: Union[BytesReaderP, BytesReaderIntoP],
        *,
        sha256: Optional[Sha256],
        suffix: Suffix,
        original_file_name: FileName,
        original_root: Union[RootHttpUrl, AbsoluteDirectory, ZipFile],
        is_zipfile: Optional[bool],
    ) -> None:
        self._reader = reader
        self._sha256 = sha256
        self._suffix = suffix
        self._original_file_name = original_file_name
        self._original_root = original_root
        self._is_zipfile = is_zipfile
        super().__init__()

    @property
    def is_zipfile(self) -> bool:
        if self._is_zipfile is None:
            pos = self.tell()
            self._is_zipfile = zipfile.is_zipfile(self)
            _ = self.seek(pos)

        return self._is_zipfile

    @property
    def sha256(self) -> Sha256:
        if self._sha256 is None:
            pos = self._reader.tell()
            _ = self._reader.seek(0)
            self._sha256 = get_sha256(self._reader)
            _ = self._reader.seek(pos)

        return self._sha256

    @property
    def suffix(self) -> Suffix:
        return self._suffix

    @property
    def original_file_name(self) -> FileName:
        return self._original_file_name

    @property
    def original_root(self) -> Union[RootHttpUrl, AbsoluteDirectory, ZipFile]:
        return self._original_root

    def read(self, size: int = -1, /) -> bytes:
        return self._reader.read(size)

    def read_text(self, encoding: str = "utf-8") -> str:
        return self._reader.read().decode(encoding)

    def readable(self) -> bool:
        return True

    def seek(self, offset: int, whence: int = os.SEEK_SET, /) -> int:
        return self._reader.seek(offset, whence)

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self._reader.tell()

    @property
    def closed(self) -> bool:
        return self._reader.closed


def get_sha256(source: Union[BytesReaderP, BytesReaderIntoP, Path]) -> Sha256:
    chunksize = 128 * 1024
    h = hashlib.sha256()

    if isinstance(source, BytesReaderIntoP):
        b = bytearray(chunksize)
        mv = memoryview(b)
        for n in iter(lambda: source.readinto(mv), 0):
            h.update(mv[:n])
    else:
        if isinstance(source, Path):
            read_ctxt = source.open(mode="rb")
        else:
            read_ctxt = nullcontext(source)

        with read_ctxt as r:
            for chunk in iter(partial(r.read, chunksize), b""):
                h.update(chunk)

    sha = h.hexdigest()
    return Sha256(sha)
