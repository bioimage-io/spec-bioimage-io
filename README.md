# Bioimiage.io Configuration Specification

## Transformation Specification:
A transformation in the bioimage.io model zoo is defined by a configuration file `<transformation name>.transformation.yaml` according to the following specification
The configuration must contain the keys: `name`, `description`, `format_version`, `language`, `cite`, `authors`, `documentation`, `tags`, `dependencies`, `source`, `kwargs`, `inputs`, and `outputs`. The following additional keys are optional: `thumbnail`, `test_input`, and `test_output`.

### `name`
###  `description`
### `format_version`
Version of this bioimage.io configuration spec.

### `language`
Programming language of the model definition. Must map to one of `python`, `java` or `javascript`.

### `cite`

### `authors`

### `documentation`
Relative path to file with additional documentation in markdown.

### `tags`

### `dependencies`

### `source`
<relative path from config file to the implementation source file>:<identifier of transformation/model within the source file>

### `kwargs`
Keyword arguments for the transformation/model class specified by [`source`](#source).

### `inputs`
Either a string from the following choices:
  - any: any number/shape of input tensors is accepted/returned

or a list of [tensor specifications](#tensor-specification).

#### tensor specification
- name: input1
- axes: string of axes identifiers, e.g. btczyx
- data_type: data type (e.g. float32)
- data_range: tuple of (minimum, maximum)
- [shape]: optional: needed if shape restrictions apply
     - Either
       - `min`: minimum shape with same length as `axes`.
       - `step`: minimum shape change with same length as `axes`. 
     - or
       - `exact`: exact shape (or list thereof) with same lenght as `axes`

### `outputs`
Either a string from the following choices:
  - any: any number/shape of input tensors is accepted/returned
  - identity: number/shape of output tensors is the same as input tensors
  - same number: same number of tensors as given to input is returned (shape may differ)

or a list of [tensor specifications](#tensor-specification).

### `thumbnail`

### `test_input`

### `test_output`

## Model Specification:
A model entry in the bioimage.io model zoo is defined by a configuration file `<model name>.model.yaml` according to the [transformation specification](#transformation-entry) and the **additional** following specification:
The configuration must contain the keys: `framework`, `prediction`, and `training`.

### `framework`
Deep learning framework used for this model. Currently supported frameworks are `tensorflow` and `pytorch`.

### `prediction`
Sub specification of prediction:
- `weights`: model weights
  `source`: link to the model weight file
  `hash`: hash of hash of the model weight file specified by `source`

### `training`
Sub specification of training:
todo
Definition of the training procedure.
Must contain:
- `loss`: loss function used in training
  - `name`: name of the loss function (must)
  - `kwargs`: keyword arguments for the loss function (can)
  - `transformations`: list of transformations applied to model output before passed to loss (can)
- `optimizer`: optimizer used in training
  - `name`: Name of the optimizer (must)
  - `kwargs`: keyword arguments for the optimizer (can)
- `pretrained_on`: description of pre-training:
  - `datasets`: list of datasets the model was trained on, valid entry:
    - `name`: Name of dataset in the core library.
    - TODO need optional ways of specifying identifiers for custom training data via url / doi
  - `n_iterations`: Number of iterations used in training (change to iterations ?)
- `batch_size`: batch size used for training



## data

Additional transformations.
Can contain:
- `input_transformations`: List of transformations applied to data before passed to the model.
- `output_transformatons`:


# Example Configuration

```yaml
version: 0.0.1
language: python
framework:
    pytorch: 1.1

model:
    definition:
        source: unet2d.py
        hash: {sha256: 27892992d157f4cf10d7ab4365c83fc29eb6f1f7e6031049cfbd859e5891ebe0}
        name: UNet2d
        kwargs: {input_channels: 1, output_channels: 1}
    weights:
        source: 10.5281/zenodo.3446812
        hash: {md5: c16cb3ba3cb9d257550fd19067ecfb91}
    documentation: unet2d.md
    input_axes: "cyx"
    input_size: [1, 256, 256]
    minimal_valid_step: [0, 32, 32]
    output_axes: "cyx"

training:
    loss:
        name: BCELoss
        kwargs: {reduction: "mean"}
        transformations:
            - {name: Sigmoid}
    optimizer:
        name: Adam
        kwargs: {lr: 0.002}
    pretrained_on:
        datasets:
            - {name: NucleiDataset}  # optional: source : {identifier: doi/url, hash: hash_value}
        n_iterations: 500
    batch_size: 4

data:
    input_transformations:
        - {name: NormalizeZeroMeanUnitVariance, kwargs: {eps: 0.000001}}
    output_transformations:
        - {name: Sigmoid}

meta:
    description: A 2d U-Net pretrained on broad nucleus dataset.
    cite: "Ronneberger, Olaf et al. U-net: Convolutional networks for biomedical image segmentation. MICCAI 2015."
    parent_model: 2d-unet
```
