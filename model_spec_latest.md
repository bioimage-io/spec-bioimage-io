# BioImage.IO Model Resource Description File Specification 0.3.4
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing AI models with pretrained weights.
These fields are typically stored in YAML files which we called Model Resource Description Files or `model RDF`.
The model RDFs can be downloaded or uploaded to the bioimage.io website, produced or consumed by BioImage.IO-compatible consumers(e.g. image analysis software or other website).

The model RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.

* `format_version` _String_ Version of the BioImage.IO Model Resource Description File Specification used.
This is mandatory, and important for the consumer software to verify before parsing the fields.
The recommended behavior for the implementation is to keep backward compatibility and throw an error if the model yaml
is in an unsupported format version. The current format version described here is
0.3.4
* `authors` _List\[Author\]_ Dictionary of text keys and URI (or a list of URI) values to additional, relevant files. E.g. we can place a list of URIs under the `files` to list images and other files that this resource depends on.
  1. _Author_   is a Dict with the following keys:
    * `name` _String_ Full name.
    * `affiliation` _optional String_ Affiliation.
    * `orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
* `cite` _List\[CiteEntry\]_ A citation entry or list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used. List\[CiteEntry\] is a Dict with the following keys:
  * `text` _String_ 
  * `doi` _optional* String_ 
  * `url` _optional* String_ 
* `description` _String_ A string containing a brief description.
* `documentation` _RelativeLocalPath→Path_ Relative path to file with additional documentation in markdown. This means: 1) only relative file path is allowed 2) the file must be in markdown format with `.md` file name extension 3) URL is not allowed. It is recommended to use `README.md` as the documentation name.
* `license` _String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
* `name` _String_ Name of this model. It should be human-readable and only contain letters, numbers, `_`, `-` or spaces and not be longer than 36 characters.
* `tags` _List\[String\]_ A list of tags.
* `test_inputs` _List\[URI→String\]_ List of URIs to test inputs as described in inputs for **a single test case**. This means if your model has more than one input, you should provide one URI for each input.Each test input should be a file with a ndarray in [numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).The extension must be '.npy'.
* `test_outputs` _List\[URI→String\]_ Analog to to test_inputs.
* `timestamp` _DateTime_ Timestamp of the initial creation of this model in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format.
* `type` _String_ 
* `weights` _Dict\[String, Union\[PytorchStateDictWeightsEntry | PytorchScriptWeightsEntry | KerasHdf5WeightsEntry | TensorflowJsWeightsEntry | TensorflowSavedModelBundleWeightsEntry | OnnxWeightsEntry\]\]_ The weights for this model. Weights can be given for different formats, but should otherwise be equivalent. The available weight formats determine which consumers can use this model.
  1. _String_ Format of this set of weights. Weight formats can define additional (optional or required) fields. See [supported_formats_and_operations.md#Weight Format](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#weight_format). One of: pytorch_state_dict, pytorch_script, keras_hdf5, tensorflow_js, tensorflow_saved_model_bundle, onnx
* `attachments` _optional Dict\[String, List\[Union\[URI→String | Raw\]\]\]_ 
  1. _optional* List\[Union\[URI→String | Raw\]\]_ Dictionary of text keys and URI (or a list of URI) values to additional, relevant files. E.g. we can place a list of URIs under the `files` to list images and other files that this resource depends on.
    1. _optional Union\[URI→String | Raw\]_ 
      1. _optional URI→String_ 
      1. _optional Raw_ 
* `badges` _optional List\[Badge\]_ a list of badges
  1. _Badge_ Custom badge Badge is a Dict with the following keys:Custom badge
    * `label` _String_ e.g. 'Open in Colab'
    * `icon` _optional String_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
    * `url` _optional URI→String_ e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'
* `config` _optional Dict\[Any, Any\]_ A custom configuration field that can contain any keys not present in the RDF spec. This means you should not store, for example, github repo URL in `config` since we already have the `git_repo` key defined in the spec.
Keys in `config` may be very specific to a tool or consumer software. To avoid conflicted definitions, it is recommended to wrap configuration into a sub-field named with the specific domain or tool name, for example:
```yaml
   config:
      bioimage_io:  # here is the domain name
        my_custom_key: 3837283
        another_key:
           nested: value
      imagej:
        macro_dir: /path/to/macro/file
```
If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.

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

* `covers` _optional List\[URI→String\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'https'.Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
* `dependencies` _optional Dependencies→String_ Dependency manager and dependency file, specified as `<dependency manager>:<relative path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'
* `download_url` _optional String_ recommended url to the zipped file if applicable
* `framework` _optional String_ The deep learning framework of the source code. One of: pytorch, tensorflow. This field is only required if the field `source` is present.
* `git_repo` _optional String_ A url to the git repository, e.g. to Github or Gitlab.If the model is contained in a subfolder of a git repository, then a url to the exact folder(which contains the configuration yaml file) should be used.
* `icon` _optional String_ an icon for the resource
* `inputs` _List\[InputTensor\]_ Describes the input tensors expected by this model. List\[InputTensor\] is a Dict with the following keys:
  * `axes` _Axes→String_ Axes identifying characters from: bitczyx. Same length and order as the axes in `shape`.

    | character | description |
    | --- | --- |
    |  b  |  batch (groups multiple samples) |
    |  i  |  instance/index/element |
    |  t  |  time |
    |  c  |  channel |
    |  z  |  spatial dimension z |
    |  y  |  spatial dimension y |
    |  x  |  spatial dimension x |
  * `data_type` _String_ The data type of this tensor. For inputs, only `float32` is allowed and the consumer software needs to ensure that the correct data type is passed here. For outputs can be any of `float32, float64, (u)int8, (u)int16, (u)int32, (u)int64`. The data flow in bioimage.io models is explained [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).
  * `name` _String_ Tensor name.
  * `shape` _InputShape→Union\[ExplicitShape→List\[Integer\] | ParametrizedInputShape\]_ Specification of tensor shape.
    1. _optional ExplicitShape→List\[Integer\]_ Exact shape with same length as `axes`, e.g. `shape: [1, 512, 512, 1]`
    1. _ParametrizedInputShape_ A sequence of valid shapes given by `shape = min + k * step for k in {0, 1, ...}`. ParametrizedInputShape is a Dict with the following keys:
      * `min` _List\[Integer\]_ The minimum input shape with same length as `axes`
      * `step` _List\[Integer\]_ The minimum shape change with same length as `axes`
  * `data_range` _optional Tuple_ Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor. If not specified, the full data range that can be expressed in `data_type` is allowed.
  * `description` _optional String_ 
  * `preprocessing` _optional List\[Preprocessing\]_ Description of how this input should be preprocessed.
    1. _Preprocessing_   is a Dict with the following keys:
      * `name` _String_ Name of preprocessing. One of: binarize, clip, scale_linear, sigmoid, zero_mean_unit_variance, scale_range (see [supported_formats_and_operations.md#preprocessing](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#preprocessing) for information on which transformations are supported by specific consumer software).
      * `kwargs` _optional Kwargs→Dict\[String, Any\]_ Key word arguments.
* `kwargs` _optional Kwargs→Dict\[String, Any\]_ Keyword arguments for the implementation specified by `source`. This field is only required if the field `source` is present.
* `language` _optional* String_ Programming language of the source code. One of: python, java. This field is only required if the field `source` is present.
* `links` _optional List\[String\]_ links to other bioimage.io resources
* `outputs` _List\[OutputTensor\]_ Describes the output tensors from this model. List\[OutputTensor\] is a Dict with the following keys:
  * `axes` _Axes→String_ Axes identifying characters from: bitczyx. Same length and order as the axes in `shape`.

    | character | description |
    | --- | --- |
    |  b  |  batch (groups multiple samples) |
    |  i  |  instance/index/element |
    |  t  |  time |
    |  c  |  channel |
    |  z  |  spatial dimension z |
    |  y  |  spatial dimension y |
    |  x  |  spatial dimension x |
  * `data_type` _String_ The data type of this tensor. For inputs, only `float32` is allowed and the consumer software needs to ensure that the correct data type is passed here. For outputs can be any of `float32, float64, (u)int8, (u)int16, (u)int32, (u)int64`. The data flow in bioimage.io models is explained [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).
  * `name` _String_ Tensor name.
  * `shape` _OutputShape→Union\[ExplicitShape→List\[Integer\] | ImplicitOutputShape\]_ 
    1. _optional ExplicitShape→List\[Integer\]_ 
    1. _ImplicitOutputShape_ In reference to the shape of an input tensor, the shape of the output tensor is `shape = shape(input_tensor) * scale + 2 * offset`. ImplicitOutputShape is a Dict with the following keys:
      * `offset` _List\[Integer\]_ Position of origin wrt to input.
      * `reference_tensor` _String_ Name of the reference tensor.
      * `scale` _List\[Float\]_ 'output_pix/input_pix' for each dimension.
  * `data_range` _optional Tuple_ Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor. If not specified, the full data range that can be expressed in `data_type` is allowed.
  * `description` _optional String_ 
  * `halo` _optional List\[Integer\]_ The halo to crop from the output tensor (for example to crop away boundary effects or for tiling). The halo should be cropped from both sides, i.e. `shape_after_crop = shape - 2 * halo`. The `halo` is not cropped by the bioimage.io model, but is left to be cropped by the consumer software. Use `shape:offset` if the model output itself is cropped and input and output shapes not fixed.
  * `postprocessing` _optional List\[Postprocessing\]_ Description of how this output should be postprocessed.
    1. _Postprocessing_   is a Dict with the following keys:
      * `name` _String_ Name of postprocessing. One of: binarize, clip, scale_linear, sigmoid, zero_mean_unit_variance, scale_range, scale_mean_variance (see [supported_formats_and_operations.md#postprocessing](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#postprocessing) for information on which transformations are supported by specific consumer software).
      * `kwargs` _optional Kwargs→Dict\[String, Any\]_ Key word arguments.
* `packaged_by` _optional List\[Author\]_ The persons that have packaged and uploaded this model. Only needs to be specified if different from `authors` in root or any entry in `weights`.
  1. _Author_   is a Dict with the following keys:
    * `name` _String_ Full name.
    * `affiliation` _optional String_ Affiliation.
    * `orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
* `parent` _ModelParent_ Parent model from which the trained weights of this model have been derived, e.g. by finetuning the weights of this model on a different dataset. For format changes of the same trained model checkpoint, see `weights`. ModelParent is a Dict with the following keys:
  * `sha256` _optional SHA256→String_ Hash of the weights of the parent model.
  * `uri` _optional URI→String_ Url of another model available on bioimage.io or path to a local model in the bioimage.io specification. If it is a url, it needs to be a github url linking to the page containing the model (NOT the raw file).
* `run_mode` _RunMode_ Custom run mode for this model: for more complex prediction procedures like test time data augmentation that currently cannot be expressed in the specification. The different run modes should be listed in [supported_formats_and_operations.md#Run Modes](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#run-modes). RunMode is a Dict with the following keys:
  * `name` _String_ The name of the `run_mode`
  * `kwargs` _optional Kwargs→Dict\[String, Any\]_ Key word arguments.
* `sample_inputs` _optional List\[URI→String\]_ List of URIs to sample inputs to illustrate possible inputs for the model, for example stored as png or tif images.
* `sample_outputs` _optional List\[URI→String\]_ List of URIs to sample outputs corresponding to the `sample_inputs`.
* `sha256` _optional String_ SHA256 checksum of the model source code file.You can drag and drop your file to this [online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate it in your browser. Or you can generate the SHA256 code for your model and weights by using for example, `hashlib` in Python. 
Code snippet to compute SHA256 checksum

```python
import hashlib

filename = "your filename here"
with open(filename, "rb") as f:
  bytes = f.read() # read entire file as bytes
  readable_hash = hashlib.sha256(bytes).hexdigest()
  print(readable_hash)
  ```

 This field is only required if the field source is present.
* `source` _optional* ImportableSource→String_ Language and framework specific implementation. As some weights contain the model architecture, the source is optional depending on the present weight formats. `source` can either point to a local implementation: `<relative path to file>:<identifier of implementation within the source file>` or the implementation in an available dependency: `<root-dependency>.<sub-dependency>.<identifier>`.
For example: `my_function.py:MyImplementation` or `core_library.some_module.some_function`.
* `version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
