import torch


class Sigmoid:
    def __call__(self, x, y=None):
        return torch.sigmoid(x), y


class NormalizeZeroMeanUnitVariance:
    def __init__(self, eps=1e-6):
        self.eps = eps

    def __call__(self, x, y=None):
        return (x - x.mean()) / (x.std() + self.eps), y


def apply_transforms(transforms, x, y=None):
    if not all(callable(trafo) for trafo in transforms):
        raise ValueError("Expect iterable with callables")
    for trafo in transforms:
        x, y = trafo(x, y)
    return x, y
