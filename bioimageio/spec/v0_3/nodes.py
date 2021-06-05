from __future__ import annotations

from typing import Callable

from .raw_nodes import *


@dataclass
class ImportedSource:
    factory: Callable

    def __call__(self, *args, **kwargs):
        return self.factory(*args, **kwargs)


@dataclass
class RDF(RDF):
    covers: List[Path] = missing
    documentation: Path = missing


@dataclass
class WeightsEntry(WeightsEntry):
    source: Path = missing


@dataclass
class Model(Model):
    source: ImportedSource = missing
    test_inputs: List[Path] = missing
    test_outputs: List[Path] = missing
    weights: Dict[WeightsFormat, WeightsEntry] = missing
