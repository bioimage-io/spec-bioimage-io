"""
raw_nodes 0.1 only implements the Model class (and its requirements) and not other aspects of the deprecated 0.1 spec
"""
import pathlib
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, NewType, Tuple, Union

from marshmallow.utils import _Missing, missing

from bioimageio.spec.shared.raw_nodes import ImplicitInputShape, ImplicitOutputShape, Node, SpecURI, URI

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal  # type: ignore


ModelFormatVersion = Literal["0.1.0"]


@dataclass
class CiteEntry(Node):
    text: str = missing
    doi: Union[_Missing, str] = missing
    url: Union[_Missing, str] = missing


@dataclass
class BaseSpec(Node):
    name: str = missing
    format_version: ModelFormatVersion = missing
    description: str = missing
    cite: List[CiteEntry] = missing
    authors: List[str] = missing
    documentation: pathlib.Path = missing
    tags: List[str] = missing
    license: str = missing

    language: str = missing
    framework: Union[_Missing, str] = missing
    source: str = missing
    required_kwargs: Union[_Missing, List[str]] = missing
    optional_kwargs: Union[_Missing, Dict[str, Any]] = missing

    test_input: Union[_Missing, pathlib.Path] = missing
    test_output: Union[_Missing, pathlib.Path] = missing
    covers: Union[_Missing, List[pathlib.Path]] = missing


@dataclass
class Weights(Node):
    source: URI
    hash: Dict[str, str]


@dataclass
class SpecWithKwargs(Node):
    spec: SpecURI = missing
    kwargs: Union[_Missing, Dict[str, Any]] = missing


@dataclass
class Transformation(SpecWithKwargs):
    pass


@dataclass
class Prediction(Node):
    weights: Weights = missing
    dependencies: str = missing
    preprocess: Union[_Missing, List[Transformation]] = missing
    postprocess: Union[_Missing, List[Transformation]] = missing


Axes = str


@dataclass
class Array(Node):
    name: str = missing
    axes: Union[_Missing, Axes] = missing
    data_type: str = missing
    data_range: Union[_Missing, Tuple[float, float]] = missing


@dataclass
class InputArray(Array):
    shape: Union[List[int], ImplicitInputShape] = missing


@dataclass
class OutputArray(Array):
    shape: Union[List[int], ImplicitOutputShape] = missing
    halo: Union[_Missing, List[int]] = missing


@dataclass
class Model(BaseSpec):
    type: ClassVar[str] = "model"
    config: Union[_Missing, dict] = missing
    inputs: List[InputArray] = missing
    outputs: List[OutputArray] = missing
    prediction: Prediction = missing
    training: Union[_Missing, dict] = missing
