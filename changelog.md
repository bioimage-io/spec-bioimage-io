## Changelog

The bioimageio.spec Python package defines a type specific, versioned resource description format.
In this file we log both:

- [Changes to the bioimageio.spec Python package](#changes-to-the-bioimageiospec-python-package)
- [Changes to the Resource Description Format](#changes-to-the-resource-description-format)

### Changes to the bioimageio.spec Python package

This changelog includes implementation details and my reference the [changes to the Resource Description Format](#changes-to-the-resource-description-format), e.g. in entry [bioimageio.spec 0.5.2](#bioimageiospec-052).

#### bioimageio.spec 0.5.4.4

- infinity and not-a-number values are no longer allowed (when used in a tensor description under data.range they are replaced with `None`)
- stricter validation of integers; float values no longer allowed for input/output fields `size.offset`, `size.min`, `size.max`

#### bioimageio.spec 0.5.4.3

- fix root determination of cacheless downloads of non-zip files
- use httpx instead of requests
- improved caching with genericache (thanks @Tomaz-Vieira !)
- enable pretty validation errors in ipython at import time (deprecates `enable_pretty_validation_errors_in_ipynb()`)

#### bioimageio.spec 0.5.4.2

- improved validation summary formatting
- new validation context `disable_cache` (equivalent to an empty `cache_path` in `settings`)
  circumvents caching to disk and keeps downloads in memory only
- new setting `allow_pickle` to control `numpy.load`/`numpy.save` behavior
- allow the `ValidationContext`'s `known_files` to include `None` values (isntead of known SHA values) to only check for file existence without comparing file hashes.

#### bioimageio.spec 0.5.4.1

- fixed mutable default ValidationContext

#### bioimageio.spec 0.5.4.0

- [model format 0.5.4](#model-054)
- new utlity functions `update_format`, `update_hashes`
- environment for tensorflow 1 is now using tf 2.17 (to support py >=3.8)
- update conda environments (remove `cpuonly` from pytorch envs)
- bugfix: Fix wrong warning by matching a '# Validation' section within the
    documentation (not only at the start).
- bugfix: Include dependency file when packaging 0.4 models.
- experimental feature for debugging: raise validation errors with `ValidationContext.raise_errors=True`
- remove deprecated `IN_PACKAGE_MESSAGE`
- added utitlity methods `ValidationSummary.save_markdown`, `ValidationSummary.save`, `ValidationSummary.load`
- added `ValidationSummary.status` field to include new status `valid-format` (to distinguish if core tests have run or not)

#### bioimageio.spec 0.5.3.6

- fix URL validation (checking with actual http requests was erroneously skipped)

#### bioimageio.spec 0.5.3.5

- fix loading tifffile in python 3.8 (pin tifffile)
- use default tensorflow environments for Keras H5 weights

#### bioimageio.spec 0.5.3.4

- support loading and saving from/to zipfile.ZipFile objects
- fix bug when packaging with weights priority order (#638)
- add conda_env module providing helper to create recommended conda environments for model descriptions
- fix summary formatting
- improve logged origin for logged messages
- make the `model.v0_5.ModelDescr.training_data` field a `left_to_right` Union to avoid warnings
- the deprecated `version_number` is no longer appended to the `id`, but instead set as `version` if no `version` is specified.

#### bioimageio.spec 0.5.3.3

- expose `progressbar` to customize display of download progress
- expose `get_resource_package_content`
- prefer `rdf.yaml` over `bioimageio.yaml` (name `bioimageio.yaml` file `rdf.yaml` file when packaging, look for `rdf.yaml` first, etc.)
- enforce: (generic 0.3/model 0.5 spec) documentation source file encoding has to be UTF-8.
- bugfix: allow optional pre- and postprocessing to be missing in an RDF (before it required an empty dict).

#### bioimageio.spec 0.5.3.2

- bugfix "reset known files if root changes" (#619)

#### bioimageio.spec 0.5.3.1

note: the versioning scheme was changed as our previous `post` releases include changes beyond what a post release should entail (only changing docstrings, etc).
This was motivated by the desire to keep the library version in sync with the (model) format version to avoid confusion.
To keep this relation, but avoid overbearing post releases a library version number is now added as the 4th part MAJOR.MINOR.PATCH.LIB_VERSION.

- add `load_model_description` and `load_dataset_description`
- add `ensure_description_is_model` and `ensure_description_is_dataset`
- expose `perform_io_checks` and `known_files` from `ValidationContext` to `load_description` and `load_description_and_validate_format_only`

#### bioimageio.spec 0.5.3post4

- fix pinning of pydantic

#### bioimageio.spec 0.5.3post3

- update resolving of bioimage.io resource IDs

#### bioimageio.spec 0.5.3post2

- fix SHA-256 value when resolving a RDF version from the bioimage.io collection that is not the latest

#### bioimageio.spec 0.5.3post1

- bump patch version during loading for model 0.5.x
- improve validation error formatting
- validate URLs first with a head request, if forbidden, follow up with a get request that is streamed and if that is also forbidden a regular get request.
- `RelativePath.absolute()` is now a method (not a property) analog to `pathlib.Path`

#### bioimageio.spec 0.5.3

- remove collection description
- update SPDX license list
- update generic description to 0.3.1
- update model description to 0.5.3
- add timeout argument to all requests.get calls

#### bioimageio.spec 0.5.2post5

- added more information to validation summary
- deprioritize `Path` objects in the `FileSource` union

#### bioimageio.spec 0.5.2post4

- resolve backup DOIs
- fix resolving relative file paths given as strings
- allow to bypass download and hashing of known files

#### bioimageio.spec 0.5.2post3

- avoid full download when validating urls

#### bioimageio.spec 0.5.2post2

- resolve version (un)specific collection IDs, e.g. `load_description('affable-shark')`, `load_description('affable-shark/1')`

#### bioimageio.spec 0.5.2post1

- fix model packaging with weights format priority

#### bioimageio.spec 0.5.2

- new patch version [model 0.5.2](#model-052)

#### bioimageio.spec 0.5.1

- new patch version [model 0.5.1](#model-051)

#### bioimageio.spec 0.5.0post2

- don't fail if CI env var is a string

#### bioimageio.spec 0.5.0post1

- fix `_internal.io_utils.identify_bioimageio_yaml_file()`

#### bioimageio.spec 0.5.0

- new description formats: [generic 0.3, application 0.3, collection 0.3, dataset 0.3, notebook 0.3](generic-030--application-030--collection-030--dataset-030--notebook-030) and [model 0.5](model-050).
- various API changes, most important functions:
  - `bioimageio.spec.load_description` (replaces `load_raw_resource_description`, interface changed)
  - `bioimageio.spec.validate_format` (new)
  - `bioimageio.spec.dump_description` (replaces `serialize_raw_resource_description_to_dict`, interface changed)
  - `bioimageio.spec.update_format` (interface changed)
- switch from Marshmallow to Pydantic
  - extended validation
  - one joint, more precise JSON Schema

#### bioimageio.spec 0.4.9

- small bugixes
- better type hints
- improved tests

#### bioimageio.spec 0.4.8post1

- add `axes` and `eps` to `scale_mean_var`

#### bioimageio.spec 0.4.7post1

- add simple forward compatibility by treating future format versions as latest known (for the respective resource type)

#### bioimageio.spec 0.4.6post3

- Make CLI output more readable

- find redirected URLs when checking for URL availability

#### bioimageio.spec 0.4.6post2

- Improve error message for non-existing RDF file path given as string

- Improve documentation for model description's `documentation` field

#### bioimageio.spec 0.4.6post1

- fix enrich_partial_rdf_with_imjoy_plugin (see <https://github.com/bioimage-io/spec-bioimage-io/pull/452>)

#### bioimageio.spec 0.4.5post16

- fix rdf_update of entries in `resolve_collection_entries()`

#### bioimageio.spec 0.4.5post15

- pass root to `enrich_partial_rdf` arg of `resolve_collection_entries()`

#### bioimageio.spec 0.4.5post14

- keep `ResourceDescrption.root_path` as URI for remote resources. This fixes the collection description as the collection entries are resolved after the collection description has been loaded.

#### bioimageio.spec 0.4.5post13

- new bioimageio.spec.partner module adding validate-partner-collection command if optional 'lxml' dependency is available

#### bioimageio.spec 0.4.5post12

- new env var `BIOIMAGEIO_CACHE_WARNINGS_LIMIT` (default: 3) to avoid spam from cache hit warnings

- more robust conversion of ImportableSourceFile for absolute paths to relative paths (don't fail on non-path source file)

#### bioimageio.spec 0.4.5post11

- resolve symlinks when transforming absolute to relative paths during serialization; see [#438](https://github.com/bioimage-io/spec-bioimage-io/pull/438)

#### bioimageio.spec 0.4.5post10

- fix loading of collection description with id (id used to be ignored)

#### bioimageio.spec 0.4.5post9

- support loading bioimageio resources by their animal nickname (currently only models have nicknames).

#### bioimageio.spec 0.4.5post8

- any field previously expecting a local relative path is now also accepting an absolute path

- load_raw_resource_description returns a raw resource description which has no relative paths (any relative paths are converted to absolute paths).

#### bioimageio.spec 0.4.4post7

- add command `commands.update_rdf()`/`update-rdf`(cli)

#### bioimageio.spec 0.4.4post2

- fix unresolved ImportableSourceFile

#### bioimageio.spec 0.4.4post1

- fix collection description conversion for type field

#### bioimageio.spec 0.4.3post1

- fix to shape validation for model description 0.4: output shape now needs to be bigger than halo

- moved objects from bioimageio.spec.shared.utils to bioimageio.spec.shared\[.node_transformer\]
- additional keys to validation summary: bioimageio_spec_version, status

#### bioimageio.spec 0.4.2post4

- fixes to generic description:
  - ignore value of field `root_path` if present in yaml. This field is used internally and always present in RDF nodes.

#### bioimageio.spec 0.4.1.post5

- fixes to collection description:
  - RDFs specified directly in collection description are validated correctly even if their source field does not point to an RDF.
  - nesting of collection description allowed

#### bioimageio.spec 0.4.1.post4

- fixed missing field `icon` in generic description's raw node

- fixes to collection description:
  - RDFs specified directly in collection description are validated correctly
  - no nesting of collection description allowed for now
  - `links` is no longer an explicit collection entry field ("moved" to unknown)

#### bioimageio.spec 0.4.1.post0

- new model spec 0.3.5 and 0.4.1

#### bioimageio.spec 0.4.0.post3

- `load_raw_resource_description` no longer accepts `update_to_current_format` kwarg (use `update_to_format` instead)

#### bioimageio.spec 0.4.0.post2

- `load_raw_resource_description` accepts `update_to_format` kwarg

### Changes to the Resource Description Format

Which fields a resource description field has and how they are to be interpreted depends on the `type` and  `format_version` fields.
Here is a list of changes for each `type` and `format_version`.
Note that 'generic' changes apply to `type` application, dataset and notebook of the same `format_versions`.
If the changes also apply to `type` model, the coresponding model format version is noted, e.g. [generic 0.3.1 and model 0.5.3](#generic-031-and-model-053).

#### model 0.5.4

- Breaking changes (that shouldn't affect any released models though)
  - Do not allow a model to reference itself in the `parent` field
- Non-breaking changes
  - validate `config.bioimageio.reproducibility_tolerance` to store relative and absolute tolerances as well as a tolerance for mismatched elements.
  - allow `+` in name
  - new optional `comment` field for weights entries

#### generic 0.3.1 and model 0.5.3

- Non-breaking changes
  - remove `version_number` in favor of using `version`

#### model 0.5.2

- Non-breaking changes
  - added `concatenable` flag to index, time and space input axes

#### model 0.5.1

- Non-breaking changes
  - added `DataDependentSize` for `outputs.i.size` to specify an output shape that is not known before inference is run.
  - added optional `inputs.i.optional` field to indicate that a tensor may be `None`
  - made data type assumptions in `preprocessing` and `postprocessing` explicit by adding `'ensure_dtype'` operations per default.
  - allow to specify multiple thresholds (along an `axis`) in a 'binarize' processing step

#### generic 0.3.0 / application 0.3.0 / collection 0.3.0 / dataset 0.3.0 / notebook 0.3.0

- Breaking canges that are fully auto-convertible
  - dropped `download_url`
  - dropped non-file attachments
  - `attachments.files` moved to `attachments.i.source`
- Non-breaking changes
  - added optional `parent` field

#### model 0.5.0

all generic 0.3.0 changes (except models already have the `parent` field) plus:

- Breaking changes that are partially auto-convertible
  - `inputs.i.axes` are now defined in more detail (same for `outputs.i.axes`)
  - `inputs.i.shape` moved per axes to `inputs.i.axes.size` (same for `outputs.i.shape`)
  - new pre-/postprocessing 'fixed_zero_mean_unit_variance' separated from 'zero_mean_unit_variance', where `mode=fixed` is no longer valid.
    (for scalar values this is auto-convertible.)
- Breaking changes that are fully auto-convertible
  - changes in `weights.pytorch_state_dict.architecture`
    - renamed `weights.pytorch_state_dict.architecture.source_file` to `...architecture.source`
  - changes in `weights.pytorch_state_dict.dependencies`
    - only conda environment allowed and specified by `weights.pytorch_state_dict.dependencies.source`
    - new optional field `weights.pytorch_state_dict.dependencies.sha256`
  - changes in `weights.tensorflow_model_bundle.dependencies`
    - same as changes in `weights.pytorch_state_dict.dependencies`
  - moved `test_inputs` to `inputs.i.test_tensor`
  - moved `test_outputs` to `outputs.i.test_tensor`
  - moved `sample_inputs` to `inputs.i.sample_tensor`
  - moved `sample_outputs` to `outputs.i.sample_tensor`
  - renamed `inputs.i.name` to `inputs.i.id`
  - renamed `outputs.i.name` to `outputs.i.id`
  - renamed `inputs.i.preprocessing.name` to `inputs.i.preprocessing.id`
  - renamed `outputs.i.postprocessing.name` to `outputs.i.postprocessing.id`
- Non-breaking changes:
  - new pre-/postprocessing: `id`='ensure_dtype' with kwarg `dtype`

#### generic 0.2.4 and model 0.4.10

- Breaking changes that are fully auto-convertible
  - `id` overwritten with value from `config.bioimageio.nickname` if available
- Non-breaking changes
  - `version_number` is a new, optional field indicating that an RDF is the nth published version with a given `id`
  - `id_emoji` is a new, optional field (set from `config.bioimageio.nickname_icon` if available)
  - `uploader` is a new, optional field with `email` and an optional `name` subfields

#### model 0.4.9

- Non-breaking changes
  - make pre-/postprocessing kwargs `mode` and `axes` always optional for model description 0.3 and 0.4

#### model 0.4.8

- Non-breaking changes
  - `cite` field is now optional

#### generic 0.2.2 and model 0.4.7

- Breaking changes that are fully auto-convertible
  - name field may not include '/' or '\' (conversion removes these)

#### model 0.4.6

- Non-breaking changes
  - Implicit output shape can be expanded by inserting `null` into `shape:scale` and indicating length of new dimension D in the `offset` field. Keep in mind that `D=2*'offset'`.

#### model 0.4.5

- Breaking changes that are fully auto-convertible
  - `parent` field changed to hold a string that is a bioimage.io ID, a URL or a local relative path (and not subfields `uri` and `sha256`)

#### model 0.4.4

- Non-breaking changes
  - new optional field `training_data`

#### dataset 0.2.2

- Non-breaking changes
  - explicitly define and document dataset description (for now, clone of generic description with type="dataset")

#### model 0.4.3

- Non-breaking changes
  - add optional field `download_url`
  - add optional field `dependencies` to all weight formats (not only pytorch_state_dict)
  - add optional `pytorch_version` to the pytorch_state_dict and torchscript weight formats

#### model 0.4.2

- Bug fixes:
  - in a `pytorch_state_dict` weight entry `architecture` is no longer optional.

#### collection 0.2.2

- Non-breaking changes
  - make `authors`, `cite`, `documentation` and `tags` optional

- Breaking changes that are fully auto-convertible
  - Simplifies collection description 0.2.1 by merging resource type fields together to a `collection` field,
    holindg a list of all resources in the specified collection.

#### generic 0.2.2 / model 0.3.6 / model 0.4.2

- Non-breaking changes
  - `rdf_source` new optional field
  - `id` new optional field

#### collection 0.2.1

- First official release, extends generic description with fields `application`, `model`, `dataset`, `notebook` and (nested)
  `collection`, which hold lists linking to respective resources.

#### generic 0.2.1

- Non-breaking changes
  - add optional `email` and `github_user` fields to entries in `authors`
  - add optional `maintainers` field (entries like in `authors` but  `github_user` is required (and `name` is not))

#### model 0.4.1

- Breaking changes that are fully auto-convertible
  - moved field `dependencies` to `weights:pytorch_state_dict:dependencies`

- Non-breaking changes
  - `documentation` field accepts URLs as well

#### model 0.3.5

- Non-breaking changes
  - `documentation` field accepts URLs as well

#### model 0.4.0

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
  - a `maintainers` field was added to the model description.
  - the entries in the `authors` field may now additionally contain `email` or `github_user`.
  - the summary returned by the `validate` command now also contains a list of warnings.
  - an `update_format` command was added to aid with updating older RDFs by applying auto-conversion.

#### model 0.3.4

- Non-breaking changes
  - Add optional parameter `eps` to `scale_range` postprocessing.

#### model 0.3.3

- Breaking changes that are fully auto-convertible
  - `reference_input` for implicit output tensor shape was renamed to `reference_tensor`

#### model 0.3.2

- Breaking changes
  - The RDF file name in a package should be `rdf.yaml` for all the RDF (not `model.yaml`);
  - Change `authors` and `packaged_by` fields from List[str] to List[Author] with Author consisting of a dictionary `{name: '<Full name>', affiliation: '<Affiliation>', orcid: 'optional orcid id'}`;
  - Add a mandatory `type` field to comply with the generic description. Only valid value is 'model' for model description;
  - Only allow `license` identifier from the [SPDX license list](https://spdx.org/licenses/);

- Non-breaking changes
  - Add optional `version` field (default 0.1.0) to keep track of model changes;
  - Allow the values in the `attachments` list to be any values besides URI;
