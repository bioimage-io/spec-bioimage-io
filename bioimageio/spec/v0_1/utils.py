from bioimageio.spec.shared.io import IO_Base
from . import converters, nodes, raw_nodes, schema


class IO(IO_Base):
    preceding_model_loader = None
    converters = converters
    schema = schema
    raw_nodes = raw_nodes
    nodes = nodes
