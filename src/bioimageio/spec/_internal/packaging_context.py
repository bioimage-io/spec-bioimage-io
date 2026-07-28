from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Callable, List, Literal, Sequence, cast

from .io import FileDescr
from .io_basics import FileName
from .utils import SLOTS


@dataclass(frozen=True, **SLOTS)
class PackagingContext:
    _context_tokens: list[Token[PackagingContext | None]] = field(
        init=False,
        default_factory=cast(
            "Callable[[], List[Token[PackagingContext | None]]]", list
        ),
    )

    bioimageio_yaml_file_name: FileName

    file_sources: dict[FileName, FileDescr]
    """File sources to include in the packaged resource"""

    weights_priority_order: Sequence[str] | None = None
    """set to select a single weights entry when packaging model resources"""

    local_files_only: bool = False
    """Whether to include only local files when packaging. If True, remote files will be excluded."""

    def replace(
        self,
        *,
        bioimageio_yaml_file_name: FileName | None = None,
        file_sources: dict[FileName, FileDescr] | None = None,
        weights_priority_order: Sequence[str]
        | None
        | Literal["unchanged"] = "unchanged",
        local_files_only: bool | None = None,
    ) -> PackagingContext:
        """return a modiefied copy"""
        return PackagingContext(
            bioimageio_yaml_file_name=(
                self.bioimageio_yaml_file_name
                if bioimageio_yaml_file_name is None
                else bioimageio_yaml_file_name
            ),
            file_sources=(
                dict(self.file_sources) if file_sources is None else file_sources
            ),
            weights_priority_order=(
                self.weights_priority_order
                if weights_priority_order == "unchanged"
                else weights_priority_order
            ),
            local_files_only=(
                self.local_files_only if local_files_only is None else local_files_only
            ),
        )

    def __enter__(self):
        self._context_tokens.append(packaging_context_var.set(self))
        return self

    def __exit__(self, type, value, traceback):  # type: ignore
        packaging_context_var.reset(self._context_tokens.pop(-1))


packaging_context_var: ContextVar[PackagingContext | None] = ContextVar(
    "packaging_context_var", default=None
)
