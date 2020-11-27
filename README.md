# Bioimiage.io Configuration Specification

The model zoo specification contains configuration definitions for the following categories:
- [`Model`](#model-specification): configuration of a trainable (deep-learning) model.

The configurations are represented by a yaml file.

To get a quick overview of the config file, see an example file [here](https://github.com/bioimage-io/pytorch-bioimage-io/blob/master/specs/models/unet2d/nuclei_broad/UNet2DNucleiBroad.model.yaml).

## Current `format_version`: 0.3.0


## Model Specification

A model entry in the bioimage.io model zoo is defined by a configuration file `<model name>.model.yaml`.
The configuration file must contain the following \[optional\]* keys (* denotes that the field is optional depending on input to another field):


- `format_version`
Version of this bioimage.io configuration specification. This is mandatory, and important for the consumer software to verify before parsing the fields.
The recommended behavior for the implementation is to keep backward compatibility, and throw error if the model yaml is in an unsupported format version.

- `name`
Name of this model. The model name should be human readble and only contain letters, numbers, `_`, `-` or spaces and not be longer than 36 characters.

- `timestamp`
Timestamp of the initial creation of this model in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format.

- `description`
A string containing a brief description. 

- `authors`
A list of author strings. 
A string can be seperated by `;` in order to identify multiple handles per author.
The authors are the creators of the specifications and the primary points of contact.

- `cite`
A citation entry or list of citation entries.
Each entry contains of a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used.

- `git_repo`
A url to the git repository, e.g. to Github or Gitlab.\
If the model is contained in a subfolder of a git repository, then a url to the exact folder (which contains the configuration yaml file) should be used.

- `tags`
A list of tags.

- `license`
A string to a common license name (e.g. `MIT`, `APLv2`) or a relative path to the license file.

- `documentation`
Relative path to file with additional documentation in markdown.

- `attachments`
Dictionary of text keys and URI values to additional, relevant files.

- `inputs`
Describes the input tensors expected by this model.
Must be a list of *tensor specification keys*.

  *tensor specification keys*:
  - `name` tensor name
  - `data_type` data type (e.g. float32)
  - `data_range` tuple of (minimum, maximum)
  - `axes` string of axes identifying characters from: btczyx
  - `shape` specification of tensor shape\
    Either as *exact shape with same length as `axes`*,\
    or (only for input) as {`min` *minimum shape with same length as `axes`*, `step` *minimum shape change with same length as `axes`*},\
    or (only for output) as {`reference_input` *input tensor name*, `scale` *list of factors 'output_pix/input_pix' for each dimension*, `offset` *position of origin wrt to input*, `halo` *the halo to crop from the output tensor (for example to crop away boundary efects or for tiling)*}
  - `[preprocessing]` (only for input) list of transformations describing how this input should be preprocessed. Each entry has these keys:
    - `name` name of preprocessing (see [supported_formats_and_operations.md#preprocessing](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#preprocessing) for valid names).
    - `[kwargs]` key word arguments for `preprocessing`.
  - `[postprocessing]` (only for output) list describing how this output should be postprocessed. Each entry has these keys:
    - `name` name of the postprocessing (see [supported_formats_and_operations.md#postprocessing](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#postprocessing) for valid names).
    - `[kwargs]` key word arguments for `postprocessing`.

- `outputs`
Describes the output tensors from this model.
Must be a list of *tensor specification*.

- `language`
Programming language of the source code. For now, we support `python` and `java`.
<!---
What about `javascript`?
-->

- `framework`
The deep learning framework of the source code. For now, we support `pytorch` and `tensorflow`.
Can be `null` if the implementation is not framework specific.\
`language` and `framework` define which model runner can use this model for inference. 

- `[source]*`
Language and framework specific implementation.\
As some weights contain the model architecture, the source is optional depending on `weights_format`.\
This can either point to a local implementation:
`<relative path to file>:<identifier of implementation within the source file>`\
or the implementation in an available dependency:
`<root-dependency>.<sub-dependency>.<identifier>`\
For example:
  - `./my_function:MyImplementation`
  - `core_library.some_module.some_function`
<!---
java: <path-to-jar>:ClassName ?
-->

- `sha256`
SHA256 checksum of the model file (for both serialized model file or source code).\
You can drag and drop your file to this [online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate it in your browser.\
Or you can generate the SHA256 code for your model and weights by using for example, `hashlib` in Python, [here is a codesnippet](#code-snippet-to-compute-sha256-checksum).

- `kwargs`
Keyword arguments for the implementation specified by [`source`](#source).

- `covers`
A list of cover images provided by either a relative path to the model folder, or a hyperlink starts with `https`.\
Please use an image smaller than 500KB, aspect ratio width to height 2:1. The supported image formats are: `jpg`, `png`, `gif`.
<!--- `I am not quite sure what we decided on for the uri identifiers in the end, I am sticking with the simplest option for now <format>+<protocoll>://<path>`, e.g.: `conda+file://./req.txt` -->  

- `dependencies` Dependency manager and dependency file, specified as `<dependency manager>:<relative path to file>`\
For example:
  - conda:./environment.yaml
  - maven:./pom.xml
  - pip:./requirements.txt

- `[attachments]` Additional files for this specification; e.g. images that are necessary for the documentation. These files will be included when generating the model package.

- `test_inputs` list of URIs to test inputs as described in inputs for a single test case. Supported file formats/extensions: .npy
- `test_outputs` analog to test_inputs.

- `[sample_inputs]` list of URIs to sample inputs to illustrate possible inputs for the model, for example stored as png or tif images.
- `[sample_outputs]` list of URIs to sample outputs corresponding to the `sample_inputs`.

- `weights` The weights for this model. Weights can be given for different formats, but should otherwise be equivalent.
   - `weight_format` Format of this set of weights. Weight formats can define additional (optional or required) fields. See [supported_formats_and_operations.md#Weight Format](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#weight_format)
        - `[authors]` a list of authors.
        - `source` link to the weights file. Preferably an url to the weights file.
        - `sha256` SHA256 checksum of the model weight file specified by `source` (see `models` section above for how to generate SHA256 checksum)
        - `[attachments]` weight specific attachments that will be included when generating the model package.

- `[execution_model]` Custom mode for running prediction with this model. For more complex prediction procedures like test time data augmentation that cannot be expressed in the current model configuration. The different execution models should be listed in [supported_formats_and_operations.md#Execution Model](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#execution_model)
  - `name` the name of the execution model
  - `[kwargs]` keyword arguments for this execution model
 
- `[config]`
A custom configuration field that can contain any other keys which are not defined above. It can be very specifc to a framework or specific tool. To avoid conflicted defintions, it is recommended to wrap configuration into a sub-field named with the specific framework or tool name. 

For example:
```yaml
config:
  # custom config for DeepImageJ, see https://github.com/bioimage-io/configuration/issues/23
  deepimagej:
    model_keys:
      # In principle the tag "SERVING" is used in almost every tf model
      model_tag: tf.saved_model.tag_constants.SERVING
      # Signature definition to call the model. Again "SERVING" is the most general
      signature_definition: tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY
    test_information:  
      input_size: [2048x2048] # Size of the input images  
      output_size: [1264x1264 ]# Size of all the outputs  
      device: cpu # Device used. In principle either cpu or GPU  
      memory_peak: 257.7 Mb # Maximum memory consumed by the model in the device  
      runtime: 78.8s # Time it took to run the model
      pixel_size: [9.658E-4µmx9.658E-4µm] # Size of the pixels of the input
```

# Code snippet to compute SHA256 checksum

```python
import hashlib

filename = "your filename here"
with open(filename, "rb") as f:
  bytes = f.read() # read entire file as bytes
  readable_hash = hashlib.sha256(bytes).hexdigest()
  print(readable_hash)
  ```

# Example Configurations
## PyTorch
 - [UNet 2D Nuclei Broad](https://github.com/bioimage-io/pytorch-bioimage-io/blob/master/specs/models/unet2d/nuclei_broad/UNet2DNucleiBroad.model.yaml).
