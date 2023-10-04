from __future__ import annotations

import pathlib
from pathlib import Path, PurePosixPath
from typing import Any, Union
from urllib.parse import urljoin

from pydantic import AnyUrl, DirectoryPath, FilePath, GetCoreSchemaHandler, HttpUrl, ValidationInfo
from pydantic_core import core_schema


class RelativePath:
    path: PurePosixPath

    def __init__(self, path: Union[str, Path, RelativePath]) -> None:
        super().__init__()
        self.path = (
            path.path
            if isinstance(path, RelativePath)
            else PurePosixPath(path.as_posix())
            if isinstance(path, Path)
            else PurePosixPath(Path(path).as_posix())
        )

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
        return core_schema.general_after_validator_function(
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

    def get_absolute(self, root: Union[DirectoryPath, AnyUrl]) -> Union[FilePath, AnyUrl]:
        if isinstance(root, pathlib.Path):
            return root / self.path
        else:
            return AnyUrl(urljoin(str(root), str(self.path)))

    def _check_exists(self, root: Union[DirectoryPath, AnyUrl]) -> None:
        if isinstance((p := self.get_absolute(root)), pathlib.Path) and not p.exists():
            raise ValueError(f"{p} does not exist")

    @classmethod
    def _validate(cls, value: Union[pathlib.Path, str], info: ValidationInfo):
        if isinstance(value, str) and (value.startswith("https://") or value.startswith("http://")):
            raise ValueError(f"{value} looks like a URL, not a relative path")

        ret = cls(value)
        root = (info.context or {}).get("root")
        if root is not None:
            ret._check_exists(root)

        return ret


class RelativeFilePath(RelativePath):
    def _check_exists(self, root: Union[DirectoryPath, AnyUrl]) -> None:
        if isinstance((p := self.get_absolute(root)), pathlib.Path) and not p.is_file():
            raise ValueError(f"{p} does not point to an existing file")


class RelativeDirectory(RelativePath):
    def _check_exists(self, root: Union[DirectoryPath, AnyUrl]) -> None:
        if isinstance((p := self.get_absolute(root)), pathlib.Path) and not p.is_dir():
            raise ValueError(f"{p} does not point to an existing directory")


FileSource = Union[HttpUrl, RelativeFilePath]
