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

[These](https://bioimage-io.github.io/spec-bioimage-io/#format-version-overview) are the latest format specifications that bioimage.io-compatible resources should comply to.

Note that the Python package PyYAML does not support YAML 1.2 .
We therefore use and recommend [ruyaml](https://ruyaml.readthedocs.io/en/latest/).
For differences see <https://ruamelyaml.readthedocs.io/en/latest/pyyaml>.

Please also note that the best way to check whether your `rdf.yaml` file is fully bioimage.io-compliant, is to call `bioimageio.core.test_description` from the [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python) Python package.
The [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python) Python package also provides the bioimageio command line interface (CLI) with the `test` command:

```terminal
bioimageio test path/to/your/rdf.yaml
```

## Documentation

The bioimageio.spec documentation is hosted at [https://bioimage-io.github.io/spec-bioimage-io](https://bioimage-io.github.io/spec-bioimage-io).
