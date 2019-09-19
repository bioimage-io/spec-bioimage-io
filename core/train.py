import torch
import torch.utils.data
from tqdm import trange

from .transforms import apply_transforms
from .parser import parse_config


def train(config_file, out_file):
    config = parse_config(config_file)
    model, train_config, data_config = config['model'], config['training'], config['data']
    model.train()

    optimizer, loss = train_config['optimizer'], train_config['loss']
    loss_trafos, batch_size = train_config['transforms'], train_config['batch_size']
    ds = train_config['dataset']
    n_iterations = train_config['n_iterations']

    in_trafos = data_config['input_transforms']

    loader = torch.utils.data.DataLoader(ds, shuffle=True, num_workers=2, batch_size=batch_size)

    for ii in trange(n_iterations):
        x, y = next(iter(loader))
        optimizer.zero_grad()

        x, y = apply_transforms(in_trafos, x, y)
        out = model(x)
        out, y = apply_transforms(loss_trafos, out, y)
        ll = loss(out, y)

        ll.backward()
        optimizer.step()

    # save model weights
    torch.save(model.state_dict(), out_file)
