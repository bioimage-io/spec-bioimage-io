# type: ignore
# errors like:
# Name "RDF" already defined (possibly by an import)
# todo: get rid of * import
from bioimageio.spec.shared.nodes import ImportedSource
from .raw_nodes import *


@dataclass
class RDF(RDF):
    covers: List[Path] = missing
    documentation: Path = missing


@dataclass
class KerasHdf5WeightsEntry(KerasHdf5WeightsEntry):
    source: Path = missing


@dataclass
class OnnxWeightsEntry(OnnxWeightsEntry):
    source: Path = missing


@dataclass
class PytorchStateDictWeightsEntry(PytorchStateDictWeightsEntry):
    source: Path = missing


@dataclass
class PytorchScriptWeightsEntry(PytorchScriptWeightsEntry):
    source: Path = missing


@dataclass
class TensorflowJsWeightsEntry(TensorflowJsWeightsEntry):
    source: Path = missing


@dataclass
class TensorflowSavedModelBundleWeightsEntry(TensorflowSavedModelBundleWeightsEntry):
    source: Path = missing


WeightsEntry = Union[
    KerasHdf5WeightsEntry,
    OnnxWeightsEntry,
    PytorchScriptWeightsEntry,
    PytorchStateDictWeightsEntry,
    TensorflowJsWeightsEntry,
    TensorflowSavedModelBundleWeightsEntry,
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
