![License](https://img.shields.io/github/license/bioimage-io/spec-bioimage-io.svg)
![PyPI](https://img.shields.io/pypi/v/bioimageio-spec.svg?style=popout)
![conda-version](https://anaconda.org/conda-forge/bioimageio.spec/badges/version.svg)

# Specifications for bioimage.io

This repository contains specifications defined by the bioimage.io community. These specifications are used for defining fields in YAML 1.2 files which should be named `rdf.yaml`. Such a rdf.yaml --- along with files referenced in it --- can be downloaded from or uploaded to the [bioimage.io website](https://bioimage.io) and may be produced or consumed by bioimage.io-compatible consumers (e.g. image analysis software like ilastik).

bioimage.io-compatible resources must fulfill the following rules:

Note that the Python package PyYAML does not support YAML 1.2 .
We therefore use and recommend [ruyaml](https://ruyaml.readthedocs.io/en/latest/).
For differences see <https://ruamelyaml.readthedocs.io/en/latest/pyyaml>.

Please also note that the best way to check whether your `rdf.yaml` file is bioimage.io-compliant is to call `bioimageio.core.validate` from the [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python) Python package.
The [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python) Python package also provides the bioimageio command line interface (CLI) with the `validate` command:

```terminal
bioimageio validate path/to/your/rdf.yaml
```

## Format version overview

All bioimage.io description formats are defined as [Pydantic models](https://docs.pydantic.dev/latest/).

| type | format version | documentation |
| --- | --- | --- |
| model | 0.5 </br> 0.4 | [model_spec_v0-5.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_v0-5.md) </br> [model_spec_v0-4.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/model_spec_v0-4.md) |
| dataset | 0.3 </br> 0.2 | [dataset_spec_v0-3.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/dataset_spec_v0-3.md) </br> [dataset_spec_v0-2.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/dataset_spec_v0-2.md) |
| notebook | 0.3 </br> 0.2 | [notebook_spec_v0-3.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/notebook_spec_v0-3.md) </br> [notebook_spec_v0-2.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/notebook_spec_v0-2.md) |
| application | 0.3 </br> 0.2 | [application_spec_v0-3.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/application_spec_v0-3.md) </br> [application_spec_v0-2.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/application_spec_v0-2.md) |
| collection | 0.3 </br> 0.2 | [collection_spec_v0-3.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/collection_spec_v0-3.md) </br> [collection_spec_v0-2.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/collection_spec_v0-2.md) |
| generic | 0.3 </br> 0.2 | [generic_spec_v0-3.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/generic_spec_v0-3.md) </br> [generic_spec_v0-2.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/generic_spec_v0-2.md) |

## JSON schema

Simplified descriptions are available as [JSON schema](https://json-schema.org/):

| bioimageio.spec version | JSON schema |
| --- | --- |
| latest | [bioimageio_schema_latest.json](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/bioimageio_schema_latest.json) |
| 0.5 | [bioimageio_schema_v0-5.json](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/bioimageio_schema_v0-5.json) |

These are primarily intended for syntax highlighting and form generation.

## Examples

We provide some [examples for using rdf.yaml files to describe models, applications, notebooks and datasets](https://github.com/bioimage-io/spec-bioimage-io/blob/main/example_descriptions/examples.md).

## 💁 Recommendations

* Due to the limitations of storage services such as Zenodo, which does not support subfolders, it is recommended to place other files in the same directory level of the `rdf.yaml` file and try to avoid using subdirectories.
* Use the [bioimageio.core Python package](https://github.com/bioimage-io/core-bioimage-io-python) to validate your `rdf.yaml` file.
* bioimageio.spec keeps evolving. Try to use and upgrade to the most current format version!

## ⌨ bioimageio command-line interface (CLI)

The bioimageio CLI has moved entirely to [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python).

## 🖥 Installation

bioimageio.spec can be installed with either `conda` or `pip`, we recommend to install `bioimageio.core` instead:

```console
conda install -c conda-forge bioimageio.core
```

or

```console
pip install -U bioimageio.core
```

## 🤝 How to contribute

## ♥ Contributors

<a href="https://github.com/bioimage-io/spec-bioimage-io/graphs/contributors">
  <img alt="bioimageio.spec contributors" src="https://contrib.rocks/image?repo=bioimage-io/spec-bioimage-io" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

## Δ Changelog

### bioimageio.spec Python package

#### bioimageio.spec 0.5.0post2

* don't fail if CI env var is a string

#### bioimageio.spec 0.5.0post1

* fix `_internal.io_utils.identify_bioimageio_yaml_file()`

#### bioimageio.spec 0.5.0

* new description formats: [generic 0.3, application 0.3, collection 0.3, dataset 0.3, notebook 0.3](generic-030--application-030--collection-030--dataset-030--notebook-030) and [model 0.5](model-050).
* various API changes, most important functions:
  * `bioimageio.spec.load_description` (replaces `load_raw_resource_description`, interface changed)
  * `bioimageio.spec.validate_format` (new)
  * `bioimageio.spec.dump_description` (replaces `serialize_raw_resource_description_to_dict`, interface changed)
  * `bioimageio.spec.update_format` (interface changed)
* switch from Marshmallow to Pydantic
  * extended validation
  * one joint, more precise JSON schema

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

### Resource Description Format Versions

#### generic 0.3.0 / application 0.3.0 / collection 0.3.0 / dataset 0.3.0 / notebook 0.3.0

* Breaking canges that are fully auto-convertible
  * dropped `download_url`
  * dropped non-file attachments
  * `attachments.files` moved to `attachments.i.source`
* Non-breaking changes
  * added optional `parent` field

#### model 0.5.0

all generic 0.3.0 changes (except models already have the `parent` field) plus:

* Breaking changes that are partially auto-convertible
  * `inputs.i.axes` are now defined in more detail (same for `outputs.i.axes`)
  * `inputs.i.shape` moved per axes to `inputs.i.axes.size` (same for `outputs.i.shape`)
  * new pre-/postprocessing 'fixed_zero_mean_unit_variance' separated from 'zero_mean_unit_variance', where `mode=fixed` is no longer valid.
    (for scalar values this is auto-convertible.)
* Breaking changes that are fully auto-convertible
  * changes in `weights.pytorch_state_dict.architecture`
    * renamed `weights.pytorch_state_dict.architecture.source_file` to `...architecture.source`
  * changes in `weights.pytorch_state_dict.dependencies`
    * only conda environment allowed and specified by `weights.pytorch_state_dict.dependencies.source`
    * new optional field `weights.pytorch_state_dict.dependencies.sha256`
  * changes in `weights.tensorflow_model_bundle.dependencies`
    * same as changes in `weights.pytorch_state_dict.dependencies`
  * moved `test_inputs` to `inputs.i.test_tensor`
  * moved `test_outputs` to `outputs.i.test_tensor`
  * moved `sample_inputs` to `inputs.i.sample_tensor`
  * moved `sample_outputs` to `outputs.i.sample_tensor`
  * renamed `inputs.i.name` to `inputs.i.id`
  * renamed `outputs.i.name` to `outputs.i.id`
  * renamed `inputs.i.preprocessing.name` to `inputs.i.preprocessing.id`
  * renamed `outputs.i.postprocessing.name` to `outputs.i.postprocessing.id`
* Non-breaking changes:
  * new pre-/postprocessing: `id`='ensure_dtype' with kwarg `dtype`

#### generic 0.2.4 and model 0.4.10

* Breaking changes that are fully auto-convertible
  * `id` overwritten with value from `config.bioimageio.nickname` if available
* Non-breaking changes
  * `version_number` is a new, optional field indicating that an RDF is the nth published version with a given `id`
  * `id_emoji` is a new, optional field (set from `config.bioimageio.nickname_icon` if available)
  * `uploader` is a new, optional field with `email` and an optional `name` subfields

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

* Non-breaking changes
  * Add optional `version` field (default 0.1.0) to keep track of model changes;
  * Allow the values in the `attachments` list to be any values besides URI;
