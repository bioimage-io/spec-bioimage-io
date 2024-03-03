from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Union

from pydantic import DirectoryPath

from bioimageio.spec._internal import settings
from bioimageio.spec._internal.io_basics import (
    BIOIMAGEIO_YAML,
    AbsoluteDirectory,
)
from bioimageio.spec._internal.root_url import RootHttpUrl
from bioimageio.spec._internal.warning_levels import WarningLevel


@dataclass(frozen=True)
class ValidationContext:
    _context_tokens: "List[Token[ValidationContext]]" = field(
        init=False, default_factory=list
    )

    root: Union[RootHttpUrl, AbsoluteDirectory] = Path()
    """url/directory serving as base to resolve any relative file paths"""

    warning_level: WarningLevel = 50
    """raise warnings of severity s as validation errors if s >= `warning_level`"""

    file_name: str = BIOIMAGEIO_YAML
    """file name of the bioimageio Yaml file"""

    perform_io_checks: bool = settings.perform_io_checks
    """wether or not to perfrom validation that requires IO operations like downloading
    or reading a file from disk"""

    def replace(
        self,
        root: Optional[Union[RootHttpUrl, DirectoryPath]] = None,
        warning_level: Optional[WarningLevel] = None,
        file_name: Optional[str] = None,
        perform_io_checks: Optional[bool] = None,
    ) -> "ValidationContext":
        return ValidationContext(
            root=self.root if root is None else root,
            warning_level=(
                self.warning_level if warning_level is None else warning_level
            ),
            file_name=self.file_name if file_name is None else file_name,
            perform_io_checks=(
                self.perform_io_checks
                if perform_io_checks is None
                else perform_io_checks
            ),
        )

    def __enter__(self):
        self._context_tokens.append(validation_context_var.set(self))
        return self

    def __exit__(self, type, value, traceback):  # type: ignore
        validation_context_var.reset(self._context_tokens.pop(-1))


validation_context_var: ContextVar[ValidationContext] = ContextVar(
    "validation_context_var", default=ValidationContext()
)
