import os
import importlib
from runpy import run_path

import torch
import torch.utils.data
import yaml
from tqdm import trange
from nuclei_dataset import NucleiDataset


def apply_transforms(transforms, *tensors):
    if not all(callable(trafo) for trafo in transforms):
        raise ValueError("Expect iterable with callables")
    for trafo in transforms:
        tensors = trafo(*tensors)
    return tensors


def train(model, train_config, out_file):
    model.train()

    optimizer_conf, loss = train_config['optimizer'], train_config['loss']
    optimizer = optimizer_conf['class'](model.parameters(), **optimizer_conf['kwargs'])
    preprocess = train_config['preprocess']

    # TODO don't hardcode this, but load from config!
    ds = NucleiDataset()
    n_iterations = 100
    batch_size = 2
    # ds = train_config['dataset']
    # n_iterations = train_config['n_iterations']
    # batch_size = train_config['batch_size']

    loader = torch.utils.data.DataLoader(ds, shuffle=True, num_workers=2, batch_size=batch_size)

    for ii in trange(n_iterations):
        x, y = next(iter(loader))
        optimizer.zero_grad()

        x, y = apply_transforms(preprocess, x, y)
        out = model(x)
        # kinda hacky ...
        out, y = apply_transforms(loss[:-1], out, y)
        ll = loss[-1](out, y)

        ll.backward()
        optimizer.step()

    # save model weights
    torch.save(model.state_dict(), out_file)


def instantiate_from_file(file_path, name, kwargs={}):
    # NOTE runpy is unsafe and should not be used in production
    return run_path(file_path)[name](**kwargs)


def class_from_module(module, name):
    m = importlib.import_module(module)
    return getattr(m, name)


def instantiate_from_module(module, name, kwargs={}):
    return class_from_module(module, name)(**kwargs)


def instantiate_from_config(name, kwargs={}, reference_path=None):
    # parse the name
    if ":" in name:
        file_path, to_import = name.split(":")
        if reference_path is not None:
            file_path = os.path.join(reference_path, file_path)
        return instantiate_from_file(file_path, to_import, kwargs)
    else:
        name_split = name.split('.')
        to_import = name_split[-1]
        module = '.'.join(name_split[:-1])
        return instantiate_from_module(module, to_import, kwargs)


def parse_transform(trafo):
    source = trafo['source']
    kwargs = trafo.get('kwargs', {})
    with open(source, 'r') as f:
        trafo_config = yaml.load(f, Loader=yaml.SafeLoader)
    trafo_source = trafo_config['source']
    # these are only here for reference
    # kwargs = trafo_config['kwargs']
    ref_path = os.path.split(source)[0]
    return instantiate_from_config(trafo_source, reference_path=ref_path, kwargs=kwargs)


def parse_training_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)['training']

    # parse the preprocess config
    preprocess = config['preprocess']
    preprocess = [parse_transform(trafo) for trafo in preprocess]

    # parse the loss
    loss = config['loss']
    loss = [parse_transform(trafo) for trafo in loss]

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
        config = yaml.load(f, Loader=yaml.SafeLoader)

    source = config['source']
    kwargs = config.get('kwargs', {})

    file_path, to_import = source.split(":")
    return instantiate_from_file(file_path, to_import, kwargs)


def training(config, output):
    train_config = parse_training_config(config)
    model = load_model(config)
    train(model, train_config, output)


if __name__ == '__main__':
    training('./UNet2dExample.model.yaml', 'unet2d_weights.torch')
