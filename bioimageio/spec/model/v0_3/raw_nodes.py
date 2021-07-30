from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Union

from marshmallow import missing
from marshmallow.utils import _Missing

from bioimageio.spec.rdf import v0_2 as rdf
from bioimageio.spec.shared.raw_nodes import (
    ImplicitInputShape,
    ImplicitOutputShape,
    ImportableModule,
    ImportableSourceFile,
    RawNode,
    URI,
)
from . import base_nodes

# reassign to use imported classes
ImplicitInputShape = ImplicitInputShape
ImplicitOutputShape = ImplicitOutputShape

# same as general RDF
Author = rdf.nodes.Author
Badge = rdf.nodes.Badge
CiteEntry = rdf.nodes.CiteEntry
Dependencies = rdf.nodes.Dependencies


@dataclass
class RunMode(RawNode, base_nodes.RunMode):
    pass


@dataclass
class Preprocessing(RawNode, base_nodes.Preprocessing):
    pass


@dataclass
class Postprocessing(RawNode, base_nodes.Postprocessing):
    pass


@dataclass
class InputTensor(RawNode, base_nodes.InputTensor):
    pass


@dataclass
class OutputTensor(RawNode, base_nodes.OutputTensor):
    pass


@dataclass
class WeightsEntryBase(RawNode, base_nodes.WeightsEntryBase):
    source: Path = missing


@dataclass
class KerasHdf5WeightsEntry(WeightsEntryBase, base_nodes.KerasHdf5WeightsEntry):
    pass


@dataclass
class OnnxWeightsEntry(WeightsEntryBase, base_nodes.OnnxWeightsEntry):
    pass


@dataclass
class PytorchStateDictWeightsEntry(WeightsEntryBase, base_nodes.PytorchStateDictWeightsEntry):
    pass


@dataclass
class PytorchScriptWeightsEntry(WeightsEntryBase, base_nodes.PytorchScriptWeightsEntry):
    pass


@dataclass
class TensorflowJsWeightsEntry(WeightsEntryBase, base_nodes.TensorflowJsWeightsEntry):
    pass


@dataclass
class TensorflowSavedModelBundleWeightsEntry(WeightsEntryBase, base_nodes.TensorflowSavedModelBundleWeightsEntry):
    pass


WeightsEntry = Union[
    KerasHdf5WeightsEntry,
    OnnxWeightsEntry,
    PytorchScriptWeightsEntry,
    PytorchStateDictWeightsEntry,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
]

ImportableSource = Union[ImportableSourceFile, ImportableModule]


@dataclass
class Model(base_nodes.Model, rdf.raw_nodes.RDF, RawNode):
    source: Union[_Missing, ImportableSource] = missing
    test_inputs: List[URI] = missing
    test_outputs: List[URI] = missing
    weights: Dict[base_nodes.WeightsFormat, WeightsEntry] = missing
