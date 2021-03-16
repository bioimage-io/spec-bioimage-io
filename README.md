## BioImage.IO Model File Specification

The BioImage.IO model file specification defines pretrained AI models represented in [YAML format](https://en.wikipedia.org/wiki/YAML). This format is used to describe models hosted in the [BioImage.IO](https://bioimage.io) model repository site.

To get a quick overview of the config file, see an example file [here](https://github.com/bioimage-io/pytorch-bioimage-io/blob/master/specs/models/unet2d_nuclei_broad/UNet2DNucleiBroad.model.yaml).

## Current `format_version`: 0.3.0

A model entry in the bioimage.io model zoo is defined by a configuration file `model.yaml`.
The configuration file must contain the following fields; optional fields are followed by \[optional\].
If a field is followed by \[optional\]\*, they are optional depending on another field.


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

- `cite` \[optional\]
A citation entry or list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used.

- `git_repo` \[optional\]
A url to the git repository, e.g. to Github or Gitlab.\
If the model is contained in a subfolder of a git repository, then a url to the exact folder (which contains the configuration yaml file) should be used.

- `tags`
A list of tags.

- `license`
A string to a common license name (e.g. `MIT`, `APLv2`) or a relative path to the license file.

- `documentation`
Relative path to file with additional documentation in markdown.

- `attachments` \[optional\] Dictionary of text keys and URI (or a list of URI) values to additional, relevant files. E.g. we can place a list of URIs under the `files` to list images and other files that are necessary for the documentation or for the model to run, these files will be included when generating the model package.

- `packaged_by` \[optional\]
The person(s) that have packaged and uploaded this model. Only needs to be specified if different from `authors` in the root weights`, see `weights` for more details.

- `parent` \[optional\] Parent model from which the trained weights of this model have been derived, e.g. by finetuning the weights of this model on a different dataset. For format changes of the same trained model checkpoint, see `weights`.
  - `uri` Url of another model available on bioimage.io or path to a local model in the bioimage.io specification. If it is a url, it needs to be a github url linking to the page containing the model (NOT the raw file). 
  - `sha256` hash of the weights of the parent model.

- `inputs` 
Describes the input tensors expected by this model.
Must be a list of *tensor specification keys*.

  *tensor specification keys*:
  - `name` tensor name
  - `data_type` the data type of this tensor. For inputs, only `float32` is allowed and the consumer software needs to ensure that the correct data type is passed here. For outputs can be any of `float32, float64, (u)int8, (u)int16, (u)int32, (u)int64`. The data flow in bioimage.io models is explained [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).
  - `data_range` \[optional\] tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor. If not specified, the full data range that can be expressed in `data_type` is allowed.
  - `axes` string of axes identifying characters from: btczyx. Same length and order as the axes in `shape`.
  - `shape` specification of tensor shape. It can be specified in three diffeent ways:
    1. as exact shape with same length as `axes`, e.g. `shape: [1, 512, 512, 1]`
    2. (only for input) as a sequence of valid shapes.\
       The valid shapes are given by `shape = min + k * step for k in {0, 1, ...}`. Specified by the following fields: 
       - `min` the minimum input shape with same length as `axes`
       - `step` the minimum shape change with same length as `axes`
    3. (only for output) in reference to the shape of an input tensor.\
       The shape of the output tensor is `shape = shape(input_tensor) * scale + 2 * offset`. Specified by the following fields:
       - `reference_input` name of the reference input tensor
       - `scale` list of factors 'output_pix/input_pix' for each dimension
       - `offset` position of origin wrt to input 
       - `halo` the halo to crop from the output tensor (for example to crop away boundary efects or for tiling). The halo should be croped from both sides, i.e. `shape_after_crop = shape - 2 * halo`. The `halo` is not cropped by the bioimage.io model, but is left to be cropped by the consumer software. Use `offset` if the model output itself is cropped.
  - `preprocessing` \[optional\] (only for input) list of transformations describing how this input should be preprocessed. Each entry has these keys:
    - `name` name of preprocessing (see [supported_formats_and_operations.md#preprocessing](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#preprocessing) for valid names).
    - `kwargs` \[optional\] key word arguments for `preprocessing`.
  - `postprocessing` \[optional\](only for output) list describing how this output should be postprocessed. Each entry has these keys:
    - `name` name of the postprocessing (see [supported_formats_and_operations.md#postprocessing](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#postprocessing) for valid names).
    - `kwargs`\[optional\] key word arguments for `postprocessing`.

- `outputs`
Describes the output tensors from this model.
Must be a list of *tensor specification*.

- `source` \[optional\]\*
Language and framework specific implementation.\
As some weights contain the model architecture, the source is optional depending on `weight_format`.\
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

- `language` \[optional\]\*
Programming language of the source code. For now, we support `python` and `java`.
This field is only required if the field `source` is present.

<!---
What about `javascript`?
-->

- `framework` \[optional\]\*
The deep learning framework of the source code. For now, we support `pytorch` and `tensorflow`.
This field is only required if the field `source` is present.

- `sha256` \[optional\]\*
SHA256 checksum of the model file (for both serialized model file or source code).\
You can drag and drop your file to this [online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate it in your browser.\
Or you can generate the SHA256 code for your model and weights by using for example, `hashlib` in Python, [here is a codesnippet](#code-snippet-to-compute-sha256-checksum).
This field is only required if the field source is present.

- `kwargs` \[optional\]\*
Keyword arguments for the implementation specified by [`source`](#source).
This field is only required if the field `source` is present.

- `covers`
A list of cover images provided by either a relative path to the model folder, or a hyperlink starts with `https`.\
Please use an image smaller than 500KB, aspect ratio width to height 2:1. The supported image formats are: `jpg`, `png`, `gif`.
<!--- `I am not quite sure what we decided on for the uri identifiers in the end, I am sticking with the simplest option for now <format>+<protocoll>://<path>`, e.g.: `conda+file://./req.txt` -->  

- `dependencies` Dependency manager and dependency file, specified as `<dependency manager>:<relative path to file>`\
For example:
  - conda:./environment.yaml
  - maven:./pom.xml
  - pip:./requirements.txt

- `test_inputs` list of URIs to test inputs as described in inputs for a single test case. Supported file formats/extensions: .npy
- `test_outputs` analog to test_inputs.

- `sample_inputs` \[optional\] list of URIs to sample inputs to illustrate possible inputs for the model, for example stored as png or tif images.
- `sample_outputs` \[optional\] list of URIs to sample outputs corresponding to the `sample_inputs`.

- `weights` The weights for this model. Weights can be given for different formats, but should otherwise be equivalent. The available weight formats determine which consumers can use this model.
   - `weight_format` Format of this set of weights. Weight formats can define additional (optional or required) fields. See [supported_formats_and_operations.md#Weight Format](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#weight_format)
        - `authors` a list of authors. If this is the root weight (it does not have a `parent` field): the person(s) that have trained this model. If this is a child wieght (it has a `parent` field): the person(s) who have converted the weights to this format.
        - `parent` \[optional\]* the source weights used as input for converting the weights to this format. For example, if the weights were converted from the format `pytorch_state_dict` to `pytorch_script`, the parent is `pytorch_state_dict`. All weight entries except one (the initial set of weights resulting from training the model), need to have this field.
        - `source` link to the weights file. Preferably an url to the weights file.
        - `sha256` SHA256 checksum of the model weight file specified by `source` (see `sha256` section for how to generate the checksum)
        - `attachments` \[optional\] Dictionary of text keys and URI (or a list of URI) values to additional, relevant files that are specific to the current weight format. A list of URIs can be listed under the `files` key to included additional files for generating the model package.

- `run_mode` \[optional\] Custom run mode for this model: for more complex prediction procedures like test time data augmentation that currently cannot be expressed in the specification. The different run modes should be listed in [supported_formats_and_operations.md#Run Modes](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#run-modes).
  - `name` the name of the `run_mode`
  - `kwargs` \[optional\] keyword arguments for this `run_mode`
 
- `config` \[optional\]
A custom configuration field that can contain any other keys which are not defined above. It can be very specifc to a framework or specific tool. To avoid conflicted definitions, it is recommended to wrap configuration into a sub-field named with the specific framework or tool name. 

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
