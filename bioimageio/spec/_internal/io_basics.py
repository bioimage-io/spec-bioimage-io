import hashlib
import os
from functools import partial
from pathlib import Path
from typing import Any, ClassVar, Optional, Protocol, Type, Union, runtime_checkable

import pydantic
import zipp  # pyright: ignore[reportMissingTypeStubs]
from annotated_types import Predicate
from pydantic import RootModel, StringConstraints
from typing_extensions import Annotated

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
        reader: Union[BytesReaderP, BytesReaderIntoP],
        sha256: Optional[Sha256],
        suffix: Suffix,
        original_file_name: FileName,
    ) -> None:
        self._reader = reader
        self._sha256 = sha256
        self._suffix = suffix
        self._original_file_name = original_file_name
        super().__init__()

    @property
    def sha256(self) -> Sha256:
        if self._sha256 is None:
            self._sha256 = get_sha256(self._reader)

        return self._sha256

    @property
    def suffix(self) -> Suffix:
        return self._suffix

    @property
    def original_file_name(self) -> Optional[FileName]:
        return self._original_file_name

    def read(self, size: int = -1, /) -> bytes:
        return self._reader.read(size)

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


def get_sha256(reader: Union[BytesReaderP, BytesReaderIntoP]) -> Sha256:
    chunksize = 128 * 1024
    h = hashlib.sha256()
    if isinstance(reader, BytesReaderIntoP):
        b = bytearray(chunksize)
        mv = memoryview(b)
        for n in iter(lambda: reader.readinto(mv), 0):
            h.update(mv[:n])
    else:
        for chunk in iter(partial(reader.read, chunksize), b""):
            h.update(chunk)

    sha = h.hexdigest()
    return Sha256(sha)
