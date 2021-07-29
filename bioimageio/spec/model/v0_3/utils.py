from bioimageio.spec.shared.io_ import IO_Base
from . import converters, nodes, raw_nodes, schema
from .. import v0_1


class IO(IO_Base):
    preceding_io_class = v0_1.utils.IO
    converters = converters
    schema = schema
    raw_nodes = raw_nodes
    nodes = nodes
