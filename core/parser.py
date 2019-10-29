import importlib
from runpy import run_path
import yaml


def instantiate_from_file(file_path, name, kwargs={}):
    # NOTE runpy is unsafe and should not be used in production
    return run_path(file_path)[name](**kwargs)


def class_from_module(module, name):
    m = importlib.import_module(module)
    return getattr(m, name)


def instantiate_from_module(module, name, kwargs={}):
    return class_from_module(module, name)(**kwargs)


def instantiate_from_config(name, kwargs={}):
    # parse the name
    if ":" in name:
        file_path, to_import = name.split(":")
        return instantiate_from_file(file_path, to_import, kwargs)
    else:
        name_split = name.split('.')
        to_import = name_split[-1]
        module = '.'.join(name_split[:-1])
        return instantiate_from_module(module, to_import, kwargs)


# TODO
def parse_prediction_config(config_file):
    # with open(config_file, 'r') as f:
    #     config = yaml.load(f)['prediction']
    pass


def parse_training_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)['training']

    # parse the preprocess config
    preprocess = config['preprocess']
    preprocess = [instantiate_from_config(**pre) for pre in preprocess]

    # parse the loss
    loss = config['loss']
    loss = [instantiate_from_config(**lo) for lo in loss]

    # parse the optimizer
    optimizer_conf = config['optimizer']
    name_split = optimizer_conf['name'].split('.')
    to_import = name_split[-1]
    module = '.'.join(name_split[:-1])
    optimizer = class_from_module(module, to_import)
    optimizer_kwargs = optimizer_conf.get('kwargs', {})

    # TODO parse the rest as well
    return {'preprocess': preprocess,
            'loss': loss,
            'optimizer': {'class': optimizer, 'kwargs': optimizer_kwargs}}


def load_model(config_file):
    with open(config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)['model']

    definition = config['definition']
    source = definition['source']
    kwargs = definition.get('kwargs', {})

    file_path, to_import = source.split(":")
    return instantiate_from_file(file_path, to_import, kwargs)
