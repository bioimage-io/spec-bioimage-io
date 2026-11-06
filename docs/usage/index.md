# Usage

## Recommendations

* Use the [bioimageio.core Python package](https://github.com/bioimage-io/core-bioimage-io-python) to not only validate the format of your `bioimageio.yaml`/`rdf.yaml` file, but also test and deploy it (e.g. model inference).
* bioimageio.spec keeps evolving. Try to use and upgrade to the most current format version!
  Note: The command line interface `bioimageio` (part of [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python)) has the `update-format` command to help you with that.

## Examples

We provide some [bioimageio.yaml/rdf.yaml example files](https://github.com/bioimage-io/spec-bioimage-io/blob/main/example_descriptions/) to describe models, applications, notebooks and datasets; more examples are available at [bioimage.io](https://bioimage.io).
There is also an [example notebook](https://github.com/bioimage-io/spec-bioimage-io/blob/main/example/load_model_and_create_your_own.ipynb) demonstrating how to programmatically access the models, applications, notebooks and datasets descriptions in Python.
For integration of bioimageio resources we recommend the [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python) Python package.

## bioimageio command-line interface (CLI)

The bioimageio CLI has moved to [bioimageio.core](https://github.com/bioimage-io/core-bioimage-io-python).

## API overview

bioimageio.spec implements type and format version specific `pydantic.BaseModel` models for resources shared on bioimage.io.

The return type of [`load_description`][bioimageio.spec.load_description] is [`ResourceDescr`][bioimageio.spec.ResourceDescr].
This is a `typing.Union` over various format type and format version specific and unspecific classes including [`InvalidDescr`][bioimageio.spec.InvalidDescr] and [`GenericDescr`][bioimageio.spec.GenericDescr].
The individual `*Descr`-classes of this `Union` can be instantiated in code to create a bioimage.io resource description in the first place.

For more narrow type hints and runtime-checks during loading dedicated `load_*_description` methods may be used:

* [`load_model_description`][bioimageio.spec.load_model_description]
* [`load_dataset_description`][bioimageio.spec.load_dataset_description]

Another way to narrow/check the return type is to call [`load_description`][bioimageio.spec.load_description]/[`load_model_description`][bioimageio.spec.load_model_description]... with `format_version="latest"`, returning [`LatestResourceDescr`][bioimageio.spec.LatestResourceDescr]/[`ModelDescr`][bioimageio.spec.ModelDescr] (instead of [`AnyModelDescr`][bioimageio.spec.AnyModelDescr])/... .

To export resource descriptions:

* [`save_bioimageio_package`][bioimageio.spec.save_bioimageio_package] saves the metadata alongside referenced files as a zip*archive (recommended)
* [`save_bioimageio_package_as_folder`][bioimageio.spec.save_bioimageio_package_as_folder]
* [`save_bioimageio_package_to_stream`][bioimageio.spec.save_bioimageio_package_to_stream]
* [`save_bioimageio_yaml_only`][bioimageio.spec.save_bioimageio_yaml_only] (save only the metadata without referenced files)

## Environment variables

See [bioimageio.spec.settings][]

## Logging

bioimageio.spec (and bioimageio.core) use [loguru](https://loguru.readthedocs.io/en/stable/) for logging.
To enable logs from bioimageio.spec (and bioimageio.core) use:

```python
from loguru import logger

logger.enable("bioimageio")
```
