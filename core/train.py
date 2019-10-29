import torch
import torch.utils.data
from tqdm import trange

from .transforms import apply_transforms
from .data import NucleiDataset


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
