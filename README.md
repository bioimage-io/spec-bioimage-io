# Bioimiage.io Configuration Specification

## Transformation Specification:
A transformation in the bioimage.io model zoo is defined by a configuration file `<transformation name>.transformation.yaml` according to the following specification
The configuration must contain the keys: `name`, `description`, `format_version`, `language`, `cite`, `authors`, `documentation`, `tags`, `dependencies`, `source`, `kwargs`, `inputs`, and `outputs`. The following additional keys are optional: `thumbnail`, `test_input`, and `test_output`.

### `name`
Name of the transformation. This name should equal the name of any existing, logically equivalent transformation in another framework.

###  `description`
A string containing a brief description. 

### `format_version`
Version of this bioimage.io configuration specification.

### `language`
Programming language of the model definition. Must map to one of `python`, `java` or `javascript`.

### `cite`
A [citation entry](#citation-entry) or a list thereof.

#### citation entry
A citation entry contains of a mandatory `text` field and either one or both of `doi` and `url`.

### `authors`
A list of author strings. 
todo: we want to add identifiers to parse these strings in order to extract github user names, twitter handles, etc... 

### `documentation`
Relative path to file with additional documentation in markdown.

### `tags`
A list of tags.

### `dependencies`
`<format>+<protocoll>://<path>`, e.g.: `conda+file://./req.txt`

### `source`
`<relative path from config file to the implementation source file>:<identifier of transformation within the source file>`

### `kwargs`
Keyword arguments for the transformation class specified by [`source`](#source).

### `inputs`
Either a string from the following choices:
  - any: any number/shape of input tensors is accepted/returned

or a list of [tensor specifications](#tensor-specification).

#### tensor specification
- `name`: tensor name
- `axes`: string of axes identifiers, e.g. btczyx
- `data_type`: data type (e.g. float32)
- `data_range`: tuple of (minimum, maximum)
- [shape]: optional specification of tensor shape
     - Either
       - `min`: minimum shape with same length as `axes`.
       - `step`: minimum shape change with same length as `axes`. 
     - or
       - `exact`: exact shape (or list thereof) with same lenght as `axes`

### `outputs`
Either a string from the following choices:
  - any: any number/shape of input tensors is accepted/returned
  - identity: number/shape of output tensors is the same as input tensors
  - same number: same number of tensors as given to input is returned (shape may differ)

or a list of [tensor specifications](#tensor-specification).

### `thumbnail`
'Artistic' image to convey the idea of the transformation.

### `test_input`
Relative file path to test input. `language` and the file extension define its memory representation.

### `test_output`
Relative file path to test input. `language` and the file extension define its memory representation.

## Model Specification:
A model entry in the bioimage.io model zoo is defined by a configuration file `<model name>.model.yaml` according to the [transformation specification](#transformation-entry) and the **additional** following specification:
The configuration must contain the keys: `name`, `description`, `format_version`, `language`, `cite`, `authors`, `documentation`, `tags`, `dependencies`, `source`, `kwargs`, `inputs`,`framework`, `prediction`, and `training`.  and `outputs`. The following additional keys are optional: `thumbnail`, `test_input`, and `test_output`.

### `framework`
Deep learning framework used for this model. Currently supported frameworks are `tensorflow` and `pytorch`.

### `prediction`
Sub specification of prediction:
- `weights`: model weights
  `source`: link to the model weight file
  `hash`: hash of hash of the model weight file specified by `source`

### `training`
Sub specification of training:
todo
Definition of the training procedure.
Must contain:
- `loss`: list of transformations and loss function used in training
  - `<transformation name>.transform.yaml`: name of pre-loss transformations (differentiable post processing)
    - `<kwarg>`: keyword argument for the transformation
  - `<loss name>.loss.yaml`: name of loss
    - `<kwarg>`: keyword argument to inititalize the loss function
- `optimizer`: optimizer used in training
  - `name`: Name of the optimizer (must)
  - `kwargs`: keyword arguments for the optimizer (can)
- `pretrained_on`: description of pre-training:
  - `data_reader`: list of data readers used in training
    - `name`: Name of dataset in the core library.
    - `kwargs`: key word arguments of data reader
    - TODO need optional ways of specifying identifiers for custom training data via url / doi
  - `n_iterations`: Number of iterations used in training (change to iterations ?)


## data


# Example Configuration

```yaml
[!INCLUDE[example configuration](./UNet2dExample.model.yaml)]
```
