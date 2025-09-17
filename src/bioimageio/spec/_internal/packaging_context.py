from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Literal, Optional, Sequence, Union, cast

from .io import FileDescr
from .io_basics import FileName
from .utils import SLOTS


@dataclass(frozen=True, **SLOTS)
class PackagingContext:
    _context_tokens: "List[Token[Optional[PackagingContext]]]" = field(
        init=False,
        default_factory=cast(
            "Callable[[], List[Token[Optional[PackagingContext]]]]", list
        ),
    )

    bioimageio_yaml_file_name: FileName

    file_sources: Dict[FileName, FileDescr]
    """File sources to include in the packaged resource"""

    weights_priority_order: Optional[Sequence[str]] = None
    """set to select a single weights entry when packaging model resources"""

    def replace(
        self,
        *,
        bioimageio_yaml_file_name: Optional[FileName] = None,
        file_sources: Optional[Dict[FileName, FileDescr]] = None,
        weights_priority_order: Union[
            Optional[Sequence[str]], Literal["unchanged"]
        ] = "unchanged",
    ) -> "PackagingContext":
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
        )

    def __enter__(self):
        self._context_tokens.append(packaging_context_var.set(self))
        return self

    def __exit__(self, type, value, traceback):  # type: ignore
        packaging_context_var.reset(self._context_tokens.pop(-1))


packaging_context_var: ContextVar[Optional[PackagingContext]] = ContextVar(
    "packaging_context_var", default=None
)
