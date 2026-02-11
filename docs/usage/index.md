# Usage

## 💁 Recommendations

* Use the [bioimageio.core Python package](https://github.com/bioimage-io/core-bioimage-io-python) to not only validate the format of your `bioimageio.yaml`/`rdf.yaml` file, but also test and deploy it (e.g. model inference).
* bioimageio.spec keeps evolving. Try to use and upgrade to the most current format version!
  Note: The command line interface `bioimageio` (part of [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python)) has the `update-format` command to help you with that.

## Examples

We provide some [bioimageio.yaml/rdf.yaml example files](https://github.com/bioimage-io/spec-bioimage-io/blob/main/example_descriptions/) to describe models, applications, notebooks and datasets; more examples are available at [bioimage.io](https://bioimage.io).
There is also an [example notebook](https://github.com/bioimage-io/spec-bioimage-io/blob/main/example/load_model_and_create_your_own.ipynb) demonstrating how to programmatically access the models, applications, notebooks and datasets descriptions in Python.
For integration of bioimageio resources we recommend the [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python) Python package.

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

See [bioimageio.spec.settings][]

## 🗎 Logging

bioimageio.spec (and bioimageio.core) use [loguru](https://loguru.readthedocs.io/en/stable/) for logging.
To enable logs from bioimageio.spec (and bioimageio.core) use:

```python
from loguru import logger

logger.enable("bioimageio")
```
