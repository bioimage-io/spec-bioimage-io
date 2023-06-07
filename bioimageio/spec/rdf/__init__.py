from . import v0_2

# autogen: start
from . import nodes

try:
    from typing import get_args
except ImportError:
    from typing_extensions import get_args  # type: ignore

format_version = get_args(nodes.FormatVersion)[-1]

# autogen: stop
