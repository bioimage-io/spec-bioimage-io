from bioimageio.spec.shared.model_loader_utils import ModelLoaderBase
from . import converters, nodes, raw_nodes, schema


class ModelLoader(ModelLoaderBase):
    preceding_model_loader = None
    converters = converters
    schema = schema
    raw_nodes = raw_nodes
    nodes = nodes


load_raw_model = ModelLoader.load_raw_model
load_model = ModelLoader.load_model
