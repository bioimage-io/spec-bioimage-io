![License](https://img.shields.io/github/license/bioimage-io/spec-bioimage-io.svg)
![PyPI](https://img.shields.io/pypi/v/bioimageio-spec.svg?style=popout)
![conda-version](https://anaconda.org/conda-forge/bioimageio.spec/badges/version.svg)

# Specifications for bioimage.io

This repository contains specifications defined by the bioimage.io community. These specifications are used for defining fields in YAML files which we called `Resource Description Files` or `RDF`. The RDFs can be downloaded or uploaded to the [bioimage.io website](https://bioimage.io), produced or consumed by bioimage.io-compatible consumers(e.g. image analysis software or other website). Currently we defined two types of RDFs: a dedicated RDF specification for AI models (i.e. `model description`) and a generic description specification. The model description is a RDF with additional fields that specifically designed for describing AI models.

All the bioimage.io-compatible RDF must fulfill the following rules:

* Must be a YAML file encoded as UTF-8; If yaml syntax version is not specified to be 1.1 in the first line by `% YAML 1.1` it must be equivalent in yaml 1.1 and yaml 1.2. For differences see <https://yaml.readthedocs.io/en/latest/pyyaml.html#differences-with-pyyaml>.
* The RDF file extension must be `.yaml` (not `.yml`)
* The RDF file can be saved in a folder (or virtual folder) or in a zip package, the following additional rules must apply:
   1. When stored in a local file system folder, github repo, zenodo deposition, blob storage virtual folder or similar kind, the RDF file name should match the pattern of `*.rdf.yaml`, for example `my-model.rdf.yaml`.
   2. When the RDF file and other files are zipped into a RDF package, it must be named as `rdf.yaml`.

As a general guideline, please follow the model description spec to describe AI models and use the generic description spec for other resource types including `dataset`, `application`. You will find more details about these two specifications in the following sections. Please also note that the best way to check whether your RDF file is bioimage.io-compliant is to run the bioimage.io validator against it.

## Resource Description Specification

A bioimage.io-compatible Resource Description File (RDF) is a YAML file with a set of specifically defined fields.

You can find detailed field definitions here:

* [generic description (latest)](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/generic_spec_latest.md)
* [generic description (0.2.x)](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/generic_spec_0_2.md)

The specifications are also available as json schemas:

* [generic description (0.2.x, json schema)](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/generic_spec_0_2.json)

[Here](https://github.com/bioimage-io/spec-bioimage-io/blob/main/example_specs/rdf-examples.md) you can find some examples for using RDFs to describe applications, notebooks, datasets etc.

## Model Description Specification

Besides the generic description spec, the `model description spec` defines a file format for representing pretrained AI models in [YAML format](https://en.wikipedia.org/wiki/YAML). This format is used to describe models hosted on the [bioimage.io](https://bioimage.io) model repository site.

You can find the latest `model description` here:

* [model description spec (latest)](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_latest.md)

Here is a list of model description Examples:

* [Model RDF Examples](https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_specs/models).

## Collection Specification

The [`Collection Description Specification`](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/collection_spec_latest.md)(`collection description`) defines a file format for representing collections of resources for the [bioimage.io](https://bioimage.io) website.

You can find the latest `collection description` here:

* [collection description spec (latest)](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/collection_spec_latest.md)

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

## 🖧 Hosting RDFs

In order to make a resource description file (RDF) available on <https://bioimage.io>, you can use the [bioimage.io uploader](https://bioimage.io/#/upload/), which assists you in uploading it and any associated files to [Zenodo](https://zenodo.org/).
Alternatively you can upload directly to [Zenodo](https://zenodo.org/). In this case keep in mind to create an `rdf.yaml` file and add the keyword `bioimage.io` to your zenodo record for our CI to discover it.

## 💁 Recommendations

* For AI models, consider using the model-specific spec (i.e. [model description](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_latest.md)) instead of the generic description. Only fallback to the generic description if writing model specific RDF is not possible for some reason.
* The RDF or package file name should not contain spaces or special characters, it should be concise, descriptive, in kebab case or camel case.
* Due to the limitations of storage services such as Zenodo, which does not support subfolders, it is recommended to place other files in the same directory level of the RDF file and try to avoid using subdirectories.
* Use the [bioimage.io spec validator](#bioimageio-spec-validator) to verify your YAML file
* Store the yaml file in a version controlled Git repository (e.g. Github or Gitlab)
* Use or upgrade to the latest format version

# ⌨ bioimageio command-line interface (CLI)

The bioimage.io command line tool makes it easy to work with bioimage.io RDFs.
A basic version of it, documented here, is provided by the [bioimageio.spec package](bioimageio-python-package), which is extended by the [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python) package.

## 🧪 validate

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

# bioimageio.spec and bioimageio.core Python package

The bioimageio.spec package allows to represent bioimage.io RDFs in Python.
The [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python) package extends bioimageio.spec by providing a CLI and an extended API.

note: The CLI has moved entirely to [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python).

## 🖥 Installation

bioimageio.spec can be installed with either `pip` or `conda`, we recommend to install `bioimageio.core` instead:

```console
pip install -U bioimageio.core
```

or

```console
conda install -c conda-forge bioimageio.core
```

## Δ Changelog

### bioimageio.spec Python package

<details>
<summary></summary>
#### bioimageio.spec 0.5.0
- various API changes
- switch from Marshmallow to Pydantic

#### bioimageio.spec 0.4.9

* small bugixes

* better type hints
* improved tests

#### bioimageio.spec 0.4.8post1

* add `axes` and `eps` to `scale_mean_var`

#### bioimageio.spec 0.4.7post1

* add simple forward compatibility by treating future format versions as latest known (for the respective resource type)

#### bioimageio.spec 0.4.6post3

* Make CLI output more readable

* find redirected URLs when checking for URL availability

#### bioimageio.spec 0.4.6post2

* Improve error message for non-existing RDF file path given as string

* Improve documentation for model description's `documentation` field

#### bioimageio.spec 0.4.6post1

* fix enrich_partial_rdf_with_imjoy_plugin (see <https://github.com/bioimage-io/spec-bioimage-io/pull/452>)

#### bioimageio.spec 0.4.5post16

* fix rdf_update of entries in `resolve_collection_entries()`

#### bioimageio.spec 0.4.5post15

* pass root to `enrich_partial_rdf` arg of `resolve_collection_entries()`

#### bioimageio.spec 0.4.5post14

* keep `ResourceDescrption.root_path` as URI for remote resources. This fixes the collection description as the collection entries are resolved after the collection description has been loaded.

#### bioimageio.spec 0.4.5post13

* new bioimageio.spec.partner module adding validate-partner-collection command if optional 'lxml' dependency is available

#### bioimageio.spec 0.4.5post12

* new env var `BIOIMAGEIO_CACHE_WARNINGS_LIMIT` (default: 3) to avoid spam from cache hit warnings

* more robust conversion of ImportableSourceFile for absolute paths to relative paths (don't fail on non-path source file)

#### bioimageio.spec 0.4.5post11

* resolve symlinks when transforming absolute to relative paths during serialization; see [#438](https://github.com/bioimage-io/spec-bioimage-io/pull/438)

#### bioimageio.spec 0.4.5post10

* fix loading of collection description with id (id used to be ignored)

#### bioimageio.spec 0.4.5post9

* support loading bioimageio resources by their animal nickname (currently only models have nicknames).

#### bioimageio.spec 0.4.5post8

* any field previously expecting a local relative path is now also accepting an absolute path

* load_raw_resource_description returns a raw resource description which has no relative paths (any relative paths are converted to absolute paths).

#### bioimageio.spec 0.4.4post7

* add command `commands.update_rdf()`/`update-rdf`(cli)

#### bioimageio.spec 0.4.4post2

* fix unresolved ImportableSourceFile

#### bioimageio.spec 0.4.4post1

* fix collection description conversion for type field

#### bioimageio.spec 0.4.3post1

* fix to shape validation for model description 0.4: output shape now needs to be bigger than halo

* moved objects from bioimageio.spec.shared.utils to bioimageio.spec.shared\[.node_transformer\]
* additional keys to validation summary: bioimageio_spec_version, status

#### bioimageio.spec 0.4.2post4

* fixes to generic description:
  * ignore value of field `root_path` if present in yaml. This field is used internally and always present in RDF nodes.

#### bioimageio.spec 0.4.1.post5

* fixes to collection description:
  * RDFs specified directly in collection description are validated correctly even if their source field does not point to an RDF.
  * nesting of collection description allowed

#### bioimageio.spec 0.4.1.post4

* fixed missing field `icon` in generic description's raw node

* fixes to collection description:
  * RDFs specified directly in collection description are validated correctly
  * no nesting of collection description allowed for now
  * `links` is no longer an explicit collection entry field ("moved" to unknown)

#### bioimageio.spec 0.4.1.post0

* new model spec 0.3.5 and 0.4.1

#### bioimageio.spec 0.4.0.post3

* `load_raw_resource_description` no longer accepts `update_to_current_format` kwarg (use `update_to_format` instead)

#### bioimageio.spec 0.4.0.post2

* `load_raw_resource_description` accepts `update_to_format` kwarg

</details>

<details>
<summary>### Resource Description Format Versions</summary>
#### application 0.3.0 / collection 0.3.0 / dataset 0.3.0 / generic 0.3.0 / notebook 0.3.0
todo: format version updates

#### model 0.5.0

* all generic 0.3.0 changes +
* Breaking canges that are fully auto-convertible
  * rename `weights.pytorch_state_dict.architecture.source_file` to `...architecture.file`
  * rename `inputs[i].name` to `inputs[i].id`
  * rename `outputs[i].name` to `outputs[i].id`
  * rename `inputs[i].preprocessing.name` to `inputs[i].preprocessing.id`
  * rename `outputs[i].postprocessing.name` to `outputs[i].postprocessing.id`

#### model 0.4.9

* Non-breaking changes
  * make pre-/postprocessing kwargs `mode` and `axes` always optional for model description 0.3 and 0.4

#### model 0.4.8

* Non-breaking changes
  * `cite` field is now optional

#### generic 0.2.2 and model 0.4.7

* Breaking changes that are fully auto-convertible
  * name field may not include '/' or '\' (conversion removes these)

#### model 0.4.6

* Non-breaking changes
  * Implicit output shape can be expanded by inserting `null` into `shape:scale` and indicating length of new dimension D in the `offset` field. Keep in mind that `D=2*'offset'`.

#### model 0.4.5

* Breaking changes that are fully auto-convertible
  * `parent` field changed to hold a string that is a bioimage.io ID, a URL or a local relative path (and not subfields `uri` and `sha256`)

#### model 0.4.4

* Non-breaking changes
  * new optional field `training_data`

#### dataset 0.2.2

* Non-breaking changes
  * explicitly define and document dataset description (for now, clone of generic description with type="dataset")

#### model 0.4.3

* Non-breaking changes
  * add optional field `download_url`
  * add optional field `dependencies` to all weight formats (not only pytorch_state_dict)
  * add optional `pytorch_version` to the pytorch_state_dict and torchscript weight formats

#### model 0.4.2

* Bug fixes:
  * in a `pytorch_state_dict` weight entry `architecture` is no longer optional.

#### collection 0.2.2

* Non-breaking changes
  * make `authors`, `cite`, `documentation` and `tags` optional

* Breaking changes that are fully auto-convertible
  * Simplifies collection description 0.2.1 by merging resource type fields together to a `collection` field,
    holindg a list of all resources in the specified collection.

#### generic 0.2.2 / model 0.3.6 / model 0.4.2

* Non-breaking changes
  * `rdf_source` new optional field
  * `id` new optional field

#### collection 0.2.1

* First official release, extends generic description with fields `application`, `model`, `dataset`, `notebook` and (nested)
  `collection`, which hold lists linking to respective resources.

#### generic 0.2.1

* Non-breaking changes
  * add optional `email` and `github_user` fields to entries in `authors`
  * add optional `maintainers` field (entries like in `authors` but  `github_user` is required (and `name` is not))

#### model 0.4.1

* Breaking changes that are fully auto-convertible
  * moved field `dependencies` to `weights:pytorch_state_dict:dependencies`

* Non-breaking changes
  * `documentation` field accepts URLs as well

#### model 0.3.5

* Non-breaking changes
  * `documentation` field accepts URLs as well

#### model 0.4.0

* Breaking changes
  * model inputs and outputs may not use duplicated names.
  * model field `sha256` is required if `pytorch_state_dict` weights are defined.
    and is now moved to the `pytroch_state_dict` entry as `architecture_sha256`.

* Breaking changes that are fully auto-convertible
  * model fields language and framework are removed.
  * model field `source` is renamed `architecture` and is moved together with `kwargs` to the `pytorch_state_dict`
    weights entry (if it exists, otherwise they are removed).
  * the weight format `pytorch_script` was renamed to `torchscript`.
* Other changes
  * model inputs (like outputs) may be defined by `scale`ing and `offset`ing a `reference_tensor`
  * a `maintainers` field was added to the model description.
  * the entries in the `authors` field may now additionally contain `email` or `github_user`.
  * the summary returned by the `validate` command now also contains a list of warnings.
  * an `update_format` command was added to aid with updating older RDFs by applying auto-conversion.

#### model 0.3.4

* Non-breaking changes
  * Add optional parameter `eps` to `scale_range` postprocessing.

#### model 0.3.3

* Breaking changes that are fully auto-convertible
  * `reference_input` for implicit output tensor shape was renamed to `reference_tensor`

#### model 0.3.2

* Breaking changes
  * The RDF file name in a package should be `rdf.yaml` for all the RDF (not `model.yaml`);
  * Change `authors` and `packaged_by` fields from List[str] to List[Author] with Author consisting of a dictionary `{name: '<Full name>', affiliation: '<Affiliation>', orcid: 'optional orcid id'}`;
  * Add a mandatory `type` field to comply with the generic description. Only valid value is 'model' for model description;
  * Only allow `license` identifier from the [SPDX license list](https://spdx.org/licenses/);

* Other changes
  * Add optional `version` field (default 0.1.0) to keep track of model changes;
  * Allow the values in the `attachments` list to be any values besides URI;

</details>

<details>
<summary>### Model Description Format Versions</summary>
#### model 0.4.9
- Non-breaking changes
  - make pre-/postprocessing kwargs `mode` and `axes` always optional for model description 0.3 and 0.4

#### model 0.4.8

* Non-breaking changes
  * `cite` field is now optional

#### RDF 0.2.2 and model 0.4.7

* Breaking changes that are fully auto-convertible
  * name field may not include '/' or '\' (conversion removes these)

#### model 0.4.6

* Non-breaking changes
  * Implicit output shape can be expanded by inserting `null` into `shape:scale` and indicating length of new dimension D in the `offset` field. Keep in mind that `D=2*'offset'`.

#### model 0.4.5

* Breaking changes that are fully auto-convertible
  * `parent` field changed to hold a string that is a bioimage.io ID, a URL or a local relative path (and not subfields `uri` and `sha256`)

#### model 0.4.4

* Non-breaking changes
  * new optional field `training_data`

#### dataset 0.2.2

* Non-breaking changes
  * explicitly define and document dataset description (for now, clone of generic description with type="dataset")

#### model 0.4.3

* Non-breaking changes
  * add optional field `download_url`
  * add optional field `dependencies` to all weight formats (not only pytorch_state_dict)
  * add optional `pytorch_version` to the pytorch_state_dict and torchscript weight formats

#### model 0.4.2

* Bug fixes:
  * in a `pytorch_state_dict` weight entry `architecture` is no longer optional.

#### collection 0.2.2

* Non-breaking changes
  * make `authors`, `cite`, `documentation` and `tags` optional

* Breaking changes that are fully auto-convertible
  * Simplifies collection description 0.2.1 by merging resource type fields together to a `collection` field,
    holindg a list of all resources in the specified collection.

#### generic 0.2.2 / model 0.3.6 / model 0.4.2

* Non-breaking changes
  * `rdf_source` new optional field
  * `id` new optional field

#### collection 0.2.1

* First official release, extends generic description with fields `application`, `model`, `dataset`, `notebook` and (nested)
  `collection`, which hold lists linking to respective resources.

#### generic 0.2.1

* Non-breaking changes
  * add optional `email` and `github_user` fields to entries in `authors`
  * add optional `maintainers` field (entries like in `authors` but  `github_user` is required (and `name` is not))

</details>
