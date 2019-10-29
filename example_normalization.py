def NormalizeZeroMeanUnitVariance(inputs, targets=None, input_indices=None, target_indices=None):
    inputs = normalize(inputs)
    if apply_to_target:
        targets = normalize(targets)
    return inputs, target
