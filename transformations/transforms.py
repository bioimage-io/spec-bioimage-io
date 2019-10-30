import torch


class Sigmoid:
    def __init__(self, apply_to):
        self.apply_to = apply_to

    def __call__(self, *tensors):
        ret = [torch.sigmoid(x) if ii in self.apply_to else x
               for ii, x in enumerate(tensors)]
        return ret


class NormalizeZeroMeanUnitVariance:
    def __init__(self, apply_to, eps):
        self.eps = eps
        self.apply_to = apply_to

    def normalize(self, x):
        return (x - x.mean()) / (x.std() + self.eps)

    def __call__(self, *tensors):
        ret = [self.normalize(x) if ii in self.apply_to else x
               for ii, x in enumerate(tensors)]
        return ret
