from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List

from marshmallow import missing

from . import raw_nodes

Axes = raw_nodes.Axes
CiteEntry = raw_nodes.CiteEntry
Dependencies = raw_nodes.Dependencies
FormatVersion = raw_nodes.FormatVersion
Framework = raw_nodes.Framework
ImplicitInputShape = raw_nodes.ImplicitInputShape
ImplicitOutputShape = raw_nodes.ImplicitOutputShape
InputTensor = raw_nodes.InputTensor
Language = raw_nodes.Language
Node = raw_nodes.Node
OutputTensor = raw_nodes.OutputTensor
Postprocessing = raw_nodes.Postprocessing
PostprocessingName = raw_nodes.PostprocessingName
Preprocessing = raw_nodes.Preprocessing
PreprocessingName = raw_nodes.PreprocessingName
RunMode = raw_nodes.RunMode
WeightsFormat = raw_nodes.WeightsFormat


@dataclass
class ImportedSource:
    factory: Callable

    def __call__(self, *args, **kwargs):
        return self.factory(*args, **kwargs)


@dataclass
class RDF(raw_nodes.RDF):
    covers: List[Path] = missing
    documentation: Path = missing


@dataclass
class WeightsEntry(raw_nodes.WeightsEntry):
    source: Path = missing


@dataclass
class Model(raw_nodes.Model):
    source: ImportedSource = missing
    test_inputs: List[Path] = missing
    test_outputs: List[Path] = missing
    weights: Dict[WeightsFormat, WeightsEntry] = missing
