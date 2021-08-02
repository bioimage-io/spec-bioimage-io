![License](https://img.shields.io/github/license/bioimage-io/spec-bioimage-io.svg)
![PyPI](https://img.shields.io/pypi/v/bioimageio-spec.svg?style=popout)
![conda-version](https://anaconda.org/conda-forge/bioimageio.spec/badges/version.svg)
# Specifications for BioImage.IO

This repository contains specifications defined by the BioImage.IO community. These specifications are used for defining fields in YAML files which we called `Resource Description Files` or `RDF`. The RDFs can be downloaded or uploaded to the [bioimage.io website](https://bioimage.io), produced or consumed by BioImage.IO-compatible consumers(e.g. image analysis software or other website). Currently we defined two types of RDFs: a dedicated RDF specification for AI models (i.e. `model RDF`) and a general RDF specification. The model RDF is a RDF with additional fields that specifically designed for describing AI models.


All the BioImage.IO-compatible RDF must fulfill the following rules:
 * Must be a YAML file encoded as UTF-8; If yaml syntax version is not specified to be 1.1 in the first line by `% YAML 1.1` it must be equivalent in yaml 1.1 and yaml 1.2. For differences see https://yaml.readthedocs.io/en/latest/pyyaml.html#differences-with-pyyaml.
 * The RDF file extension must be `.yaml` (not `.yml`)
 * The RDF file can be saved in a folder (or virtual folder) or in a zip package, the following additional rules must apply:
   1. When stored in a local file system folder, github repo, zenodo deposition, blob storage virtual folder or similar kind, the RDF file name should match the pattern of `*.rdf.yaml`, for example `my-model.rdf.yaml`.
   2. When the RDF file and other files are zipped into a RDF package, it must be named as `rdf.yaml`.

As a general guideline, please follow the model RDF spec to describe AI models and use the general RDF spec for other resource types including `dataset`, `notebook`, `application`. You will find more details about these two specifications in the following sections. Please also note that the best way to check whether your RDF file is BioImage.IO-compliant is to run the BioImage.IO Validator against it.

## [Resource Description File Specification](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/rdf_spec_latest.md)

A BioImage.IO-compatible Resource Description File (RDF) is a YAML file with a set of specifically defined fields. 

You can find detailed field definitions here: 
   - [general RDF spec 0.2.x](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/rdf_spec_0_2.md)

The specifications are also available as json schemas: 
   - [general RDF spec 0.2.x (json schema)](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/rdf_spec_0_2.json)


### Describing applications
The RDF can be used to describe applications. To do so set the `type` field to `application`.\
For regular software package with a downloadable file, you can set `download_url` to the downloadable file, for example, you can upload the executable files as Github release, deposit it on Zenodo, or even generate a sharable url from Dropbox/Google Drive.\
For web application, set `source` to the url of the web application. Users can then click and redirect to your web application. However, simple integration will not support features such as opening dataset or models with your application.

It is recommended to build BioEngine Apps such that users can directly try and use them in BioImage.IO. See [here](https://github.com/bioimage-io/bioimage.io/blob/main/docs/bioengine_apps/build-bioengine-apps.md) for more details.\
Below is an example for [Kaibu](https://kaibu.org), which is a BioEngine/ImJoy compatible web application:
```yaml
id: kaibu
name: Kaibu
description: Kaibu--a web application for visualizing and annotating multi-dimensional images
covers:
 # use the `raw` url if you store the image on github
 - https://raw.githubusercontent.com/imjoy-team/kaibu/master/public/static/img/kaibu-screenshot-1.png

# source url to kaibu.org
source: https://kaibu.org
# add custom badge
badge:
 - icon: https://imjoy.io/static/badge/launch-imjoy-badge.svg
   label: Launch ImJoy
   url: https://imjoy.io/#/app?plugin=https://kaibu.org/#/app
```
For more application examples, see the [manifest for ImJoy](https://github.com/imjoy-team/bioimage-io-models/blob/master/manifest.bioimage.io.yaml).

### Describing datasets, notebooks and other types
The RDF allows for the description of datasets (type=`dataset`), notebooks (type=`notebook`) and other potential resources, you can use set `source` and/or `download_url` to point to the resource, or use `attachments` to specify a list of associated files.

For examples, see entries `dataset`/`notebook` in the [ZeroCostDL4Mic](https://github.com/HenriquesLab/ZeroCostDL4Mic/blob/master/manifest.bioimage.io.yaml) collection.


### Describing models with the unspecific RDF(not recommended, use the Model RDF instead)
In general, it is discouraged to use the general RDF to describe AI models and we recommend to follow the [model RDF spec](#model-resource-description-file-specification) instead. However, in some cases, it is not possible to provide detailed fields defined in the [model RDF spec](#model-resource-description-file-specification), the general RDF can be used for discribing AI models.
To do that, you need to first set the `type` field to `model`.\
A basic integration would be simply provide a `download_url` to a zip file (for example, with the model weights, source code or executable binary file) hosted on Github releases, Dropbox, Google Drive etc. For example: 
```yaml
download_url: https://zenodo.org/record/3446812/files/unet2d_weights.torch?download=1
```

If the model is available as a github repo, then provide the `git_repo` field:
```yaml
git_repo: https://github.com/my/model...
```

Here an example of a general RDF describing a model (not recommended): 
https://github.com/CellProfiling/HPA-model-zoo/blob/2f668d87defddc6c7cd156259a8be4146b665e72/manifest.bioimage.io.yaml#L33-L59 


## [Model Resource Description File Specification](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_latest.md)

Besides the general RDF spec, the [`Model Resource Description File Specification`](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_latest.md)(`model RDF`) defines a file format for representing pretrained AI models in [YAML format](https://en.wikipedia.org/wiki/YAML). This format is used to describe models hosted on the [BioImage.IO](https://bioimage.io) model repository site.

Here is a list of model RDF Examples:
 - [UNet 2D Nuclei Broad](https://github.com/bioimage-io/pytorch-bioimage-io/blob/master/specs/models/unet2d_nuclei_broad/UNet2DNucleiBroad.model.yaml).


## Link between resource items (under development)

You can use `links` which is a list of `id` to other resource items, for example, if you want to associate an applicaiton with a model, you can set the links field of the models like the following:
```yaml
application:
  - id: HPA-Classification
    source: https://raw.githubusercontent.com/bioimage-io/tfjs-bioimage-io/master/apps/HPA-Classification.imjoy.html

model:
  - id: HPAShuffleNetV2
    source: https://raw.githubusercontent.com/bioimage-io/tfjs-bioimage-io/master/models/HPAShuffleNetV2/HPAShuffleNetV2.model.yaml
    links:
      - HPA-Classification
```

## Hosting the file (under development)
It is recommended to host the resource description file on one of the public git repository website, including Github, Gitlab, Bitbucket, or Gist. A link can be submitted to BioImage.IO so we can keep track of the changes later.


## Recommendations

 * For AI models, consider using the model-specific spec (i.e. [model RDF](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_latest.md)) instead of the general RDF. Only fallback to the general RDF if writing model specific RDF is not possible for some reason.
 * The RDF or package file name should not contain spaces or special characters, it should be concise, descriptive, in kebab case or camel case.
 * Due to the limitations of storage services such as Zenodo, which does not support subfolders, it is recommended to place other files in the same directory level of the RDF file and try to avoid using subdirectories.
 * Use the [bioimage.io spec validator](#bioimageio-spec-validator) to verify your YAML file
 * Store the yaml file in a version controlled Git repository (e.g. Github or Gitlab)
 * Use or upgrade to the latest format version


## BioImage.IO Spec Validator

It is recommended to use our validator to verify your models when you write it manually or develop tools for generating RDF/MDF files.

The spec validator can be installed either with `pip`, or `conda`:
```
# pip
pip install -U bioimageio.spec

# conda
conda install -c conda-forge bioimageio.spec
```

To use the spec validator, you can verify a model configuration in the [bioimage.io model format](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_latest.md) using the following command:
```
python -m bioimageio.spec validate <MY-MODEL>.yaml

# alternatively using the entry-point:
bioimageio validate <MY-MODEL>.yaml
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
    - Breaking changes
      - The RDF file name in a package should be `rdf.yaml` for all the RDF (not `model.yaml`);
      - Change `authors` and `packaged_by` fields from List[str] to List[Author] with Author consisting of a dictionary `{name: '<Full name>', affiliation: '<Affiliation>', orcid: 'optional orcid id'}`;
      - Add a mandatory `type` field to comply with the general RDF. Only valid value is 'model' for model RDF;
      - Only allow `license` identifier from the [SPDX license list](https://spdx.org/licenses/);
    - Other changes
      - Add optional `version` field (default 0.1.0) to keep track of model changes;
      - Allow the values in the `attachments` list to be any values besides URI;
