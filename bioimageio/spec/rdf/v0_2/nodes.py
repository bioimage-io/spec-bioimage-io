# type: ignore
# errors like:
# Name "RDF" already defined (possibly by an import)
# todo: get rid of * import
from .raw_nodes import *
from bioimageio.spec.shared import nodes as shared_nodes

Dependencies = shared_nodes.Dependencies


@dataclass
class RDF(RDF):
    covers: List[Path] = missing
    documentation: Path = missing
