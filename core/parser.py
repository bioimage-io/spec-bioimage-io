import os
from runpy import run_path

import yaml
import torch.nn as nn
import torch.optim as optim

from . import data as datasets
from . import transforms as core_trafos


def get_class(name, packages):
    for pkg in packages:
        if hasattr(pkg, name):
            return getattr(pkg, name)
    raise AttributeError("Did not find %s" % name)


def parse_train_config(train_config, model):
    loss_config = train_config['loss']
    loss = get_class(loss_config['name'], [nn])(**loss_config.get('kwargs', {}))

    transform_config = loss_config.get('transformations', [])
    transforms = [get_class(trafo['name'], [core_trafos])(**trafo.get('kwargs', {}))
                  for trafo in transform_config]

    optimizer_config = train_config['optimizer']
    optimizer = get_class(optimizer_config['name'], [optim])(model.parameters(),
                                                             **optimizer_config.get('kwargs', {}))

    batch_size = train_config['batch_size']

    # This needs to be more sophisticated in practice
    # need to support concatenating multiple datasets
    # need to support custom urls/dois and validate hashes
    ds_config = train_config['pretrained_on'][0]
    ds = get_class(ds_config['name'], [datasets])()

    return {'loss': loss, 'optimizer': optimizer,
            'transforms': transforms, 'batch_size': batch_size,
            'dataset': ds}


def parse_data_config(data_config):
    in_config = data_config['input_transformations']
    in_transforms = [get_class(trafo['name'], [core_trafos])(**trafo.get('kwargs', {}))
                     for trafo in in_config]

    out_config = data_config['output_transformations']
    out_transforms = [get_class(trafo['name'], [core_trafos])(**trafo.get('kwargs', {}))
                      for trafo in out_config]

    return {'input_transforms': in_transforms, 'output_transforms': out_transforms}


def parse_model_config(model_config, path):
    definition = model_config['definition']
    script = definition['source']
    name = definition['name']
    kwargs = definition.get('kwargs', {})

    script_file = os.path.join(os.path.split(path)[0], script)

    if not os.path.exists(script_file):
        raise RuntimeError("Script %s does not exist" % script_file)

    # NOTE runpy should not be used in production,
    # use importlib instead (I was just to lazy to figure it out now)
    script_globals = run_path(script_file)
    if name not in script_globals:
        raise RuntimeError("Class name %s does not exist" % name)
    model = script_globals[name](**kwargs)
    return model


def parse_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.load(f)

    model = parse_model_config(config['model'], config_file)
    train_dict = parse_train_config(config['training'], model)
    data_dict = parse_data_config(config['data'])
    return {'model': model, 'training': train_dict, 'data': data_dict}
