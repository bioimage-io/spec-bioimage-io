from pathlib import Path

from bioimageio.spec.shared.nodes import ImportedSource
from .raw_nodes import *


@dataclass
class RDF(RDF):
    covers: List[Path] = missing
    documentation: Path = missing


@dataclass
class PickleWeightsEntry(PickleWeightsEntry):
    source: Path = missing


@dataclass
class PytorchStateDictWeightsEntry(PytorchStateDictWeightsEntry):
    source: Path = missing


@dataclass
class PytorchScriptWeightsEntry(PytorchScriptWeightsEntry):
    source: Path = missing


@dataclass
class KerasHdf5WeightsEntry(KerasHdf5WeightsEntry):
    source: Path = missing


@dataclass
class TensorflowJsWeightsEntry(TensorflowJsWeightsEntry):
    source: Path = missing


@dataclass
class TensorflowSavedModelBundleWeightsEntry(TensorflowSavedModelBundleWeightsEntry):
    source: Path = missing


@dataclass
class OnnxWeightsEntry(OnnxWeightsEntry):
    source: Path = missing


WeightsEntry = Union[
    PickleWeightsEntry,
    PytorchStateDictWeightsEntry,
    PytorchScriptWeightsEntry,
    KerasHdf5WeightsEntry,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
    OnnxWeightsEntry,
]


@dataclass
class WeightsEntry(WeightsEntryBase):
    source: Path = missing


@dataclass
class Model(Model):
    source: ImportedSource = missing
    test_inputs: List[Path] = missing
    test_outputs: List[Path] = missing
    weights: Dict[WeightsFormat, WeightsEntry] = missing
