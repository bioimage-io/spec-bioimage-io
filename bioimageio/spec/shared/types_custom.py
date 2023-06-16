"""types that cannot be used directly in pydantic schemas
use their equivalent from bioimageio.spec.shared.types_annotated instead
"""
from __future__ import annotations
import pathlib
from typing import Any, TypeVar, Union
from urllib.parse import urljoin

from pydantic import AnyUrl, GetCoreSchemaHandler, PydanticUserError, ValidationInfo
from pydantic_core import core_schema

T = TypeVar("T")


class RelativePath:
    """A path relative to root; root may be a (relative or absolute) path or a URL."""

    _relative: pathlib.PurePosixPath
    _root: Union[AnyUrl, pathlib.Path]
    _absolute: Union[AnyUrl, pathlib.Path]

    def __init__(
        self, path: Union[str, pathlib.Path, RelativePath], /, *, root: Union[AnyUrl, pathlib.Path] = pathlib.Path()
    ) -> None:
        self._relative = path._relative if isinstance(path, RelativePath) else pathlib.PurePosixPath(path)
        self._root = root
        self._check_exists()

    def __str__(self) -> str:
        return str(self._relative)

    def __repr__(self) -> str:
        return f"RelativePath({self._relative}, root={self._root}"

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

    @property
    def relative(self):
        return self._relative

    # @relative.setter
    # def relative(self, value: Union[pathlib.PurePath, str]):
    #     p = pathlib.PurePosixPath(value)
    #     if p.is_absolute():
    #         raise ValueError(f"{p} is absolute, expected a relative path")

    #     self._relative = p
    #     self._check_exists()

    @property
    def root(self):
        return self._root

    # @root.setter
    # def root(self, value: Union[pathlib.Path, AnyUrl]):
    #     assert isinstance(value, (pathlib.Path, AnyUrl))
    #     self._root = value
    #     self._check_exists()

    @property
    def absolute(self):
        if isinstance(self._root, pathlib.Path):
            return self._root / self._relative
        else:
            return AnyUrl(urljoin(str(self._root), str(self._relative)))

    def _check_exists(self) -> None:
        if isinstance((p := self.absolute), pathlib.Path) and not p.exists():
            raise ValueError(f"{p} does not exist")

    @classmethod
    def _validate(cls, value: Union[pathlib.Path, str], info: ValidationInfo):
        if "root" not in info.context:
            raise PydanticUserError("missing 'root' context for {klass}", code=None)

        root = info.context["root"]
        if not isinstance(root, (AnyUrl, pathlib.Path)):
            raise ValueError(
                "{klass} expected root context to be of type 'pathlib.Path' or 'pydantic.AnyUrl', "
                f"but got {root} of type '{type(root)}'"
            )

        return cls(value, root=root)


class RelativeFilePath(RelativePath):
    def _check_exists(self) -> None:
        if isinstance((p := self.absolute), pathlib.Path) and not p.is_file():
            raise ValueError(f"{p} does not point to an existing file")


class RelativeDirectory(RelativePath):
    def _check_exists(self) -> None:
        if isinstance((p := self.absolute), pathlib.Path) and not p.is_dir():
            raise ValueError(f"{p} does not point to an existing directory")
