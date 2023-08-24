from typing import List, Literal, Union

from pydantic import BaseModel, Field
from pydantic_core.core_schema import ErrorType

from bioimageio.spec import __version__
from bioimageio.spec.types import Loc, WarningLevelName


class ValidationOutcome(BaseModel):
    loc: Loc
    msg: str


class ErrorOutcome(ValidationOutcome):
    type: Union[ErrorType, str]


class WarningOutcome(ValidationOutcome):
    type: WarningLevelName


class ValidationSummary(BaseModel):
    name: str
    source_name: str
    status: Literal["passed", "failed"]
    # status_details: Dict[str, str] = Field(default_factory=dict)
    errors: List[ErrorOutcome] = Field(default_factory=list)
    traceback: List[str] = Field(default_factory=list)
    warnings: List[WarningOutcome] = Field(default_factory=list)
    bioimageio_spec_version: str = __version__
