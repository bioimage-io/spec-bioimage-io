# Specifications for BioImage.IO

This repository contains specifications defined by the BioImage.IO community. These specifications are used for defining fields in YAML files which we called `Resource Description Files` or `RDF`. The RDFs can be downloaded or uploaded to the [bioimage.io website](https://bioimage.io), produced or consumed by BioImage.IO-compatible consumers(e.g. image analysis software or other website). Currently we defined two types of RDFs: a dedicated RDF specification for AI models (i.e. `model RDF`) and a generic RDF specification.


A BioImage.IO-compatible RDF must fulfill the following rules:
 * Must be a YAML file encoded as UTF-8;
 * The RDF file extension must be `.yaml` (instead of `.yml`)
 * The RDF file can be saved in a folder(or virtual folder) or in a zip package, the following additional rules must apply:
   1. When stored in a local file system folder, github repo, zenodo deposition, blob storage virtual folder or similar kind, the RDF file name should match the pattern of `*.bioimage.io.yaml`, for example `my-model.bioimage.io.yaml`.
   2. When the RDF file and other files are zipped into a RDF package, it must be named as `rdf.bioimage.io.yaml`.
   

## [Model Description File Specification](./generated/bioimageio_model_spec.md)

The [`Model Resource Description File Specification`](./generated/bioimageio_model_spec.md)(`model RDF`) defines a file format for representing pretrained AI models in [YAML format](https://en.wikipedia.org/wiki/YAML). This format is used to describe models hosted on the [BioImage.IO](https://bioimage.io) model repository site.

### Model Description File Examples
 - [UNet 2D Nuclei Broad](https://github.com/bioimage-io/pytorch-bioimage-io/blob/master/specs/models/unet2d_nuclei_broad/UNet2DNucleiBroad.model.yaml).


## [Generic Resource Description File Specification](./bioimageio_rdf_spec.md)

A BioImage.IO-compatible Resource Description File (RDF) is a YAML file with a set of specifically defined fields. 

The common fields for all the resource description files are:

| Field | Required | Definition  |
|---|---|---|
| id | required | unique identifier for the resource, you can also use a `doi` e.g. generated from [zenodo](https://zenodo.org/) |
| type | required | type of the resource, e.g. `model`, `dataset`, `application` or `notebook` |
| name  | required | name of the resource, a human-friendly name  |
| description | required | short description for the resource |
| source | recommended | url to the source of the resource |
| download_url | recommended | url to the zipped file if applicable |
| git_repo | recommended | url to the git repo  |
| license | recommended | the license name for the resource, e.g.: `MIT`  |
| tags | recommended | a list of tags  |
| covers | recommended | a list of url to the cover images (aspect ratio width/height=2/1)  |
| attachments | optional | a group of attachments, list of resources grouped by keys  |
| authors | optional | the full list of author names  |
| badges | optional | a list of badges|
| cite | optional | how to cite the resource |
| documentation | optional | url to the documentation in markdown format  |
| icon | optional | an icon for the resource  |
| links | optional | a list of linked resources, an id to other resources|
| version | optional | the version number for the resource, starting from `0.1.0`  |


## Recommendations

 * Describing AI models in the model-specific spec (i.e. [model RDF](./generated/bioimageio_model_spec.md)) instead of the generic RDF. Only fallback to the generic RDF if writing model specific RDF is not possible for some reason.
 * The RDF or package file name should not contain spaces or special characters, it should be concise, descriptive, in kebab case or camel case.
 * Due to the limitations of storage services such as Zenodo, which does not support subfolders, it is recommended to place other files in the same directory level of the RDF file and try to avoid using subdirectories.
 * Use the [model spec validator](#model-specification-validator) to verify the format
 * Store the yaml file in a version controlled Git repository (e.g. Github or Gitlab)
 * Use or upgrade to the latest format version


## BioImage.IO Spec Validator
It is recommended to use our validator to verify your models when you write it manually or develop tools for generating RDF/MDF files.

To install the spec validator, please run the following command:
<!--
TODO from pip/conda
-->
```
pip install git+https://github.com/bioimage-io/spec-bioimage-io
```

To use the spec validator, you can verify a model configuration in the [bioimage.io model format](./generated/bioimageio_model_spec.md) using the following command:
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

## Changelog
 * **0.3.2**: 
    - Change `author` and `packaged_by` fields from List[str] to List[Author] with Author consisting of a dictionary {name: '<Full name>', affiliation: '<Affiliation>', orcid: 'optional orcid id'}
    - Add `type` field to comply with other bioimage.io RDFs. Only valid value is 'model'.
    - Add optional `version` field (default 0.1.0) to keep track of model changes.
    - Add optional `id` field as a unique identifier (the use of [doi](doi.org) is encouraged).
    - Only allow `license` identifier from the [SPDX license list](https://spdx.org/licenses/).
