# bioimage.io model specification
Specification of the fields used in a bioimage.io-compliant RDF that describes AI models with pretrained weights.

These fields are typically stored in a YAML file which we call a model resource description file (model RDF).

**General notes on this documentation:**
| symbol | explanation |
| --- | --- |
| `field`<sub>type hint</sub> | A fields's <sub>expected type</sub> may be shortened. If so, the abbreviated or full type is displayed below the field's description and can expanded to view further (nested) details if available. |
| Union[A, B, ...] | indicates that a field value may be of type A or B, etc.|
| Literal[a, b, ...] | indicates that a field value must be the specific value a or b, etc.|
| Type* := Type (restrictions) | A field Type* followed by an asterisk indicates that annotations, e.g. value restriction apply. These are listed in parentheses in the expanded type description. They are not always intuitively understandable and merely a hint at more complex validation.|
| \<type\>.v\<major\>_\<minor\>.\<sub spec\> | Subparts of a spec might be taken from another spec type or format version. |
| `field` ≝ `default` | Default field values are indicated after '≝' and make a field optional. However, `type` and `format_version` alwyas need to be set for resource descriptions written as YAML files and determine which bioimage.io specification applies. They are optional only when creating a resource description in Python code using the appropriate, `type` and `format_version` specific class.|
| `field` ≝ 🡇 | Default field value is not displayed in-line, but in the code block below. |
| ∈📦  | Files referenced in fields which are marked with '∈📦 ' are included when packaging the resource to a .zip archive. The resource description YAML file (RDF) is always included well as 'rdf.yaml'. |

## `type`<sub> Literal[model]</sub> ≝ `model`




## `format_version`<sub> Literal[0.4.10]</sub> ≝ `0.4.10`




## `authors`<sub> Sequence[generic.v0_2.Author]</sub>


<details><summary>Sequence[generic.v0_2.Author]

</summary>


**generic.v0_2.Author:**
### `authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




### `authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




### `authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#authorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `authors.i.name`<sub> str</sub>




### `authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

## `description`<sub> str</sub>




## `documentation`<sub> Union</sub>

[*Examples:*](#documentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']

<details><summary>Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]

</summary>

Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])


</details>

## `inputs`<sub> Sequence[InputTensorDescr]</sub>


<details><summary>Sequence[InputTensorDescr]

</summary>


**InputTensorDescr:**
### `inputs.i.name`<sub> TensorName</sub>




### `inputs.i.description`<sub> str</sub> ≝ ``




### `inputs.i.axes`<sub> str</sub>




### `inputs.i.data_range`<sub> Optional</sub> ≝ `None`



Optional[Sequence[float (allow_inf_nan=True), float (allow_inf_nan=True)]]

### `inputs.i.data_type`<sub> Literal[float32, uint8, uint16]</sub>




### `inputs.i.shape`<sub> Union</sub>

[*Examples:*](#inputsishape) [(1, 512, 512, 1), {'min': (1, 64, 64, 1), 'step': (0, 32, 32, 0)}]

<details><summary>Union[Sequence[int], ParameterizedInputShape]

</summary>


**ParameterizedInputShape:**
#### `inputs.i.shape.min`<sub> Sequence[int]</sub>




#### `inputs.i.shape.step`<sub> Sequence[int]</sub>




</details>

### `inputs.i.preprocessing`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[BinarizeDescr, ..., ScaleRangeDescr]*]

</summary>

Sequence of Union[BinarizeDescr, ClipDescr, ScaleLinearDescr, SigmoidDescr, ZeroMeanUnitVarianceDescr, ScaleRangeDescr]
(discriminator=name)

**BinarizeDescr:**
#### `inputs.i.preprocessing.i.name`<sub> Literal[binarize]</sub> ≝ `binarize`




#### `inputs.i.preprocessing.i.kwargs`<sub> BinarizeKwargs</sub>


<details><summary>BinarizeKwargs

</summary>


**BinarizeKwargs:**
##### `inputs.i.preprocessing.i.kwargs.threshold`<sub> float</sub>




</details>

**ClipDescr:**
#### `inputs.i.preprocessing.i.name`<sub> Literal[clip]</sub> ≝ `clip`




#### `inputs.i.preprocessing.i.kwargs`<sub> ClipKwargs</sub>


<details><summary>ClipKwargs

</summary>


**ClipKwargs:**
##### `inputs.i.preprocessing.i.kwargs.min`<sub> float</sub>




##### `inputs.i.preprocessing.i.kwargs.max`<sub> float</sub>




</details>

**ScaleLinearDescr:**
#### `inputs.i.preprocessing.i.name`<sub> Literal[scale_linear]</sub> ≝ `scale_linear`




#### `inputs.i.preprocessing.i.kwargs`<sub> ScaleLinearKwargs</sub>


<details><summary>ScaleLinearKwargs

</summary>


**ScaleLinearKwargs:**
##### `inputs.i.preprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`

[*Example:*](#inputsipreprocessingikwargsaxes) 'xy'


Optional[str (RestrictCharacters(alphabet='czyx'); AfterValidator(validate_unique_entries))]

##### `inputs.i.preprocessing.i.kwargs.gain`<sub> Union[float, Sequence[float]]</sub> ≝ `1.0`




##### `inputs.i.preprocessing.i.kwargs.offset`<sub> Union[float, Sequence[float]]</sub> ≝ `0.0`




</details>

**SigmoidDescr:**
#### `inputs.i.preprocessing.i.name`<sub> Literal[sigmoid]</sub> ≝ `sigmoid`




**ZeroMeanUnitVarianceDescr:**
#### `inputs.i.preprocessing.i.name`<sub> Literal[zero_mean_unit_variance]</sub> ≝ `zero_mean_unit_variance`




#### `inputs.i.preprocessing.i.kwargs`<sub> ZeroMeanUnitVarianceKwargs</sub>


<details><summary>ZeroMeanUnitVarianceKwargs

</summary>


**ZeroMeanUnitVarianceKwargs:**
##### `inputs.i.preprocessing.i.kwargs.mode`<sub> Literal</sub> ≝ `fixed`



Literal[fixed, per_dataset, per_sample]

##### `inputs.i.preprocessing.i.kwargs.axes`<sub> str</sub>

[*Example:*](#inputsipreprocessingikwargsaxes) 'xy'



##### `inputs.i.preprocessing.i.kwargs.mean`<sub> Union</sub> ≝ `None`

[*Example:*](#inputsipreprocessingikwargsmean) (1.1, 2.2, 3.3)


Union[float, Sequence[float] (MinLen(min_length=1)), None]

##### `inputs.i.preprocessing.i.kwargs.std`<sub> Union</sub> ≝ `None`

[*Example:*](#inputsipreprocessingikwargsstd) (0.1, 0.2, 0.3)


Union[float, Sequence[float] (MinLen(min_length=1)), None]

##### `inputs.i.preprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`




</details>

**ScaleRangeDescr:**
#### `inputs.i.preprocessing.i.name`<sub> Literal[scale_range]</sub> ≝ `scale_range`




#### `inputs.i.preprocessing.i.kwargs`<sub> ScaleRangeKwargs</sub>


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `inputs.i.preprocessing.i.kwargs.mode`<sub> Literal[per_dataset, per_sample]</sub>




##### `inputs.i.preprocessing.i.kwargs.axes`<sub> str</sub>

[*Example:*](#inputsipreprocessingikwargsaxes) 'xy'



##### `inputs.i.preprocessing.i.kwargs.min_percentile`<sub> Union[int, float]</sub> ≝ `0.0`




##### `inputs.i.preprocessing.i.kwargs.max_percentile`<sub> Union[int, float]</sub> ≝ `100.0`




##### `inputs.i.preprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`




##### `inputs.i.preprocessing.i.kwargs.reference_tensor`<sub> Optional[TensorName]</sub> ≝ `None`




</details>

</details>

</details>

## `license`<sub> Union</sub>

[*Examples:*](#license) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, str]

## `name`<sub> str</sub>




## `outputs`<sub> Sequence[OutputTensorDescr]</sub>


<details><summary>Sequence[OutputTensorDescr]

</summary>


**OutputTensorDescr:**
### `outputs.i.name`<sub> TensorName</sub>




### `outputs.i.description`<sub> str</sub> ≝ ``




### `outputs.i.axes`<sub> str</sub>




### `outputs.i.data_range`<sub> Optional</sub> ≝ `None`



Optional[Sequence[float (allow_inf_nan=True), float (allow_inf_nan=True)]]

### `outputs.i.data_type`<sub> Literal</sub>



Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

### `outputs.i.shape`<sub> Union</sub>


<details><summary>Union[Sequence[int], ImplicitOutputShape]

</summary>


**ImplicitOutputShape:**
#### `outputs.i.shape.reference_tensor`<sub> TensorName</sub>




#### `outputs.i.shape.scale`<sub> Sequence[Optional[float]]</sub>




#### `outputs.i.shape.offset`<sub> Sequence</sub>



Sequence[Union[int, float (MultipleOf(multiple_of=0.5))]]

</details>

### `outputs.i.halo`<sub> Optional[Sequence[int]]</sub> ≝ `None`




### `outputs.i.postprocessing`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[BinarizeDescr, ..., ScaleMeanVarianceDescr]*]

</summary>

Sequence of Union of
- BinarizeDescr
- ClipDescr
- ScaleLinearDescr
- SigmoidDescr
- ZeroMeanUnitVarianceDescr
- ScaleRangeDescr
- ScaleMeanVarianceDescr

(discriminator=name)

**BinarizeDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[binarize]</sub> ≝ `binarize`




#### `outputs.i.postprocessing.i.kwargs`<sub> BinarizeKwargs</sub>


<details><summary>BinarizeKwargs

</summary>


**BinarizeKwargs:**
##### `outputs.i.postprocessing.i.kwargs.threshold`<sub> float</sub>




</details>

**ClipDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[clip]</sub> ≝ `clip`




#### `outputs.i.postprocessing.i.kwargs`<sub> ClipKwargs</sub>


<details><summary>ClipKwargs

</summary>


**ClipKwargs:**
##### `outputs.i.postprocessing.i.kwargs.min`<sub> float</sub>




##### `outputs.i.postprocessing.i.kwargs.max`<sub> float</sub>




</details>

**ScaleLinearDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[scale_linear]</sub> ≝ `scale_linear`




#### `outputs.i.postprocessing.i.kwargs`<sub> ScaleLinearKwargs</sub>


<details><summary>ScaleLinearKwargs

</summary>


**ScaleLinearKwargs:**
##### `outputs.i.postprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`

[*Example:*](#outputsipostprocessingikwargsaxes) 'xy'


Optional[str (RestrictCharacters(alphabet='czyx'); AfterValidator(validate_unique_entries))]

##### `outputs.i.postprocessing.i.kwargs.gain`<sub> Union[float, Sequence[float]]</sub> ≝ `1.0`




##### `outputs.i.postprocessing.i.kwargs.offset`<sub> Union[float, Sequence[float]]</sub> ≝ `0.0`




</details>

**SigmoidDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[sigmoid]</sub> ≝ `sigmoid`




**ZeroMeanUnitVarianceDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[zero_mean_unit_variance]</sub> ≝ `zero_mean_unit_variance`




#### `outputs.i.postprocessing.i.kwargs`<sub> ZeroMeanUnitVarianceKwargs</sub>


<details><summary>ZeroMeanUnitVarianceKwargs

</summary>


**ZeroMeanUnitVarianceKwargs:**
##### `outputs.i.postprocessing.i.kwargs.mode`<sub> Literal</sub> ≝ `fixed`



Literal[fixed, per_dataset, per_sample]

##### `outputs.i.postprocessing.i.kwargs.axes`<sub> str</sub>

[*Example:*](#outputsipostprocessingikwargsaxes) 'xy'



##### `outputs.i.postprocessing.i.kwargs.mean`<sub> Union</sub> ≝ `None`

[*Example:*](#outputsipostprocessingikwargsmean) (1.1, 2.2, 3.3)


Union[float, Sequence[float] (MinLen(min_length=1)), None]

##### `outputs.i.postprocessing.i.kwargs.std`<sub> Union</sub> ≝ `None`

[*Example:*](#outputsipostprocessingikwargsstd) (0.1, 0.2, 0.3)


Union[float, Sequence[float] (MinLen(min_length=1)), None]

##### `outputs.i.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`




</details>

**ScaleRangeDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[scale_range]</sub> ≝ `scale_range`




#### `outputs.i.postprocessing.i.kwargs`<sub> ScaleRangeKwargs</sub>


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `outputs.i.postprocessing.i.kwargs.mode`<sub> Literal[per_dataset, per_sample]</sub>




##### `outputs.i.postprocessing.i.kwargs.axes`<sub> str</sub>

[*Example:*](#outputsipostprocessingikwargsaxes) 'xy'



##### `outputs.i.postprocessing.i.kwargs.min_percentile`<sub> Union[int, float]</sub> ≝ `0.0`




##### `outputs.i.postprocessing.i.kwargs.max_percentile`<sub> Union[int, float]</sub> ≝ `100.0`




##### `outputs.i.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`




##### `outputs.i.postprocessing.i.kwargs.reference_tensor`<sub> Optional[TensorName]</sub> ≝ `None`




</details>

**ScaleMeanVarianceDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[scale_mean_variance]</sub> ≝ `scale_mean_variance`




#### `outputs.i.postprocessing.i.kwargs`<sub> ScaleMeanVarianceKwargs</sub>


<details><summary>ScaleMeanVarianceKwargs

</summary>


**ScaleMeanVarianceKwargs:**
##### `outputs.i.postprocessing.i.kwargs.mode`<sub> Literal[per_dataset, per_sample]</sub>




##### `outputs.i.postprocessing.i.kwargs.reference_tensor`<sub> TensorName</sub>




##### `outputs.i.postprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`

[*Example:*](#outputsipostprocessingikwargsaxes) 'xy'


Optional[str (RestrictCharacters(alphabet='czyx'); AfterValidator(validate_unique_entries))]

##### `outputs.i.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`




</details>

</details>

</details>

## `test_inputs`<sub> Sequence</sub>


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix='.npy', case_sensitive=True))

</details>

## `test_outputs`<sub> Sequence</sub>


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix='.npy', case_sensitive=True))

</details>

## `timestamp`<sub> _internal.types.Datetime</sub>




## `weights`<sub> WeightsDescr</sub>


<details><summary>WeightsDescr

</summary>


**WeightsDescr:**
### `weights.keras_hdf5`<sub> Optional[KerasHdf5WeightsDescr]</sub> ≝ `None`


<details><summary>Optional[KerasHdf5WeightsDescr]

</summary>


**KerasHdf5WeightsDescr:**
#### `weights.keras_hdf5.source`<sub> Union</sub>


<details><summary>Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]

</summary>

Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])


</details>

#### `weights.keras_hdf5.sha256`<sub> Optional[_internal.io.Sha256]</sub> ≝ `None`




#### `weights.keras_hdf5.attachments`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.keras_hdf5.attachments.files`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.keras_hdf5.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.keras_hdf5.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.keras_hdf5.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.keras_hdf5.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightskeras_hdf5authorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.keras_hdf5.authors.i.name`<sub> str</sub>




##### `weights.keras_hdf5.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.keras_hdf5.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`

[*Examples:*](#weightskeras_hdf5dependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.keras_hdf5.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightskeras_hdf5parent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.keras_hdf5.tensorflow_version`<sub> Optional</sub> ≝ `None`



Optional[_internal.version_type.Version]

</details>

### `weights.onnx`<sub> Optional[OnnxWeightsDescr]</sub> ≝ `None`


<details><summary>Optional[OnnxWeightsDescr]

</summary>


**OnnxWeightsDescr:**
#### `weights.onnx.source`<sub> Union</sub>


<details><summary>Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]

</summary>

Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])


</details>

#### `weights.onnx.sha256`<sub> Optional[_internal.io.Sha256]</sub> ≝ `None`




#### `weights.onnx.attachments`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.onnx.attachments.files`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.onnx.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.onnx.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.onnx.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.onnx.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightsonnxauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.onnx.authors.i.name`<sub> str</sub>




##### `weights.onnx.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.onnx.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`

[*Examples:*](#weightsonnxdependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.onnx.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightsonnxparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.onnx.opset_version`<sub> Optional[int (Ge(ge=7))]</sub> ≝ `None`




</details>

### `weights.pytorch_state_dict`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[PytorchStateDictWeightsDescr]

</summary>


**PytorchStateDictWeightsDescr:**
#### `weights.pytorch_state_dict.source`<sub> Union</sub>


<details><summary>Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]

</summary>

Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])


</details>

#### `weights.pytorch_state_dict.sha256`<sub> Optional[_internal.io.Sha256]</sub> ≝ `None`




#### `weights.pytorch_state_dict.attachments`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.pytorch_state_dict.attachments.files`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.pytorch_state_dict.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.pytorch_state_dict.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.pytorch_state_dict.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.pytorch_state_dict.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightspytorch_state_dictauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.pytorch_state_dict.authors.i.name`<sub> str</sub>




##### `weights.pytorch_state_dict.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.pytorch_state_dict.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`

[*Examples:*](#weightspytorch_state_dictdependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.pytorch_state_dict.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightspytorch_state_dictparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.pytorch_state_dict.architecture`<sub> Union</sub>

[*Examples:*](#weightspytorch_state_dictarchitecture) ['my_function.py:MyNetworkClass', 'my_module.submodule.get_my_model']


Union[CallableFromFile, CallableFromDepencency]

#### `weights.pytorch_state_dict.architecture_sha256`<sub> Optional[_internal.io.Sha256]</sub> ≝ `None`
The SHA256 of the architecture source file, if the architecture is not defined in a module listed in `dependencies`
You can drag and drop your file to this
[online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate a SHA256 in your browser.
Or you can generate a SHA256 checksum with Python's `hashlib`,
[here is a codesnippet](https://gist.github.com/FynnBe/e64460463df89439cff218bbf59c1100).



#### `weights.pytorch_state_dict.kwargs`<sub> Dict[str, Any]</sub> ≝ `{}`




#### `weights.pytorch_state_dict.pytorch_version`<sub> Optional</sub> ≝ `None`



Optional[_internal.version_type.Version]

</details>

### `weights.tensorflow_js`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TensorflowJsWeightsDescr]

</summary>


**TensorflowJsWeightsDescr:**
#### `weights.tensorflow_js.source`<sub> Union</sub>


<details><summary>Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]

</summary>

Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])


</details>

#### `weights.tensorflow_js.sha256`<sub> Optional[_internal.io.Sha256]</sub> ≝ `None`




#### `weights.tensorflow_js.attachments`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.tensorflow_js.attachments.files`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.tensorflow_js.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.tensorflow_js.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.tensorflow_js.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.tensorflow_js.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstensorflow_jsauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.tensorflow_js.authors.i.name`<sub> str</sub>




##### `weights.tensorflow_js.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.tensorflow_js.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`

[*Examples:*](#weightstensorflow_jsdependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.tensorflow_js.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstensorflow_jsparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.tensorflow_js.tensorflow_version`<sub> Optional</sub> ≝ `None`



Optional[_internal.version_type.Version]

</details>

### `weights.tensorflow_saved_model_bundle`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TensorflowSavedModelBundleWeightsDescr]

</summary>


**TensorflowSavedModelBundleWeightsDescr:**
#### `weights.tensorflow_saved_model_bundle.source`<sub> Union</sub>


<details><summary>Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]

</summary>

Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])


</details>

#### `weights.tensorflow_saved_model_bundle.sha256`<sub> Optional[_internal.io.Sha256]</sub> ≝ `None`




#### `weights.tensorflow_saved_model_bundle.attachments`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.tensorflow_saved_model_bundle.attachments.files`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.tensorflow_saved_model_bundle.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.tensorflow_saved_model_bundle.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.tensorflow_saved_model_bundle.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.tensorflow_saved_model_bundle.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstensorflow_saved_model_bundleauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.tensorflow_saved_model_bundle.authors.i.name`<sub> str</sub>




##### `weights.tensorflow_saved_model_bundle.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.tensorflow_saved_model_bundle.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`

[*Examples:*](#weightstensorflow_saved_model_bundledependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.tensorflow_saved_model_bundle.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstensorflow_saved_model_bundleparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.tensorflow_saved_model_bundle.tensorflow_version`<sub> Optional</sub> ≝ `None`



Optional[_internal.version_type.Version]

</details>

### `weights.torchscript`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TorchscriptWeightsDescr]

</summary>


**TorchscriptWeightsDescr:**
#### `weights.torchscript.source`<sub> Union</sub>


<details><summary>Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]

</summary>

Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])


</details>

#### `weights.torchscript.sha256`<sub> Optional[_internal.io.Sha256]</sub> ≝ `None`




#### `weights.torchscript.attachments`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.torchscript.attachments.files`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.torchscript.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.torchscript.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.torchscript.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.torchscript.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstorchscriptauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.torchscript.authors.i.name`<sub> str</sub>




##### `weights.torchscript.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.torchscript.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`

[*Examples:*](#weightstorchscriptdependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.torchscript.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstorchscriptparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.torchscript.pytorch_version`<sub> Optional</sub> ≝ `None`



Optional[_internal.version_type.Version]

</details>

</details>

## `attachments`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
### `attachments.files`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

## `cite`<sub> Sequence[generic.v0_2.CiteEntry]</sub> ≝ `[]`


<details><summary>Sequence[generic.v0_2.CiteEntry]

</summary>


**generic.v0_2.CiteEntry:**
### `cite.i.text`<sub> str</sub>




### `cite.i.doi`<sub> Optional[_internal.types.Doi]</sub> ≝ `None`




### `cite.i.url`<sub> Optional[str]</sub> ≝ `None`




</details>

## `config`<sub> Dict[str, YamlValue]</sub> ≝ `{}`

[*Example:*](#config) {'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}



## `covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')
[*Example:*](#covers) 'cover.png'

<details><summary>Sequence[Union[_internal.url.HttpUrl, Path*, _internal.io.RelativeFilePath]*]

</summary>

Sequence of Union of
- _internal.url.HttpUrl
- Path (PathType(path_type='file'); Predicate(func=<function PurePath.is_absolute at 0x7f8a787418a0>))
- _internal.io.RelativeFilePath

(WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg'), case_sensitive=False); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

## `download_url`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`




## `git_repo`<sub> Optional[str]</sub> ≝ `None`

[*Example:*](#git_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



## `icon`<sub> Union</sub> ≝ `None`


<details><summary>Union[str*, Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union of
  - Path (PathType(path_type='file'))
  - _internal.io.RelativeFilePath
  - _internal.url.HttpUrl
  - Url (max_length=2083 allowed_schemes=['http', 'https'])

  (AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))
- None


</details>

## `id`<sub> Optional[ModelId]</sub> ≝ `None`




## `id_emoji`<sub> Optional</sub> ≝ `None`



Optional[str (Len(min_length=1, max_length=1))]

## `links`<sub> Sequence[str]</sub> ≝ `[]`

[*Example:*](#links) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



## `maintainers`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[generic.v0_2.Maintainer]

</summary>


**generic.v0_2.Maintainer:**
### `maintainers.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




### `maintainers.i.email`<sub> Optional[Email]</sub> ≝ `None`




### `maintainers.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#maintainersiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `maintainers.i.name`<sub> Optional</sub> ≝ `None`



Optional[str (AfterValidator(_remove_slashes))]

### `maintainers.i.github_user`<sub> str</sub>




</details>

## `packaged_by`<sub> Sequence[generic.v0_2.Author]</sub> ≝ `[]`


<details><summary>Sequence[generic.v0_2.Author]

</summary>


**generic.v0_2.Author:**
### `packaged_by.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




### `packaged_by.i.email`<sub> Optional[Email]</sub> ≝ `None`




### `packaged_by.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#packaged_byiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `packaged_by.i.name`<sub> str</sub>




### `packaged_by.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

## `parent`<sub> Optional[LinkedModel]</sub> ≝ `None`


<details><summary>Optional[LinkedModel]

</summary>


**LinkedModel:**
### `parent.id`<sub> ModelId</sub>




### `parent.version_number`<sub> Optional[int]</sub> ≝ `None`




</details>

## `rdf_source`<sub> Union</sub> ≝ `None`


<details><summary>Union[Path*, ..., None]

</summary>

Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])
- None


</details>

## `run_mode`<sub> Optional[RunMode]</sub> ≝ `None`


<details><summary>Optional[RunMode]

</summary>


**RunMode:**
### `run_mode.name`<sub> Union[Literal[deepimagej], str]</sub>




### `run_mode.kwargs`<sub> Dict[str, Any]</sub> ≝ `{}`




</details>

## `sample_inputs`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

## `sample_outputs`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

## `tags`<sub> Sequence[str]</sub> ≝ `[]`

[*Example:*](#tags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



## `training_data`<sub> Union</sub> ≝ `None`


<details><summary>Union[dataset.v0_2.LinkedDataset, dataset.v0_2.DatasetDescr, None]

</summary>


**dataset.v0_2.LinkedDataset:**
### `training_data.id`<sub> dataset.v0_2.DatasetId</sub>




### `training_data.version_number`<sub> Optional[int]</sub> ≝ `None`




**dataset.v0_2.DatasetDescr:**
### `training_data.name`<sub> str</sub>




### `training_data.description`<sub> str</sub>




### `training_data.covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')
[*Example:*](#training_datacovers) 'cover.png'

<details><summary>Sequence[Union[_internal.url.HttpUrl, Path*, _internal.io.RelativeFilePath]*]

</summary>

Sequence of Union of
- _internal.url.HttpUrl
- Path (PathType(path_type='file'); Predicate(func=<function PurePath.is_absolute at 0x7f8a787418a0>))
- _internal.io.RelativeFilePath

(WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg'), case_sensitive=False); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

### `training_data.id_emoji`<sub> Optional</sub> ≝ `None`



Optional[str (Len(min_length=1, max_length=1))]

### `training_data.authors`<sub> Sequence[generic.v0_2.Author]</sub> ≝ `[]`


<details><summary>Sequence[generic.v0_2.Author]

</summary>


**generic.v0_2.Author:**
#### `training_data.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




#### `training_data.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




#### `training_data.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#training_dataauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

#### `training_data.authors.i.name`<sub> str</sub>




#### `training_data.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

### `training_data.attachments`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
#### `training_data.attachments.files`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

### `training_data.cite`<sub> Sequence[generic.v0_2.CiteEntry]</sub> ≝ `[]`


<details><summary>Sequence[generic.v0_2.CiteEntry]

</summary>


**generic.v0_2.CiteEntry:**
#### `training_data.cite.i.text`<sub> str</sub>




#### `training_data.cite.i.doi`<sub> Optional[_internal.types.Doi]</sub> ≝ `None`




#### `training_data.cite.i.url`<sub> Optional[str]</sub> ≝ `None`




</details>

### `training_data.config`<sub> Dict[str, YamlValue]</sub> ≝ `{}`

[*Example:*](#training_dataconfig) {'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}



### `training_data.download_url`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`




### `training_data.git_repo`<sub> Optional[str]</sub> ≝ `None`

[*Example:*](#training_datagit_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



### `training_data.icon`<sub> Union</sub> ≝ `None`


<details><summary>Union[str*, Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union of
  - Path (PathType(path_type='file'))
  - _internal.io.RelativeFilePath
  - _internal.url.HttpUrl
  - Url (max_length=2083 allowed_schemes=['http', 'https'])

  (AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))
- None


</details>

### `training_data.links`<sub> Sequence[str]</sub> ≝ `[]`

[*Example:*](#training_datalinks) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



### `training_data.uploader`<sub> Optional[generic.v0_2.Uploader]</sub> ≝ `None`


<details><summary>Optional[generic.v0_2.Uploader]

</summary>


**generic.v0_2.Uploader:**
#### `training_data.uploader.email`<sub> Email</sub>




#### `training_data.uploader.name`<sub> Optional</sub> ≝ `None`



Optional[str (AfterValidator(_remove_slashes))]

</details>

### `training_data.maintainers`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[generic.v0_2.Maintainer]

</summary>


**generic.v0_2.Maintainer:**
#### `training_data.maintainers.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




#### `training_data.maintainers.i.email`<sub> Optional[Email]</sub> ≝ `None`




#### `training_data.maintainers.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#training_datamaintainersiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

#### `training_data.maintainers.i.name`<sub> Optional</sub> ≝ `None`



Optional[str (AfterValidator(_remove_slashes))]

#### `training_data.maintainers.i.github_user`<sub> str</sub>




</details>

### `training_data.rdf_source`<sub> Union</sub> ≝ `None`


<details><summary>Union[Path*, ..., None]

</summary>

Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])
- None


</details>

### `training_data.tags`<sub> Sequence[str]</sub> ≝ `[]`

[*Example:*](#training_datatags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



### `training_data.version`<sub> Optional</sub> ≝ `None`



Optional[_internal.version_type.Version]

### `training_data.version_number`<sub> Optional[int]</sub> ≝ `None`




### `training_data.format_version`<sub> Literal[0.2.4]</sub> ≝ `0.2.4`




### `training_data.badges`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[generic.v0_2.BadgeDescr]

</summary>


**generic.v0_2.BadgeDescr:**
#### `training_data.badges.i.label`<sub> str</sub>

[*Example:*](#training_databadgesilabel) 'Open in Colab'



#### `training_data.badges.i.icon`<sub> Union</sub> ≝ `None`

[*Example:*](#training_databadgesiicon) 'https://colab.research.google.com/assets/colab-badge.svg'

<details><summary>Union[Union[Path*, _internal.io.RelativeFilePath]*, _internal.url.HttpUrl, Url*, None]

</summary>

Union of
- Union[Path (PathType(path_type='file')), _internal.io.RelativeFilePath]
  (AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])
- None


</details>

#### `training_data.badges.i.url`<sub> _internal.url.HttpUrl</sub>

[*Example:*](#training_databadgesiurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



</details>

### `training_data.documentation`<sub> Optional</sub> ≝ `None`

[*Examples:*](#training_datadocumentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']

<details><summary>Optional[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Optional[Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f8a75305b20>, return_type=PydanticUndefined, when_used='unless-none'))]

</details>

### `training_data.license`<sub> Union</sub> ≝ `None`

[*Examples:*](#training_datalicense) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId, str, None]

### `training_data.type`<sub> Literal[dataset]</sub> ≝ `dataset`




### `training_data.id`<sub> Optional[dataset.v0_2.DatasetId]</sub> ≝ `None`




### `training_data.source`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`




</details>

## `uploader`<sub> Optional[generic.v0_2.Uploader]</sub> ≝ `None`


<details><summary>Optional[generic.v0_2.Uploader]

</summary>


**generic.v0_2.Uploader:**
### `uploader.email`<sub> Email</sub>




### `uploader.name`<sub> Optional</sub> ≝ `None`



Optional[str (AfterValidator(_remove_slashes))]

</details>

## `version`<sub> Optional</sub> ≝ `None`



Optional[_internal.version_type.Version]

## `version_number`<sub> Optional[int]</sub> ≝ `None`




# Example values
### `authors.i.orcid`
0000-0001-2345-6789
### `documentation`
- https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md
- README.md

### `inputs.i.shape`
- (1, 512, 512, 1)
- {'min': (1, 64, 64, 1), 'step': (0, 32, 32, 0)}

### `inputs.i.preprocessing.i.kwargs.axes`
xy
### `inputs.i.preprocessing.i.kwargs.axes`
xy
### `inputs.i.preprocessing.i.kwargs.mean`
(1.1, 2.2, 3.3)
### `inputs.i.preprocessing.i.kwargs.std`
(0.1, 0.2, 0.3)
### `inputs.i.preprocessing.i.kwargs.axes`
xy
### `license`
- CC0-1.0
- MIT
- BSD-2-Clause

### `outputs.i.postprocessing.i.kwargs.axes`
xy
### `outputs.i.postprocessing.i.kwargs.axes`
xy
### `outputs.i.postprocessing.i.kwargs.mean`
(1.1, 2.2, 3.3)
### `outputs.i.postprocessing.i.kwargs.std`
(0.1, 0.2, 0.3)
### `outputs.i.postprocessing.i.kwargs.axes`
xy
### `outputs.i.postprocessing.i.kwargs.axes`
xy
### `weights.keras_hdf5.authors.i.orcid`
0000-0001-2345-6789
### `weights.keras_hdf5.dependencies`
- conda:environment.yaml
- maven:./pom.xml
- pip:./requirements.txt

### `weights.keras_hdf5.parent`
pytorch_state_dict
### `weights.onnx.authors.i.orcid`
0000-0001-2345-6789
### `weights.onnx.dependencies`
- conda:environment.yaml
- maven:./pom.xml
- pip:./requirements.txt

### `weights.onnx.parent`
pytorch_state_dict
### `weights.pytorch_state_dict.authors.i.orcid`
0000-0001-2345-6789
### `weights.pytorch_state_dict.dependencies`
- conda:environment.yaml
- maven:./pom.xml
- pip:./requirements.txt

### `weights.pytorch_state_dict.parent`
pytorch_state_dict
### `weights.pytorch_state_dict.architecture`
- my_function.py:MyNetworkClass
- my_module.submodule.get_my_model

### `weights.tensorflow_js.authors.i.orcid`
0000-0001-2345-6789
### `weights.tensorflow_js.dependencies`
- conda:environment.yaml
- maven:./pom.xml
- pip:./requirements.txt

### `weights.tensorflow_js.parent`
pytorch_state_dict
### `weights.tensorflow_saved_model_bundle.authors.i.orcid`
0000-0001-2345-6789
### `weights.tensorflow_saved_model_bundle.dependencies`
- conda:environment.yaml
- maven:./pom.xml
- pip:./requirements.txt

### `weights.tensorflow_saved_model_bundle.parent`
pytorch_state_dict
### `weights.torchscript.authors.i.orcid`
0000-0001-2345-6789
### `weights.torchscript.dependencies`
- conda:environment.yaml
- maven:./pom.xml
- pip:./requirements.txt

### `weights.torchscript.parent`
pytorch_state_dict
### `config`
{'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}
### `covers`
cover.png
### `git_repo`
https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad
### `links`
('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')
### `maintainers.i.orcid`
0000-0001-2345-6789
### `packaged_by.i.orcid`
0000-0001-2345-6789
### `tags`
('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')
### `training_data.covers`
cover.png
### `training_data.authors.i.orcid`
0000-0001-2345-6789
### `training_data.config`
{'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}
### `training_data.git_repo`
https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad
### `training_data.links`
('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')
### `training_data.maintainers.i.orcid`
0000-0001-2345-6789
### `training_data.tags`
('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')
### `training_data.badges.i.label`
Open in Colab
### `training_data.badges.i.icon`
https://colab.research.google.com/assets/colab-badge.svg
### `training_data.badges.i.url`
https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb
### `training_data.documentation`
- https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md
- README.md

### `training_data.license`
- CC0-1.0
- MIT
- BSD-2-Clause

