# Bioimiage.io Entry Configuration

An entry in the bioimage.io model zoo is defined by a configuration yaml configuration file according to the following specification:
The configuration must contain the keys  `version`, `language`, `framework`, `model`, `training`, `data`, `meta`.

## version

Version of the bioimage.io configuration spec. (Should be in synch with core library).

## language

Programming language of the model definition. Must map to one of `python`, `java` or `javascript`.

## framework

Deep learning framework used for this entry. Currently supported frameworks are `tensorflow` and `pytorch`.

## model

Model definition and weights.
Must contain the keys:
- `definition`: script with model definition.
  - `source`: relative path from config file to the script
  - `hash`: hash of the script file
  - `name`: Name of class defining the model in `script`
  - `kwargs`: Optional keyword arguments for the model class. 
- `weights`: model weights
  -  source: link to the model weight file
  - hash: hash of the model weight file
- `input_axes`: Expected input axes of the model
- `input_size`: Valid input size for the model
- `output_axes`: Output axes of the model

Can contain:
- `kwargs`: Keyword argument passed to the constructor of `class_name`.
- `documentation`: Relative path to file with additional documentation in markdown.
- `minimal_valid_step`: Minimal valid step size per axis when changing inut size.

## training

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
  - `n_epocs`: Number of epochs used in training (change to iterations ?)
- `batch_size`: batch size used for training

## data

Additional transformations.
Can contain:
- `input_transformations`: List of transformations applied to data before passed to the model.
- `output_transformatons`:

## meta

Additional information.


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
        n_epochs: 10  # maybe change to iterations?
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
