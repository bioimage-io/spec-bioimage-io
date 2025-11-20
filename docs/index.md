--8<-- "README.md"

## Format version overview

All bioimage.io description formats are defined as [Pydantic models](https://docs.pydantic.dev/latest/).

| Type | Format Version | Documentation[^1] | Developer Documentation[^2] |
| --- | --- | --- | --- |
| model | 0.5 </br> 0.4 | [model 0.5](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i2_oneOf_i1) </br> [model 0.4](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i2_oneOf_i0) | [v0_5.ModelDescr](https://bioimage-io.github.io/spec-bioimage-io/dev/api/model/v0_5/#bioimageio.spec.model.v0_5.ModelDescr) </br> [v0_4.ModelDescr](https://bioimage-io.github.io/spec-bioimage-io/dev/api/model/v0_4/#bioimageio.spec.model.v0_4.ModelDescr) |
| dataset | 0.3 </br> 0.2 | [dataset 0.3](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i1_oneOf_i1) </br> [dataset 0.2](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i1_oneOf_i0) | [v0_3.DatasetDescr](https://bioimage-io.github.io/spec-bioimage-io/dev/api/dataset/v0_3/#bioimageio.spec.dataset.v0_3.DatasetDescr) </br> [v0_2.DatasetDescr](https://bioimage-io.github.io/spec-bioimage-io/dev/api/dataset/v0_2/#bioimageio.spec.dataset.v0_2.DatasetDescr) |
| notebook | 0.3 </br> 0.2 | [notebook 0.3](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i3_oneOf_i1) </br> [notebook 0.2](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i3_oneOf_i0) | [v0_3.NotebookDescr](https://bioimage-io.github.io/spec-bioimage-io/dev/api/notebook/v0_3/#bioimageio.spec.notebook.v0_3.NotebookDescr) </br> [v0_2.NotebookDescr](https://bioimage-io.github.io/spec-bioimage-io/dev/api/notebook/v0_2/#bioimageio.spec.notebook.v0_2.NotebookDescr) |
| application | 0.3 </br> 0.2 | [application 0.3](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i0_oneOf_i1) </br> [application 0.2](https://bioimage-io.github.io/spec-bioimage-io/bioimageio_schema_latest/index.html#oneOf_i0_oneOf_i0) | [v0_3.ApplicationDescr](https://bioimage-io.github.io/spec-bioimage-io/dev/api/application/v0_3/#bioimageio.spec.application.v0_3.ApplicationDescr) </br> [v0_2.ApplicationDescr](https://bioimage-io.github.io/spec-bioimage-io/dev/api/application/v0_2/#bioimageio.spec.application.v0_2.ApplicationDescr) |
| generic | 0.3 </br> 0.2 | - | [v0_3.GenericDescr](https://bioimage-io.github.io/spec-bioimage-io/dev/api/generic/v0_3/#bioimageio.spec.generic.v0_3.GenericDescr) </br> [v0_2.GenericDescr](https://bioimage-io.github.io/spec-bioimage-io/dev/api/generic/v0_2/#bioimageio.spec.generic.v0_2.GenericDescr) |

[^1]: JSON Schema based documentation generated with [json-schema-for-humans](https://coveooss.github.io/json-schema-for-humans/).
[^2]: Part of the [bioimageio.spec API reference](https://bioimage-io.github.io/spec-bioimage-io/api).

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
