from typing import Literal

WarningSeverity = Literal[20, 30, 35]
WarningLevel = Literal[WarningSeverity, 50]
"""With warning level x validation warnings of severity >=x are raised.
Highest warning level 50/error does not raise any validaiton warnings (only validation errors)."""

ERROR, ERROR_NAME = 50, "error"
"""A warning of the error level is always raised (equivalent to a validation error)"""

ALERT, ALERT_NAME = 35, "alert"
"""no ALERT nor ERROR -> RDF is worriless"""

WARNING, WARNING_NAME = 30, "warning"
"""no WARNING nor ALERT nor ERROR -> RDF is watertight"""

INFO, INFO_NAME = 20, "info"
"""info warnings are about purely cosmetic issues, etc."""
