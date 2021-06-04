# Model Description File Specification

[This specification](./generated/bioimageio_model_spec.md) defines a file format for representing pretrained AI models in [YAML format](https://en.wikipedia.org/wiki/YAML). This format is used to describe models hosted on the [BioImage.IO](https://bioimage.io) model repository site.


A BioImage.IO compatible model description file (MDF) must fulfill the following rules:
 * must be a YAML file encoded as UTF-8
 * file extension must be `.yaml` (instead of `.yml`)
 * the contained fields must follow the [specification documented here](./generated/bioimageio_model_spec.md)

It is recommended to:
 * use the [model spec validator](#model-specification-validator) to verify the format
 * store the yaml file in a version controlled Git repository (e.g. Github or Gitlab).
 * stored in a folder with a descriptive name for the model, and place the MDF inside the folder and name it as `model.yaml`.
 * the model folder can be packaged into a zip file, and the package name should use a descriptive name + `.model.zip`.
 * use or upgrade to the latest format version


# Model Specification Validator
## Installation

<!--
TODO from pip/conda
-->


Install from source and in development mode
```
pip install git+https://github.com/bioimage-io/spec-bioimage-io
```

## Usage

You can verify a model configuration in the [bioimage.io model format](./generated/bioimageio_model_spec.md) using the following command:
```
python -m bioimageio.spec verify-spec <MY-MODEL>.model.yaml
```
The output of this command will indicate missing or invalid fields in the model file. For example, if the field `timestamp` was missing it would print the following:
```
{'timestamp': ['Missing data for required field.']}
```
or if the field `test_inputs` does not contain a list, it would print:
```
{'test_inputs': ['Not a valid list.']}.
```


# Example Configurations
## PyTorch
 - [UNet 2D Nuclei Broad](https://github.com/bioimage-io/pytorch-bioimage-io/blob/master/specs/models/unet2d_nuclei_broad/UNet2DNucleiBroad.model.yaml).

# Changelog
 * **0.3.2**: 
    - Change `author` and `packaged_by` fields from List[str] to List[Author] with Author consisting of a dictionary {name: '<Full name>', affiliation: '<Affiliation>', orcid: 'optional orcid id'}
    - Add `type` field to comply with other bioimage.io RDFs. Only valid value is 'model'.
    - Add optional `version` field (default 0.1.0) to keep track of model changes.
    - Add optional `id` field as a unique identifier (the use of [doi](doi.org) is encouraged).
    - Only allow `license` identifier from the [SPDX license list](https://spdx.org/licenses/).
