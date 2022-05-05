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

As a general guideline, please follow the model RDF spec to describe AI models and use the general RDF spec for other resource types including `dataset`, `application`. You will find more details about these two specifications in the following sections. Please also note that the best way to check whether your RDF file is BioImage.IO-compliant is to run the BioImage.IO Validator against it.

## [Resource Description File Specification](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/rdf_spec_latest.md)

A BioImage.IO-compatible Resource Description File (RDF) is a YAML file with a set of specifically defined fields. 

You can find detailed field definitions here: 
   - [general RDF spec 0.2.x](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/rdf_spec_0_2.md)

The specifications are also available as json schemas: 
   - [general RDF spec 0.2.x (json schema)](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/rdf_spec_0_2.json)

[Here](https://github.com/bioimage-io/spec-bioimage-io/blob/main/example_specs/rdf-examples.md) you can find some examples for using RDF to describe applications, notebooks, datasets etc.

## [Model Resource Description File Specification](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_latest.md)

Besides the general RDF spec, the [`Model Resource Description File Specification`](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_latest.md)(`model RDF`) defines a file format for representing pretrained AI models in [YAML format](https://en.wikipedia.org/wiki/YAML). This format is used to describe models hosted on the [BioImage.IO](https://bioimage.io) model repository site.

Here is a list of model RDF Examples:
 - [Model RDF Examples](https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_specs/models).


## [Collection Resource Description File Specification](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/collection_spec_latest.md)

Another specialized RDF spec, the [`Collection Resource Description File Specification`](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/collection_spec_latest.md)(`collection RDF`) defines a file format for representing collections of resources for the [BioImage.IO](https://bioimage.io) website.


## Linking resource items

You can create links to connect resource items by adding another resource item id to the `links` field. For example, if you want to associate an applicaiton with a model, you can set the links field of the models like the following:
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

## Hosting RDFs

You can host the resource description file on one of the public git repository website, including Zenodo Github, Gitlab, Bitbucket, or Gist.
In order to make it available in https://bioimage.io, you can submit the RDF package via the uploader.


## Recommendations

 * For AI models, consider using the model-specific spec (i.e. [model RDF](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_latest.md)) instead of the general RDF. Only fallback to the general RDF if writing model specific RDF is not possible for some reason.
 * The RDF or package file name should not contain spaces or special characters, it should be concise, descriptive, in kebab case or camel case.
 * Due to the limitations of storage services such as Zenodo, which does not support subfolders, it is recommended to place other files in the same directory level of the RDF file and try to avoid using subdirectories.
 * Use the [bioimage.io spec validator](#bioimageio-spec-validator) to verify your YAML file
 * Store the yaml file in a version controlled Git repository (e.g. Github or Gitlab)
 * Use or upgrade to the latest format version
 

# bioimageio command-line interface (CLI) 
The BioImage.IO command line tool makes it easy to work with BioImage.IO RDFs. 
A basic version of it, documented here, is provided by the [bioimageio.spec package](bioimageio-python-package), which is extended by the [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python) package.


## validate

It is recommended to use this validator to verify your models when you write it manually or develop tools for generating RDF files.


Use the `validate` command to check for formatting errors like missing or invalid values:
```
bioimageio validate <MY-MODEL-SOURCE>
```

`<MY-MODEL-SOURCE>` may be a local RDF yaml "`<MY-MODEL>/rdf.yaml`" or a DOI / URL to a zenodo record, or a URL to an rdf.yaml file.

To see if your model is compatible to the [latest bioimage.io model format](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_latest.md) use the spec validator with the `--update-format` flag:
```
bioimageio validate --update-format `<MY-MODEL-SOURCE>`
```

The output of the `validate` command will indicate missing or invalid fields in the model file. For example, if the field `timestamp` was missing it would print the following:
```
{'timestamp': ['Missing data for required field.']}
```
or if the field `test_inputs` does not contain a list, it would print:
```
{'test_inputs': ['Not a valid list.']}.
```

## update-format
Similar to the `validate` command with `--update-format` flag the `update-format` command attempts to convert an RDF 
to the latest applicable format version, but saves the result in a file for further manual editing:
```
bioimageio update-format <MY-MODEL-SOURCE> <OUTPUT-PATH>
```

# bioimageio.spec Python package
The bioimageio.spec package allows to work with BioImage.IO RDFs within Python.
The commands on which the bioimageio CLI is based can be used as functions.
Additionally, IO functions are provided to work with BioImage.IO RDFs as 'raw nodes' Python objects, e.g. the raw representation of a model RDF 0.4 at [bioimageio.spec.model.v0_4.raw_nodes](bioimageio/spec/model/v0_4/raw_nodes.py#L122-L140).
The [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python) package extends this 'raw' representation for more convenience.

[//]: # (TODO: documentation for bioimageio.spec)


## installation
bioimageio.spec can be installed with either `pip` or `conda`:

```
# pip
pip install -U bioimageio.spec

# conda
conda install -c conda-forge bioimageio.spec
```

As a dependency it is included in [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python#installation) library, which extends bioimageio.spec with more powerful commands like 'predict'. 

## Environment variables

| Name | Default | Description |
|---|---|---|
| BIOIMAGEIO_USE_CACHE | "true" | Enables simple URL to file cache. possible, case-insensitive, positive values are: "true", "yes", "1". Any other value is interpreted as "false" |
| BIOIMAGEIO_CACHE_PATH | generated tmp folder  | File path for simple URL to file cache; changes of URL source are not detected. |
| BIOIMAGEIO_CACHE_WARNINGS_LIMIT | "3" | Maximum number of warnings generated for simple cache hits. |

## Changelog
#### bioimageio.spec 0.5.4.post13
- new bioimageio.spec.partner module adding validate-partner-collection command if optional 'lxml' dependency is available

#### bioimageio.spec 0.5.4.post12
- new env var `BIOIMAGEIO_CACHE_WARNINGS_LIMIT` (default: 3) to avoid spam from cache hit warnings
- more robust conversion of ImportableSourceFile for absolute paths to relative paths (don't fail on non-path source file)
 
#### bioimageio.spec 0.5.4.post11
- resolve symlinks when transforming absolute to relative paths during serialization; see [#438](https://github.com/bioimage-io/spec-bioimage-io/pull/438)

#### bioimageio.spec 0.5.4.post10
- fix loading of collection RDF with id (id used to be ignored)

#### bioimageio.spec 0.5.4.post9
- support loading bioimageio resources by their animal nickname (currently only models have nicknames).

#### bioimageio.spec 0.5.4.post8
- any field previously expecting a local relative path is now also accepting an absolute path
- load_raw_resource_description returns a raw resource description which has no relative paths (any relative paths are converted to absolute paths).

#### bioimageio.spec 0.4.4post7
- add command `commands.update_rdf()`/`update-rdf`(cli)

#### bioimageio.spec 0.4.4post2
- fix unresolved ImportableSourceFile

#### bioimageio.spec 0.4.4post1
- fix collection RDF conversion for type field

#### bioimageio.spec 0.4.3post1
- fix to shape validation for model RDF 0.4: output shape now needs to be bigger than halo
- moved objects from bioimageio.spec.shared.utils to bioimageio.spec.shared\[.node_transformer\]
- additional keys to validation summary: bioimageio_spec_version, status 

#### bioimageio.spec 0.4.2post4
- fixes to general RDF:
  - ignore value of field `root_path` if present in yaml. This field is used internally and always present in RDF nodes.

#### bioimageio.spec 0.4.1.post5
- fixes to collection RDF: 
  - RDFs specified directly in collection RDF are validated correctly even if their source field does not point to an RDF.
  - nesting of collection RDF allowed

#### bioimageio.spec 0.4.1.post4
- fixed missing field `icon` in general RDF's raw node
- fixes to collection RDF: 
  - RDFs specified directly in collection RDF are validated correctly
  - no nesting of collection RDF allowed for now
  - `links` is no longer an explicit collection entry field ("moved" to unknown)

#### bioimageio.spec 0.4.1.post0
- new model spec 0.3.5 and 0.4.1

#### bioimageio.spec 0.4.0.post3
- `load_raw_resource_description` no longer accepts `update_to_current_format` kwarg (use `update_to_format` instead)

#### bioimageio.spec 0.4.0.post2
- `load_raw_resource_description` accepts `update_to_format` kwarg


### RDF Format Versions
#### model RDF 0.4.5
- Breaking changes that are fully auto-convertible
  - `parent` field changed to hold a string that is a BioImage.IO ID, a URL or a local relative path (and not subfields `uri` and `sha256`)

#### model RDF 0.4.4
- Non-breaking changes
  - new optional field `training_data`

#### dataset RDF 0.2.2
- Non-breaking changes
  - explicitly define and document dataset RDF (for now, clone of general RDF with type="dataset")

#### model RDF 0.4.3
- Non-breaking changes
  - add optional field `download_url`
  - add optional field `dependencies` to all weight formats (not only pytorch_state_dict)
  - add optional `pytorch_version` to the pytorch_state_dict and torchscript weight formats 

#### model RDF 0.4.2
- Bug fixes:
  - in a `pytorch_state_dict` weight entry `architecture` is no longer optional.

#### collection RDF 0.2.2
- Non-breaking changes
  - make `authors`, `cite`, `documentation` and `tags` optional
- Breaking changes that are fully auto-convertible
  - Simplifies collection RDF 0.2.1 by merging resource type fields together to a `collection` field, 
    holindg a list of all resources in the specified collection.

#### (general) RDF 0.2.2 / model RDF 0.3.6 / model RDF 0.4.2
- Non-breaking changes
  - `rdf_source` new optional field
  - `id` new optional field

#### collection RDF 0.2.1
- First official release, extends general RDF with fields `application`, `model`, `dataset`, `notebook` and (nested) 
  `collection`, which hold lists linking to respective resources.

#### (general) RDF 0.2.1
- Non-breaking changes
  - add optional `email` and `github_user` fields to entries in `authors`
  - add optional `maintainers` field (entries like in `authors` but  `github_user` is required (and `name` is not))

#### model RDF 0.4.1
- Breaking changes that are fully auto-convertible
  - moved field `dependencies` to `weights:pytorch_state_dict:dependencies`
- Non-breaking changes
  - `documentation` field accepts URLs as well

#### model RDF 0.3.5
- Non-breaking changes
  - `documentation` field accepts URLs as well

#### model RDF 0.4.0
- Breaking changes
  - model inputs and outputs may not use duplicated names.
  - model field `sha256` is required if `pytorch_state_dict` weights are defined. 
    and is now moved to the `pytroch_state_dict` entry as `architecture_sha256`.
- Breaking changes that are fully auto-convertible
  - model fields language and framework are removed.
  - model field `source` is renamed `architecture` and is moved together with `kwargs` to the `pytorch_state_dict` 
    weights entry (if it exists, otherwise they are removed).
  - the weight format `pytorch_script` was renamed to `torchscript`.
- Other changes
  - model inputs (like outputs) may be defined by `scale`ing and `offset`ing a `reference_tensor`
  - a `maintainers` field was added to the model RDF.
  - the entries in the `authors` field may now additionally contain `email` or `github_user`.
  - the summary returned by the `validate` command now also contains a list of warnings.
  - an `update_format` command was added to aid with updating older RDFs by applying auto-conversion.

#### model RDF 0.3.4
- Non-breaking changes
   - Add optional parameter `eps` to `scale_range` postprocessing. 

#### model RDF 0.3.3
- Breaking changes that are fully auto-convertible
  - `reference_input` for implicit output tensor shape was renamed to `reference_tensor`

#### model RDF 0.3.2 
- Breaking changes
  - The RDF file name in a package should be `rdf.yaml` for all the RDF (not `model.yaml`);
  - Change `authors` and `packaged_by` fields from List[str] to List[Author] with Author consisting of a dictionary `{name: '<Full name>', affiliation: '<Affiliation>', orcid: 'optional orcid id'}`;
  - Add a mandatory `type` field to comply with the general RDF. Only valid value is 'model' for model RDF;
  - Only allow `license` identifier from the [SPDX license list](https://spdx.org/licenses/);
- Other changes
  - Add optional `version` field (default 0.1.0) to keep track of model changes;
  - Allow the values in the `attachments` list to be any values besides URI;
  
