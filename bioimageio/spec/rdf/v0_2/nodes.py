# type: ignore
# errors like:
# Name "RDF" already defined (possibly by an import)
# todo: get rid of * import
from .raw_nodes import *


@dataclass
class RDF(RDF):
    covers: List[Path] = missing
    documentation: Path = missing
