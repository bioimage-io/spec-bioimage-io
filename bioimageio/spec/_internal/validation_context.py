from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urlsplit, urlunsplit
from zipfile import ZipFile

from pydantic import DirectoryPath

from ._settings import settings
from .io_basics import AbsoluteDirectory, FileName, Sha256
from .root_url import RootHttpUrl
from .warning_levels import WarningLevel


@dataclass(frozen=True)
class ValidationContext:
    _context_tokens: "List[Token[ValidationContext]]" = field(
        init=False, default_factory=list
    )

    root: Union[RootHttpUrl, AbsoluteDirectory, ZipFile] = Path()
    """url/directory serving as base to resolve any relative file paths"""

    warning_level: WarningLevel = 50
    """raise warnings of severity `s` as validation errors if `s >= warning_level`"""

    log_warnings: bool = settings.log_warnings
    """if `True` log warnings that are not raised to the console"""

    file_name: Optional[FileName] = None
    """file name of the bioimageio Yaml file"""

    perform_io_checks: bool = settings.perform_io_checks
    """wether or not to perform validation that requires file io,
    e.g. downloading a remote files.

    Existence of local absolute file paths is still being checked."""

    known_files: Dict[str, Sha256] = field(default_factory=dict)
    """allows to bypass download and hashing of referenced files"""

    def replace(
        self,
        root: Optional[Union[RootHttpUrl, DirectoryPath, ZipFile]] = None,
        warning_level: Optional[WarningLevel] = None,
        log_warnings: Optional[bool] = None,
        file_name: Optional[str] = None,
        perform_io_checks: Optional[bool] = None,
        known_files: Optional[Dict[str, Sha256]] = None,
    ) -> "ValidationContext":
        if known_files is None and root is not None and self.root != root:
            # reset known files if root changes, but no new known_files are given
            known_files = {}

        return ValidationContext(
            root=self.root if root is None else root,
            warning_level=(
                self.warning_level if warning_level is None else warning_level
            ),
            log_warnings=self.log_warnings if log_warnings is None else log_warnings,
            file_name=self.file_name if file_name is None else file_name,
            perform_io_checks=(
                self.perform_io_checks
                if perform_io_checks is None
                else perform_io_checks
            ),
            known_files=self.known_files if known_files is None else known_files,
        )

    def __enter__(self):
        self._context_tokens.append(validation_context_var.set(self))
        return self

    def __exit__(self, type, value, traceback):  # type: ignore
        validation_context_var.reset(self._context_tokens.pop(-1))

    @property
    def source_name(self) -> str:
        if self.file_name is None:
            return "in-memory"
        else:
            try:
                if isinstance(self.root, Path):
                    source = (self.root / self.file_name).absolute()
                else:
                    parsed = urlsplit(str(self.root))
                    path = list(parsed.path.strip("/").split("/")) + [self.file_name]
                    source = urlunsplit(
                        (
                            parsed.scheme,
                            parsed.netloc,
                            "/".join(path),
                            parsed.query,
                            parsed.fragment,
                        )
                    )
            except ValueError:
                return self.file_name
            else:
                return str(source)


validation_context_var: ContextVar[ValidationContext] = ContextVar(
    "validation_context_var", default=ValidationContext()
)
