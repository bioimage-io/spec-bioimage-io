from typing import List, Literal, Union

from pydantic import BaseModel
from pydantic_core.core_schema import ErrorType

from bioimageio.spec.types import Loc, WarningLevelName


class ValidationOutcome(BaseModel):
    loc: Loc
    msg: str


class ErrorOutcome(ValidationOutcome):
    type: Union[ErrorType, str]


class WarningOutcome(ValidationOutcome):
    type: WarningLevelName


class ValidationSummary(BaseModel):
    bioimageio_spec_version: str
    name: str
    source_name: str
    status: Union[Literal["passed", "failed"], str]
    errors: List[ErrorOutcome]
    traceback: List[str]
    warnings: List[WarningOutcome]
