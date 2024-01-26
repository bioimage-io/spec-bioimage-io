from contextvars import ContextVar
from pathlib import Path
from typing import Literal, Optional, Union

from pydantic import AnyUrl, BaseModel, DirectoryPath, PrivateAttr

from bioimageio.spec._internal import settings

WarningSeverity = Literal[20, 30, 35]
WarningLevel = Literal[WarningSeverity, 50]
"""With warning level x validation warnings of severity >=x are raised.
Highest warning level 50/error does not raise any validaiton warnings (only validation errors)."""


class ValidationContext(BaseModel, frozen=True):
    _context_tokens = PrivateAttr(default_factory=list)

    root: Union[DirectoryPath, AnyUrl] = Path()
    """url/directory serving as base to resolve any relative file paths"""

    warning_level: WarningLevel = 50
    """raise warnings of severity s as validation errors if s >= `warning_level`"""

    file_name: str = "bioimageio.yaml"
    """file name of the bioimageio Yaml file"""

    perform_io_checks: bool = settings.perform_io_checks
    """wether or not to perfrom validation that requires IO operations like download or reading a file from disk"""

    def copy(  # pyright: ignore[reportIncompatibleMethodOverride]  # note that pydantic.BaseModel.copy is deprecated
        self,
        root: Optional[Union[DirectoryPath, AnyUrl]] = None,
        warning_level: Optional[WarningLevel] = None,
        file_name: Optional[str] = None,
        perform_io_checks: Optional[bool] = None,
    ) -> "ValidationContext":
        return ValidationContext(
            root=self.root if root is None else root,
            warning_level=self.warning_level if warning_level is None else warning_level,
            file_name=self.file_name if file_name is None else file_name,
            perform_io_checks=self.perform_io_checks if perform_io_checks is None else perform_io_checks,
        )

    def __enter__(self):
        self._context_tokens.append(validation_context_var.set(self))
        return self

    def __exit__(self, type, value, traceback):  # type: ignore
        validation_context_var.reset(self._context_tokens.pop(-1))


validation_context_var: ContextVar[ValidationContext] = ContextVar(
    "validation_context_var", default=ValidationContext()
)
