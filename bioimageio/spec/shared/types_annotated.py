from typing import Any, Mapping
import annotated_types
from pydantic.functional_validators import AfterValidator
from typing_extensions import Annotated
from bioimageio.spec.shared.validation import (
    # validate_relative_directory,
    # validate_relative_file_path,
    # validate_relative_path,
    validate_version,
    validate_raw_mapping,
)

Version = Annotated[str, AfterValidator(validate_version)]
CapitalStr = Annotated[str, AfterValidator(lambda s: s.capitalize())]
Sha256 = Annotated[str, annotated_types.Len(256, 256)]

# These <type>Field types convert the base type to a custom <type> from type_custom
# RelativePathField = Annotated[Union[pathlib.Path, str], AfterValidator(validate_relative_path)]
# RelativeFilePathField = Annotated[Union[pathlib.Path, str], AfterValidator(validate_relative_file_path)]
# RelativeDirecotryField = Annotated[Union[pathlib.Path, str], AfterValidator(validate_relative_directory)]

# RawMappingField does not convert the value, but pydantic cannot handle recursive type definitions
RawMappingField = Annotated[Mapping[str, Any], AfterValidator(validate_raw_mapping)]
