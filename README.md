# Bioimiage.io Entry Configuration

An entry in the bioimage.io model zoo is defined by a configuration stored as yaml according to the following specification:
The configuration must contain the keys  `version`, `language`, `framework`, `model`, `training`, `data`, `meta`.

## version

Must map to the version of the bioimage.io configuration spec. (Should be in synch with core library).

## language

Programming language of the model definition. Must map to one of `python`, `java` or `javascript`.

## framework

Deep learning frameworks for this entry. Currently supported frameworks are `tensorflow` and `pytorch`.

## model

Model definition file and weights.

## training

Definition of the training procedure.
The names of `loss` and `optimizer` must match a class in the core library.


# Example Configuration

```yaml
version: 0.0.1
language: python
framework:
    pytorch: 1.1

model:
    definition:
        source: link/to/definition.py
        hash: 12
    weights:
        source: link/to/weights.torch
        hash: 42
    documentation: link/to/doc.md

training:
    loss: BinaryCrossEntropy
    optimizer:
        Adam:
            beta: 0.01
    pretrained_on:
        - {source: doi1, hash: 21}
    batch_size: 4
    target:
        task: "Segmentation"
        n_classes: 2

data:
    input_axes: "cyx"
    input_channels: 1
    input_size: [256, 256]
    valid_step: [32, 32]
    input_transformations:
        - Normalize
    output_axes: "cyx"
    output_channels: 1

info:
    name: UNet2D
    description: A 2d U-Net pretrained on ISBI2012 EM segmentation challenge.
    cite: Ronneberger et al.
    parent_model: 2d-unet
```
