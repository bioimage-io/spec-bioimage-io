![License](https://img.shields.io/github/license/bioimage-io/spec-bioimage-io.svg)
[![PyPI](https://img.shields.io/pypi/v/bioimageio-spec.svg?style=popout)](https://pypi.org/project/bioimageio.spec/)
[![conda-version](https://anaconda.org/conda-forge/bioimageio.spec/badges/version.svg)](https://anaconda.org/conda-forge/bioimageio.spec/)
[![downloads](https://static.pepy.tech/badge/bioimageio.spec)](https://pepy.tech/project/bioimageio.spec)
[![conda-forge downloads](https://img.shields.io/conda/dn/conda-forge/bioimageio.spec.svg?label=conda-forge)](https://anaconda.org/conda-forge/bioimageio.spec/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![coverage](https://bioimage-io.github.io/spec-bioimage-io/coverage/coverage-badge.svg)](https://bioimage-io.github.io/spec-bioimage-io/coverage/index.html)

# Specifications for bioimage.io

This repository contains the specifications of the standard format defined by the bioimage.io community for the content (i.e., models, datasets and applications) in the [bioimage.io website](https://bioimage.io).
Each item in the content is always described using a YAML 1.2 file named `rdf.yaml` or `bioimageio.yaml`.
This `rdf.yaml` \ `bioimageio.yaml`--- along with the files referenced in it --- can be downloaded from or uploaded to the [bioimage.io website](https://bioimage.io) and may be produced or consumed by bioimage.io-compatible consumers (e.g., image analysis software like ilastik).

[These](https://github.com/bioimage-io/spec-bioimage-io?tab=readme-ov-file#format-version-overview) are the rules and format that bioimage.io-compatible resources must fulfill.

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

| Type | Format Version | Documentation[^1] | Developer Documentation[^2] |
| --- | --- | --- | --- |
| model | 0.5 </br> 0.4 | [model 0.5](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i2_oneOf_i1) </br> [model 0.4](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i2_oneOf_i0) | [ModelDescr_v0_5](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/model/v0_5.html#ModelDescr) </br> [ModelDescr_v0_4](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/model/v0_4.html#ModelDescr) |
| dataset | 0.3 </br> 0.2 | [dataset 0.3](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i1_oneOf_i1) </br> [dataset 0.2](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i1_oneOf_i0) | [DatasetDescr_v0_3](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/dataset/v0_3.html#DatasetDescr) </br> [DatasetDescr_v0_2](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/dataset/v0_2.html#DatasetDescr) |
| notebook | 0.3 </br> 0.2 | [notebook 0.3](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i3_oneOf_i1) </br> [notebook 0.2](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i3_oneOf_i0) | [NotebookDescr_v0_3](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/notebook/v0_3.html#NotebookDescr) </br> [NotebookDescr_v0_2](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/notebook/v0_2.html#NotebookDescr) |
| application | 0.3 </br> 0.2 | [application 0.3](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i0_oneOf_i1) </br> [application 0.2](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i0_oneOf_i0) | [ApplicationDescr_v0_3](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/application/v0_3.html#ApplicationDescr) </br> [ApplicationDescr_v0_2](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/application/v0_2.html#ApplicationDescr) |
| generic | 0.3 </br> 0.2 | - | [GenericDescr_v0_3](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/generic/v0_3.html#GenericDescr) </br> [GenericDescr_v0_2](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/generic/v0_2.html#GenericDescr) |

[^1]: JSON Schema based documentation generated with [json-schema-for-humans](https://coveooss.github.io/json-schema-for-humans/).
[^2]: Part of the bioimageio.spec package documentation generated with [pdoc](https://pdoc.dev/).

## JSON Schema

Simplified descriptions are available as [JSON Schema](https://json-schema.org/) (generated with Pydantic):

| bioimageio.spec version | JSON Schema | documentation[^1] |
| --- | --- | --- |
| latest | [bioimageio_schema_latest.json](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/bioimageio_schema_latest.json) | [latest documentation](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html) |
| 0.5 | [bioimageio_schema_v0-5.json](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/bioimageio_schema_v0-5.json) | [0.5 documentation](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_v0-5/index.html) |

Note: [bioimageio_schema_v0-5.json](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/bioimageio_schema_v0-5.json) and  [bioimageio_schema_latest.json](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/bioimageio_schema_latest.json) are identical, but  [bioimageio_schema_latest.json](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/bioimageio_schema_latest.json) will eventually refer to the future `bioimageio_schema_v0-6.json`.

## Flattened, interactive docs

A flattened view of the types used by the spec that also shows values constraints.

[rendered](https://bioimage-io.github.io/spec-bioimage-io/interactive_docs_v0-5.html)

You can also generate these docs locally by running `PYTHONPATH=./scripts python -m interactive_docs`

## Examples

We provide some [bioimageio.yaml/rdf.yaml example files](https://github.com/bioimage-io/spec-bioimage-io/blob/main/example_descriptions/) to describe models, applications, notebooks and datasets; more examples are available at [bioimage.io](https://bioimage.io).
There is also an [example notebook](https://github.com/bioimage-io/spec-bioimage-io/blob/main/example/load_model_and_create_your_own.ipynb) demonstrating how to programmatically access the models, applications, notebooks and datasets descriptions in Python.
For integration of bioimageio resources we recommend the [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python) Python package.

## 💁 Recommendations

* Use the [bioimageio.core Python package](https://github.com/bioimage-io/core-bioimage-io-python) to not only validate the format of your `bioimageio.yaml`/`rdf.yaml` file, but also test and deploy it (e.g. model inference).
* bioimageio.spec keeps evolving. Try to use and upgrade to the most current format version!
  Note: The command line interface `bioimageio` (part of [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python)) has the `update-format` command to help you with that.

## ⌨ bioimageio command-line interface (CLI)

The bioimageio CLI has moved to [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python).

## 🖥 Installation

bioimageio.spec can be installed with either `conda` or `pip`.
We recommend installing `bioimageio.core` instead to get access to the Python programmatic features available in the BioImage.IO community:

```console
conda install -c conda-forge bioimageio.core
```

or

```console
pip install -U bioimageio.core
```

Still, for a lighter package or just testing, you can install the `bioimageio.spec` package solely:

```console
conda install -c conda-forge bioimageio.spec
```

or

```console
pip install -U bioimageio.spec
```

## 🏞 Environment variables

TODO: link to settings in dev docs

## 🤝 How to contribute

## ♥ Contributors

<a href="https://github.com/bioimage-io/spec-bioimage-io/graphs/contributors">
  <img alt="bioimageio.spec contributors" src="https://contrib.rocks/image?repo=bioimage-io/spec-bioimage-io" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

## 🛈 Versioining scheme

To keep the bioimageio.spec Python package version in sync with the (model) description format version, bioimageio.spec is versioned as MAJOR.MINRO.PATCH.LIB, where MAJOR.MINRO.PATCH correspond to the latest model description format version implemented and LIB may be bumpbed for library changes that do not affect the format version.
[This change was introduced with bioimageio.spec 0.5.3.1](changelog.md#bioimageiospec-0531).

## Δ Changelog

The changelog of the bioimageio.spec Python package and the changes to the resource description format it implements can be found in [changelog.md](https://github.com/bioimage-io/spec-bioimage-io/blob/main/changelog.md).
