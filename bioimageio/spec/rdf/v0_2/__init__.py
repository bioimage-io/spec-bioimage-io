from . import nodes
from typing import get_args

format_version: nodes.LatestFormatVersion = get_args(nodes.LatestFormatVersion)[-1]
