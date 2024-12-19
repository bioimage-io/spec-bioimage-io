# 
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
Specialized resource type 'model'



## `format_version`<sub> Literal[0.4.10]</sub> ≝ `0.4.10`
Version of the bioimage.io model description specification used.
When creating a new model always use the latest micro/patch version described here.
The `format_version` is important for any consumer software to understand how to parse the fields.



## `authors`<sub> Sequence[generic.v0_2.Author]</sub>
The authors are the creators of the model RDF and the primary points of contact.

<details><summary>Sequence[generic.v0_2.Author]

</summary>


**generic.v0_2.Author:**
### `authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



### `authors.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



### `authors.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#authorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `authors.i.name`<sub> str</sub>




### `authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

## `description`<sub> str</sub>




## `documentation`<sub> Union</sub>
∈📦 URL or relative path to a markdown file with additional documentation.
The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
The documentation should include a '[#[#]]# Validation' (sub)section
with details on how to quantitatively validate the model on unseen data.
[*Examples:*](#documentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

## `inputs`<sub> Sequence[InputTensorDescr]</sub>
Describes the input tensors expected by this model.

<details><summary>Sequence[InputTensorDescr]

</summary>


**InputTensorDescr:**
### `inputs.i.name`<sub> TensorName</sub>
Tensor name. No duplicates are allowed.



### `inputs.i.description`<sub> str</sub> ≝ ``




### `inputs.i.axes`<sub> str</sub>
Axes identifying characters. Same length and order as the axes in `shape`.
| axis | description |
| --- | --- |
|  b  |  batch (groups multiple samples) |
|  i  |  instance/index/element |
|  t  |  time |
|  c  |  channel |
|  z  |  spatial dimension z |
|  y  |  spatial dimension y |
|  x  |  spatial dimension x |



### `inputs.i.data_range`<sub> Optional</sub> ≝ `None`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
If not specified, the full data range that can be expressed in `data_type` is allowed.


Optional[Sequence[float (allow_inf_nan=True), float (allow_inf_nan=True)]]

### `inputs.i.data_type`<sub> Literal[float32, uint8, uint16]</sub>
For now an input tensor is expected to be given as `float32`.
The data flow in bioimage.io models is explained
[in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).



### `inputs.i.shape`<sub> Union</sub>
Specification of input tensor shape.
[*Examples:*](#inputsishape) [(1, 512, 512, 1), {'min': (1, 64, 64, 1), 'step': (0, 32, 32, 0)}]

<details><summary>Union[Sequence[int], ParameterizedInputShape]

</summary>


**ParameterizedInputShape:**
#### `inputs.i.shape.min`<sub> Sequence[int]</sub>
The minimum input shape



#### `inputs.i.shape.step`<sub> Sequence[int]</sub>
The minimum shape change



</details>

### `inputs.i.preprocessing`<sub> Sequence</sub> ≝ `[]`
Description of how this input should be preprocessed.

<details><summary>Sequence[Union[BinarizeDescr, ..., ScaleRangeDescr]*]

</summary>

Sequence of Union[BinarizeDescr, ClipDescr, ScaleLinearDescr, SigmoidDescr, ZeroMeanUnitVarianceDescr, ScaleRangeDescr]
(Discriminator(discriminator='name', custom_error_type=None, custom_error_message=None, custom_error_context=None))

**BinarizeDescr:**
#### `inputs.i.preprocessing.i.name`<sub> Literal[binarize]</sub> ≝ `binarize`




#### `inputs.i.preprocessing.i.kwargs`<sub> BinarizeKwargs</sub>


<details><summary>BinarizeKwargs

</summary>


**BinarizeKwargs:**
##### `inputs.i.preprocessing.i.kwargs.threshold`<sub> float</sub>
The fixed threshold



</details>

**ClipDescr:**
#### `inputs.i.preprocessing.i.name`<sub> Literal[clip]</sub> ≝ `clip`




#### `inputs.i.preprocessing.i.kwargs`<sub> ClipKwargs</sub>


<details><summary>ClipKwargs

</summary>


**ClipKwargs:**
##### `inputs.i.preprocessing.i.kwargs.min`<sub> float</sub>
minimum value for clipping



##### `inputs.i.preprocessing.i.kwargs.max`<sub> float</sub>
maximum value for clipping



</details>

**ScaleLinearDescr:**
#### `inputs.i.preprocessing.i.name`<sub> Literal[scale_linear]</sub> ≝ `scale_linear`




#### `inputs.i.preprocessing.i.kwargs`<sub> ScaleLinearKwargs</sub>


<details><summary>ScaleLinearKwargs

</summary>


**ScaleLinearKwargs:**
##### `inputs.i.preprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to scale jointly.
For example xy to scale the two image axes for 2d data jointly.
[*Example:*](#inputsipreprocessingikwargsaxes) 'xy'


Optional[str (RestrictCharacters(alphabet='czyx'); AfterValidator(validate_unique_entries))]

##### `inputs.i.preprocessing.i.kwargs.gain`<sub> Union[float, Sequence[float]]</sub> ≝ `1.0`
multiplicative factor



##### `inputs.i.preprocessing.i.kwargs.offset`<sub> Union[float, Sequence[float]]</sub> ≝ `0.0`
additive term



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
Mode for computing mean and variance.
|     mode    |             description              |
| ----------- | ------------------------------------ |
|   fixed     | Fixed values for mean and variance   |
| per_dataset | Compute for the entire dataset       |
| per_sample  | Compute for each sample individually |


Literal[fixed, per_dataset, per_sample]

##### `inputs.i.preprocessing.i.kwargs.axes`<sub> str</sub>
The subset of axes to normalize jointly.
For example `xy` to normalize the two image axes for 2d data jointly.
[*Example:*](#inputsipreprocessingikwargsaxes) 'xy'



##### `inputs.i.preprocessing.i.kwargs.mean`<sub> Union</sub> ≝ `None`
The mean value(s) to use for `mode: fixed`.
For example `[1.1, 2.2, 3.3]` in the case of a 3 channel image with `axes: xy`.
[*Example:*](#inputsipreprocessingikwargsmean) (1.1, 2.2, 3.3)


Union[float, Sequence[float] (MinLen(min_length=1)), None]

##### `inputs.i.preprocessing.i.kwargs.std`<sub> Union</sub> ≝ `None`
The standard deviation values to use for `mode: fixed`. Analogous to mean.
[*Example:*](#inputsipreprocessingikwargsstd) (0.1, 0.2, 0.3)


Union[float, Sequence[float] (MinLen(min_length=1)), None]

##### `inputs.i.preprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`
epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`.



</details>

**ScaleRangeDescr:**
#### `inputs.i.preprocessing.i.name`<sub> Literal[scale_range]</sub> ≝ `scale_range`




#### `inputs.i.preprocessing.i.kwargs`<sub> ScaleRangeKwargs</sub>


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `inputs.i.preprocessing.i.kwargs.mode`<sub> Literal[per_dataset, per_sample]</sub>
Mode for computing percentiles.
|     mode    |             description              |
| ----------- | ------------------------------------ |
| per_dataset | compute for the entire dataset       |
| per_sample  | compute for each sample individually |



##### `inputs.i.preprocessing.i.kwargs.axes`<sub> str</sub>
The subset of axes to normalize jointly.
For example xy to normalize the two image axes for 2d data jointly.
[*Example:*](#inputsipreprocessingikwargsaxes) 'xy'



##### `inputs.i.preprocessing.i.kwargs.min_percentile`<sub> Union[int, float]</sub> ≝ `0.0`
The lower percentile used to determine the value to align with zero.



##### `inputs.i.preprocessing.i.kwargs.max_percentile`<sub> Union[int, float]</sub> ≝ `100.0`
The upper percentile used to determine the value to align with one.
Has to be bigger than `min_percentile`.
The range is 1 to 100 instead of 0 to 100 to avoid mistakenly
accepting percentiles specified in the range 0.0 to 1.0.



##### `inputs.i.preprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability.
`out = (tensor - v_lower) / (v_upper - v_lower + eps)`;
with `v_lower,v_upper` values at the respective percentiles.



##### `inputs.i.preprocessing.i.kwargs.reference_tensor`<sub> Optional[TensorName]</sub> ≝ `None`
Tensor name to compute the percentiles from. Default: The tensor itself.
For any tensor in `inputs` only input tensor references are allowed.
For a tensor in `outputs` only input tensor refereences are allowed if `mode: per_dataset`



</details>

</details>

</details>

## `license`<sub> Union</sub>
A [SPDX license identifier](https://spdx.org/licenses/).
We do notsupport custom license beyond the SPDX license list, if you need that please
[open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose
) to discuss your intentions with the community.
[*Examples:*](#license) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, str]

## `name`<sub> str</sub>
A human-readable name of this model.
It should be no longer than 64 characters and only contain letter, number, underscore, minus or space characters.



## `outputs`<sub> Sequence[OutputTensorDescr]</sub>
Describes the output tensors.

<details><summary>Sequence[OutputTensorDescr]

</summary>


**OutputTensorDescr:**
### `outputs.i.name`<sub> TensorName</sub>
Tensor name. No duplicates are allowed.



### `outputs.i.description`<sub> str</sub> ≝ ``




### `outputs.i.axes`<sub> str</sub>
Axes identifying characters. Same length and order as the axes in `shape`.
| axis | description |
| --- | --- |
|  b  |  batch (groups multiple samples) |
|  i  |  instance/index/element |
|  t  |  time |
|  c  |  channel |
|  z  |  spatial dimension z |
|  y  |  spatial dimension y |
|  x  |  spatial dimension x |



### `outputs.i.data_range`<sub> Optional</sub> ≝ `None`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
If not specified, the full data range that can be expressed in `data_type` is allowed.


Optional[Sequence[float (allow_inf_nan=True), float (allow_inf_nan=True)]]

### `outputs.i.data_type`<sub> Literal</sub>
Data type.
The data flow in bioimage.io models is explained
[in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).


Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

### `outputs.i.shape`<sub> Union</sub>
Output tensor shape.

<details><summary>Union[Sequence[int], ImplicitOutputShape]

</summary>


**ImplicitOutputShape:**
#### `outputs.i.shape.reference_tensor`<sub> TensorName</sub>
Name of the reference tensor.



#### `outputs.i.shape.scale`<sub> Sequence[Optional[float]]</sub>
output_pix/input_pix for each dimension.
'null' values indicate new dimensions, whose length is defined by 2*`offset`



#### `outputs.i.shape.offset`<sub> Sequence</sub>
Position of origin wrt to input.


Sequence[Union[int, float (MultipleOf(multiple_of=0.5))]]

</details>

### `outputs.i.halo`<sub> Optional[Sequence[int]]</sub> ≝ `None`
The `halo` that should be cropped from the output tensor to avoid boundary effects.
The `halo` is to be cropped from both sides, i.e. `shape_after_crop = shape - 2 * halo`.
To document a `halo` that is already cropped by the model `shape.offset` has to be used instead.



### `outputs.i.postprocessing`<sub> Sequence</sub> ≝ `[]`
Description of how this output should be postprocessed.

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

(Discriminator(discriminator='name', custom_error_type=None, custom_error_message=None, custom_error_context=None))

**BinarizeDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[binarize]</sub> ≝ `binarize`




#### `outputs.i.postprocessing.i.kwargs`<sub> BinarizeKwargs</sub>


<details><summary>BinarizeKwargs

</summary>


**BinarizeKwargs:**
##### `outputs.i.postprocessing.i.kwargs.threshold`<sub> float</sub>
The fixed threshold



</details>

**ClipDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[clip]</sub> ≝ `clip`




#### `outputs.i.postprocessing.i.kwargs`<sub> ClipKwargs</sub>


<details><summary>ClipKwargs

</summary>


**ClipKwargs:**
##### `outputs.i.postprocessing.i.kwargs.min`<sub> float</sub>
minimum value for clipping



##### `outputs.i.postprocessing.i.kwargs.max`<sub> float</sub>
maximum value for clipping



</details>

**ScaleLinearDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[scale_linear]</sub> ≝ `scale_linear`




#### `outputs.i.postprocessing.i.kwargs`<sub> ScaleLinearKwargs</sub>


<details><summary>ScaleLinearKwargs

</summary>


**ScaleLinearKwargs:**
##### `outputs.i.postprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to scale jointly.
For example xy to scale the two image axes for 2d data jointly.
[*Example:*](#outputsipostprocessingikwargsaxes) 'xy'


Optional[str (RestrictCharacters(alphabet='czyx'); AfterValidator(validate_unique_entries))]

##### `outputs.i.postprocessing.i.kwargs.gain`<sub> Union[float, Sequence[float]]</sub> ≝ `1.0`
multiplicative factor



##### `outputs.i.postprocessing.i.kwargs.offset`<sub> Union[float, Sequence[float]]</sub> ≝ `0.0`
additive term



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
Mode for computing mean and variance.
|     mode    |             description              |
| ----------- | ------------------------------------ |
|   fixed     | Fixed values for mean and variance   |
| per_dataset | Compute for the entire dataset       |
| per_sample  | Compute for each sample individually |


Literal[fixed, per_dataset, per_sample]

##### `outputs.i.postprocessing.i.kwargs.axes`<sub> str</sub>
The subset of axes to normalize jointly.
For example `xy` to normalize the two image axes for 2d data jointly.
[*Example:*](#outputsipostprocessingikwargsaxes) 'xy'



##### `outputs.i.postprocessing.i.kwargs.mean`<sub> Union</sub> ≝ `None`
The mean value(s) to use for `mode: fixed`.
For example `[1.1, 2.2, 3.3]` in the case of a 3 channel image with `axes: xy`.
[*Example:*](#outputsipostprocessingikwargsmean) (1.1, 2.2, 3.3)


Union[float, Sequence[float] (MinLen(min_length=1)), None]

##### `outputs.i.postprocessing.i.kwargs.std`<sub> Union</sub> ≝ `None`
The standard deviation values to use for `mode: fixed`. Analogous to mean.
[*Example:*](#outputsipostprocessingikwargsstd) (0.1, 0.2, 0.3)


Union[float, Sequence[float] (MinLen(min_length=1)), None]

##### `outputs.i.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`
epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`.



</details>

**ScaleRangeDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[scale_range]</sub> ≝ `scale_range`




#### `outputs.i.postprocessing.i.kwargs`<sub> ScaleRangeKwargs</sub>


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `outputs.i.postprocessing.i.kwargs.mode`<sub> Literal[per_dataset, per_sample]</sub>
Mode for computing percentiles.
|     mode    |             description              |
| ----------- | ------------------------------------ |
| per_dataset | compute for the entire dataset       |
| per_sample  | compute for each sample individually |



##### `outputs.i.postprocessing.i.kwargs.axes`<sub> str</sub>
The subset of axes to normalize jointly.
For example xy to normalize the two image axes for 2d data jointly.
[*Example:*](#outputsipostprocessingikwargsaxes) 'xy'



##### `outputs.i.postprocessing.i.kwargs.min_percentile`<sub> Union[int, float]</sub> ≝ `0.0`
The lower percentile used to determine the value to align with zero.



##### `outputs.i.postprocessing.i.kwargs.max_percentile`<sub> Union[int, float]</sub> ≝ `100.0`
The upper percentile used to determine the value to align with one.
Has to be bigger than `min_percentile`.
The range is 1 to 100 instead of 0 to 100 to avoid mistakenly
accepting percentiles specified in the range 0.0 to 1.0.



##### `outputs.i.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability.
`out = (tensor - v_lower) / (v_upper - v_lower + eps)`;
with `v_lower,v_upper` values at the respective percentiles.



##### `outputs.i.postprocessing.i.kwargs.reference_tensor`<sub> Optional[TensorName]</sub> ≝ `None`
Tensor name to compute the percentiles from. Default: The tensor itself.
For any tensor in `inputs` only input tensor references are allowed.
For a tensor in `outputs` only input tensor refereences are allowed if `mode: per_dataset`



</details>

**ScaleMeanVarianceDescr:**
#### `outputs.i.postprocessing.i.name`<sub> Literal[scale_mean_variance]</sub> ≝ `scale_mean_variance`




#### `outputs.i.postprocessing.i.kwargs`<sub> ScaleMeanVarianceKwargs</sub>


<details><summary>ScaleMeanVarianceKwargs

</summary>


**ScaleMeanVarianceKwargs:**
##### `outputs.i.postprocessing.i.kwargs.mode`<sub> Literal[per_dataset, per_sample]</sub>
Mode for computing mean and variance.
|     mode    |             description              |
| ----------- | ------------------------------------ |
| per_dataset | Compute for the entire dataset       |
| per_sample  | Compute for each sample individually |



##### `outputs.i.postprocessing.i.kwargs.reference_tensor`<sub> TensorName</sub>
Name of tensor to match.



##### `outputs.i.postprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to scale jointly.
For example xy to normalize the two image axes for 2d data jointly.
Default: scale all non-batch axes jointly.
[*Example:*](#outputsipostprocessingikwargsaxes) 'xy'


Optional[str (RestrictCharacters(alphabet='czyx'); AfterValidator(validate_unique_entries))]

##### `outputs.i.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability:
"`out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean.



</details>

</details>

</details>

## `test_inputs`<sub> Sequence</sub>
∈📦 Test input tensors compatible with the `inputs` description for a **single test case**.
This means if your model has more than one input, you should provide one URL/relative path for each input.
Each test input should be a file with an ndarray in
[numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).
The extension must be '.npy'.

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix='.npy', case_sensitive=True))

</details>

## `test_outputs`<sub> Sequence</sub>
∈📦 Analog to `test_inputs`.

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix='.npy', case_sensitive=True))

</details>

## `timestamp`<sub> _internal.types.Datetime</sub>
Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat).



## `weights`<sub> WeightsDescr</sub>
The weights for this model.
Weights can be given for different formats, but should otherwise be equivalent.
The available weight formats determine which consumers can use this model.

<details><summary>WeightsDescr

</summary>


**WeightsDescr:**
### `weights.keras_hdf5`<sub> Optional[KerasHdf5WeightsDescr]</sub> ≝ `None`


<details><summary>Optional[KerasHdf5WeightsDescr]

</summary>


**KerasHdf5WeightsDescr:**
#### `weights.keras_hdf5.source`<sub> Union</sub>
∈📦 The weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.keras_hdf5.sha256`<sub> Optional</sub> ≝ `None`
SHA256 checksum of the source file


Optional[_internal.io_basics.Sha256]

#### `weights.keras_hdf5.attachments`<sub> Optional</sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.keras_hdf5.attachments.files`<sub> Sequence</sub> ≝ `[]`
∈📦 File attachments

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.keras_hdf5.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.keras_hdf5.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



##### `weights.keras_hdf5.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



##### `weights.keras_hdf5.authors.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightskeras_hdf5authorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.keras_hdf5.authors.i.name`<sub> str</sub>




##### `weights.keras_hdf5.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.keras_hdf5.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`
Dependency manager and dependency file, specified as `<dependency manager>:<relative file path>`.
[*Examples:*](#weightskeras_hdf5dependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.keras_hdf5.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightskeras_hdf5parent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.keras_hdf5.tensorflow_version`<sub> Optional</sub> ≝ `None`
TensorFlow version used to create these weights


Optional[_internal.version_type.Version]

</details>

### `weights.onnx`<sub> Optional[OnnxWeightsDescr]</sub> ≝ `None`


<details><summary>Optional[OnnxWeightsDescr]

</summary>


**OnnxWeightsDescr:**
#### `weights.onnx.source`<sub> Union</sub>
∈📦 The weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.onnx.sha256`<sub> Optional</sub> ≝ `None`
SHA256 checksum of the source file


Optional[_internal.io_basics.Sha256]

#### `weights.onnx.attachments`<sub> Optional</sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.onnx.attachments.files`<sub> Sequence</sub> ≝ `[]`
∈📦 File attachments

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.onnx.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.onnx.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



##### `weights.onnx.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



##### `weights.onnx.authors.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightsonnxauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.onnx.authors.i.name`<sub> str</sub>




##### `weights.onnx.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.onnx.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`
Dependency manager and dependency file, specified as `<dependency manager>:<relative file path>`.
[*Examples:*](#weightsonnxdependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.onnx.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightsonnxparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.onnx.opset_version`<sub> Optional[int (Ge(ge=7))]</sub> ≝ `None`
ONNX opset version



</details>

### `weights.pytorch_state_dict`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[PytorchStateDictWeightsDescr]

</summary>


**PytorchStateDictWeightsDescr:**
#### `weights.pytorch_state_dict.source`<sub> Union</sub>
∈📦 The weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.pytorch_state_dict.sha256`<sub> Optional</sub> ≝ `None`
SHA256 checksum of the source file


Optional[_internal.io_basics.Sha256]

#### `weights.pytorch_state_dict.attachments`<sub> Optional</sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.pytorch_state_dict.attachments.files`<sub> Sequence</sub> ≝ `[]`
∈📦 File attachments

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.pytorch_state_dict.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.pytorch_state_dict.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



##### `weights.pytorch_state_dict.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



##### `weights.pytorch_state_dict.authors.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightspytorch_state_dictauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.pytorch_state_dict.authors.i.name`<sub> str</sub>




##### `weights.pytorch_state_dict.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.pytorch_state_dict.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`
Dependency manager and dependency file, specified as `<dependency manager>:<relative file path>`.
[*Examples:*](#weightspytorch_state_dictdependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.pytorch_state_dict.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightspytorch_state_dictparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.pytorch_state_dict.architecture`<sub> Union</sub>
callable returning a torch.nn.Module instance.
Local implementation: `<relative path to file>:<identifier of implementation within the file>`.
Implementation in a dependency: `<dependency-package>.<[dependency-module]>.<identifier>`.
[*Examples:*](#weightspytorch_state_dictarchitecture) ['my_function.py:MyNetworkClass', 'my_module.submodule.get_my_model']


Union[CallableFromFile, CallableFromDepencency]

#### `weights.pytorch_state_dict.architecture_sha256`<sub> Optional</sub> ≝ `None`
The SHA256 of the architecture source file, if the architecture is not defined in a module listed in `dependencies`
You can drag and drop your file to this
[online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate a SHA256 in your browser.
Or you can generate a SHA256 checksum with Python's `hashlib`,
[here is a codesnippet](https://gist.github.com/FynnBe/e64460463df89439cff218bbf59c1100).


Optional[_internal.io_basics.Sha256]

#### `weights.pytorch_state_dict.kwargs`<sub> Dict[str, Any]</sub> ≝ `{}`
key word arguments for the `architecture` callable



#### `weights.pytorch_state_dict.pytorch_version`<sub> Optional</sub> ≝ `None`
Version of the PyTorch library used.
If `depencencies` is specified it should include pytorch and the verison has to match.
(`dependencies` overrules `pytorch_version`)


Optional[_internal.version_type.Version]

</details>

### `weights.tensorflow_js`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TensorflowJsWeightsDescr]

</summary>


**TensorflowJsWeightsDescr:**
#### `weights.tensorflow_js.source`<sub> Union</sub>
∈📦 The multi-file weights.
All required files/folders should be a zip archive.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.tensorflow_js.sha256`<sub> Optional</sub> ≝ `None`
SHA256 checksum of the source file


Optional[_internal.io_basics.Sha256]

#### `weights.tensorflow_js.attachments`<sub> Optional</sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.tensorflow_js.attachments.files`<sub> Sequence</sub> ≝ `[]`
∈📦 File attachments

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.tensorflow_js.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.tensorflow_js.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



##### `weights.tensorflow_js.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



##### `weights.tensorflow_js.authors.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightstensorflow_jsauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.tensorflow_js.authors.i.name`<sub> str</sub>




##### `weights.tensorflow_js.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.tensorflow_js.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`
Dependency manager and dependency file, specified as `<dependency manager>:<relative file path>`.
[*Examples:*](#weightstensorflow_jsdependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.tensorflow_js.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightstensorflow_jsparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.tensorflow_js.tensorflow_version`<sub> Optional</sub> ≝ `None`
Version of the TensorFlow library used.


Optional[_internal.version_type.Version]

</details>

### `weights.tensorflow_saved_model_bundle`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TensorflowSavedModelBundleWeightsDescr]

</summary>


**TensorflowSavedModelBundleWeightsDescr:**
#### `weights.tensorflow_saved_model_bundle.source`<sub> Union</sub>
∈📦 The weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.tensorflow_saved_model_bundle.sha256`<sub> Optional</sub> ≝ `None`
SHA256 checksum of the source file


Optional[_internal.io_basics.Sha256]

#### `weights.tensorflow_saved_model_bundle.attachments`<sub> Optional</sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.tensorflow_saved_model_bundle.attachments.files`<sub> Sequence</sub> ≝ `[]`
∈📦 File attachments

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.tensorflow_saved_model_bundle.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.tensorflow_saved_model_bundle.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



##### `weights.tensorflow_saved_model_bundle.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



##### `weights.tensorflow_saved_model_bundle.authors.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightstensorflow_saved_model_bundleauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.tensorflow_saved_model_bundle.authors.i.name`<sub> str</sub>




##### `weights.tensorflow_saved_model_bundle.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.tensorflow_saved_model_bundle.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`
Dependency manager and dependency file, specified as `<dependency manager>:<relative file path>`.
[*Examples:*](#weightstensorflow_saved_model_bundledependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.tensorflow_saved_model_bundle.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightstensorflow_saved_model_bundleparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.tensorflow_saved_model_bundle.tensorflow_version`<sub> Optional</sub> ≝ `None`
Version of the TensorFlow library used.


Optional[_internal.version_type.Version]

</details>

### `weights.torchscript`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TorchscriptWeightsDescr]

</summary>


**TorchscriptWeightsDescr:**
#### `weights.torchscript.source`<sub> Union</sub>
∈📦 The weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.torchscript.sha256`<sub> Optional</sub> ≝ `None`
SHA256 checksum of the source file


Optional[_internal.io_basics.Sha256]

#### `weights.torchscript.attachments`<sub> Optional</sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.torchscript.attachments.files`<sub> Sequence</sub> ≝ `[]`
∈📦 File attachments

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

#### `weights.torchscript.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_2.Author]]

</summary>


**generic.v0_2.Author:**
##### `weights.torchscript.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



##### `weights.torchscript.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



##### `weights.torchscript.authors.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightstorchscriptauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.torchscript.authors.i.name`<sub> str</sub>




##### `weights.torchscript.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.torchscript.dependencies`<sub> Optional[Dependencies]</sub> ≝ `None`
Dependency manager and dependency file, specified as `<dependency manager>:<relative file path>`.
[*Examples:*](#weightstorchscriptdependencies) ['conda:environment.yaml', 'maven:./pom.xml', 'pip:./requirements.txt']



#### `weights.torchscript.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightstorchscriptparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.torchscript.pytorch_version`<sub> Optional</sub> ≝ `None`
Version of the PyTorch library used.


Optional[_internal.version_type.Version]

</details>

</details>

## `attachments`<sub> Optional</sub> ≝ `None`
file and other attachments

<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
### `attachments.files`<sub> Sequence</sub> ≝ `[]`
∈📦 File attachments

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

## `cite`<sub> Sequence[generic.v0_2.CiteEntry]</sub> ≝ `[]`
citations

<details><summary>Sequence[generic.v0_2.CiteEntry]

</summary>


**generic.v0_2.CiteEntry:**
### `cite.i.text`<sub> str</sub>
free text description



### `cite.i.doi`<sub> Optional[_internal.types.Doi]</sub> ≝ `None`
A digital object identifier (DOI) is the prefered citation reference.
See https://www.doi.org/ for details. (alternatively specify `url`)



### `cite.i.url`<sub> Optional[str]</sub> ≝ `None`
URL to cite (preferably specify a `doi` instead)



</details>

## `config`<sub> Dict[str, YamlValue]</sub> ≝ `{}`
A field for custom configuration that can contain any keys not present in the RDF spec.
This means you should not store, for example, a github repo URL in `config` since we already have the
`git_repo` field defined in the spec.
Keys in `config` may be very specific to a tool or consumer software. To avoid conflicting definitions,
it is recommended to wrap added configuration into a sub-field named with the specific domain or tool name,
for example:
```yaml
config:
    bioimageio:  # here is the domain name
        my_custom_key: 3837283
        another_key:
            nested: value
    imagej:       # config specific to ImageJ
        macro_dir: path/to/macro/file
```
If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.
You may want to list linked files additionally under `attachments` to include them when packaging a resource
(packaging a resource means downloading/copying important linked files and creating a ZIP archive that contains
an altered rdf.yaml file with local references to the downloaded files)
[*Example:*](#config) {'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}



## `covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff')
[*Example:*](#covers) 'cover.png'

<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'); Predicate(is_absolute); )
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl

(union_mode='left_to_right'; WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

## `download_url`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`
URL to download the resource from (deprecated)



## `git_repo`<sub> Optional[str]</sub> ≝ `None`
A URL to the Git repository where the resource is being developed.
[*Example:*](#git_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



## `icon`<sub> Union</sub> ≝ `None`
An icon for illustration

<details><summary>Union[str*, Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
  (union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))
- None


</details>

## `id`<sub> Optional[ModelId]</sub> ≝ `None`
bioimage.io-wide unique resource identifier
assigned by bioimage.io; version **un**specific.



## `id_emoji`<sub> Optional</sub> ≝ `None`
UTF-8 emoji for display alongside the `id`.


Optional[str (Len(min_length=1, max_length=1); )]

## `links`<sub> Sequence[str]</sub> ≝ `[]`
IDs of other bioimage.io resources
[*Example:*](#links) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



## `maintainers`<sub> Sequence</sub> ≝ `[]`
Maintainers of this resource.
If not specified `authors` are maintainers and at least some of them should specify their `github_user` name

<details><summary>Sequence[generic.v0_2.Maintainer]

</summary>


**generic.v0_2.Maintainer:**
### `maintainers.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



### `maintainers.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



### `maintainers.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#maintainersiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `maintainers.i.name`<sub> Optional</sub> ≝ `None`



Optional[str (AfterValidator(_remove_slashes))]

### `maintainers.i.github_user`<sub> str</sub>




</details>

## `packaged_by`<sub> Sequence[generic.v0_2.Author]</sub> ≝ `[]`
The persons that have packaged and uploaded this model.
Only required if those persons differ from the `authors`.

<details><summary>Sequence[generic.v0_2.Author]

</summary>


**generic.v0_2.Author:**
### `packaged_by.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



### `packaged_by.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



### `packaged_by.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#packaged_byiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `packaged_by.i.name`<sub> str</sub>




### `packaged_by.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

## `parent`<sub> Optional[LinkedModel]</sub> ≝ `None`
The model from which this model is derived, e.g. by fine-tuning the weights.

<details><summary>Optional[LinkedModel]

</summary>


**LinkedModel:**
### `parent.id`<sub> ModelId</sub>
A valid model `id` from the bioimage.io collection.
[*Examples:*](#parentid) ['affable-shark', 'ambitious-sloth']



### `parent.version_number`<sub> Optional[int]</sub> ≝ `None`
version number (n-th published version, not the semantic version) of linked model



</details>

## `rdf_source`<sub> Optional</sub> ≝ `None`
Resource description file (RDF) source; used to keep track of where an rdf.yaml was loaded from.
Do not set this field in a YAML file.

<details><summary>Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right')]

</details>

## `run_mode`<sub> Optional[RunMode]</sub> ≝ `None`
Custom run mode for this model: for more complex prediction procedures like test time
data augmentation that currently cannot be expressed in the specification.
No standard run modes are defined yet.

<details><summary>Optional[RunMode]

</summary>


**RunMode:**
### `run_mode.name`<sub> Union[Literal[deepimagej], str]</sub>
Run mode name



### `run_mode.kwargs`<sub> Dict[str, Any]</sub> ≝ `{}`
Run mode specific key word arguments



</details>

## `sample_inputs`<sub> Sequence</sub> ≝ `[]`
∈📦 URLs/relative paths to sample inputs to illustrate possible inputs for the model,
for example stored as PNG or TIFF images.
The sample files primarily serve to inform a human user about an example use case

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

## `sample_outputs`<sub> Sequence</sub> ≝ `[]`
∈📦 URLs/relative paths to sample outputs corresponding to the `sample_inputs`.

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

## `tags`<sub> Sequence[str]</sub> ≝ `[]`
Associated tags
[*Example:*](#tags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



## `training_data`<sub> Union</sub> ≝ `None`
The dataset used to train this model

<details><summary>Union[dataset.v0_2.LinkedDataset, dataset.v0_2.DatasetDescr, None]

</summary>


**dataset.v0_2.LinkedDataset:**
### `training_data.id`<sub> dataset.v0_2.DatasetId</sub>
A valid dataset `id` from the bioimage.io collection.



### `training_data.version_number`<sub> Optional[int]</sub> ≝ `None`
version number (n-th published version, not the semantic version) of linked dataset



**dataset.v0_2.DatasetDescr:**
### `training_data.name`<sub> str</sub>
A human-friendly name of the resource description



### `training_data.description`<sub> str</sub>




### `training_data.covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff')
[*Example:*](#training_datacovers) 'cover.png'

<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'); Predicate(is_absolute); )
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl

(union_mode='left_to_right'; WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

### `training_data.id_emoji`<sub> Optional</sub> ≝ `None`
UTF-8 emoji for display alongside the `id`.


Optional[str (Len(min_length=1, max_length=1); )]

### `training_data.authors`<sub> Sequence[generic.v0_2.Author]</sub> ≝ `[]`
The authors are the creators of the RDF and the primary points of contact.

<details><summary>Sequence[generic.v0_2.Author]

</summary>


**generic.v0_2.Author:**
#### `training_data.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



#### `training_data.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



#### `training_data.authors.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#training_dataauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

#### `training_data.authors.i.name`<sub> str</sub>




#### `training_data.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

### `training_data.attachments`<sub> Optional</sub> ≝ `None`
file and other attachments

<details><summary>Optional[generic.v0_2.AttachmentsDescr]

</summary>


**generic.v0_2.AttachmentsDescr:**
#### `training_data.attachments.files`<sub> Sequence</sub> ≝ `[]`
∈📦 File attachments

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

### `training_data.cite`<sub> Sequence[generic.v0_2.CiteEntry]</sub> ≝ `[]`
citations

<details><summary>Sequence[generic.v0_2.CiteEntry]

</summary>


**generic.v0_2.CiteEntry:**
#### `training_data.cite.i.text`<sub> str</sub>
free text description



#### `training_data.cite.i.doi`<sub> Optional[_internal.types.Doi]</sub> ≝ `None`
A digital object identifier (DOI) is the prefered citation reference.
See https://www.doi.org/ for details. (alternatively specify `url`)



#### `training_data.cite.i.url`<sub> Optional[str]</sub> ≝ `None`
URL to cite (preferably specify a `doi` instead)



</details>

### `training_data.config`<sub> Dict[str, YamlValue]</sub> ≝ `{}`
A field for custom configuration that can contain any keys not present in the RDF spec.
This means you should not store, for example, a github repo URL in `config` since we already have the
`git_repo` field defined in the spec.
Keys in `config` may be very specific to a tool or consumer software. To avoid conflicting definitions,
it is recommended to wrap added configuration into a sub-field named with the specific domain or tool name,
for example:
```yaml
config:
    bioimageio:  # here is the domain name
        my_custom_key: 3837283
        another_key:
            nested: value
    imagej:       # config specific to ImageJ
        macro_dir: path/to/macro/file
```
If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.
You may want to list linked files additionally under `attachments` to include them when packaging a resource
(packaging a resource means downloading/copying important linked files and creating a ZIP archive that contains
an altered rdf.yaml file with local references to the downloaded files)
[*Example:*](#training_dataconfig) {'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}



### `training_data.download_url`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`
URL to download the resource from (deprecated)



### `training_data.git_repo`<sub> Optional[str]</sub> ≝ `None`
A URL to the Git repository where the resource is being developed.
[*Example:*](#training_datagit_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



### `training_data.icon`<sub> Union</sub> ≝ `None`
An icon for illustration

<details><summary>Union[str*, Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
  (union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))
- None


</details>

### `training_data.links`<sub> Sequence[str]</sub> ≝ `[]`
IDs of other bioimage.io resources
[*Example:*](#training_datalinks) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



### `training_data.uploader`<sub> Optional[generic.v0_2.Uploader]</sub> ≝ `None`
The person who uploaded the model (e.g. to bioimage.io)

<details><summary>Optional[generic.v0_2.Uploader]

</summary>


**generic.v0_2.Uploader:**
#### `training_data.uploader.email`<sub> Email</sub>
Email



#### `training_data.uploader.name`<sub> Optional</sub> ≝ `None`
name


Optional[str (AfterValidator(_remove_slashes))]

</details>

### `training_data.maintainers`<sub> Sequence</sub> ≝ `[]`
Maintainers of this resource.
If not specified `authors` are maintainers and at least some of them should specify their `github_user` name

<details><summary>Sequence[generic.v0_2.Maintainer]

</summary>


**generic.v0_2.Maintainer:**
#### `training_data.maintainers.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



#### `training_data.maintainers.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



#### `training_data.maintainers.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#training_datamaintainersiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

#### `training_data.maintainers.i.name`<sub> Optional</sub> ≝ `None`



Optional[str (AfterValidator(_remove_slashes))]

#### `training_data.maintainers.i.github_user`<sub> str</sub>




</details>

### `training_data.rdf_source`<sub> Optional</sub> ≝ `None`
Resource description file (RDF) source; used to keep track of where an rdf.yaml was loaded from.
Do not set this field in a YAML file.

<details><summary>Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right')]

</details>

### `training_data.tags`<sub> Sequence[str]</sub> ≝ `[]`
Associated tags
[*Example:*](#training_datatags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



### `training_data.version`<sub> Optional</sub> ≝ `None`
The version of the resource following SemVer 2.0.


Optional[_internal.version_type.Version]

### `training_data.version_number`<sub> Optional[int]</sub> ≝ `None`
version number (n-th published version, not the semantic version)



### `training_data.format_version`<sub> Literal[0.2.4]</sub> ≝ `0.2.4`
The format version of this resource specification
(not the `version` of the resource description)
When creating a new resource always use the latest micro/patch version described here.
The `format_version` is important for any consumer software to understand how to parse the fields.



### `training_data.badges`<sub> Sequence</sub> ≝ `[]`
badges associated with this resource

<details><summary>Sequence[generic.v0_2.BadgeDescr]

</summary>


**generic.v0_2.BadgeDescr:**
#### `training_data.badges.i.label`<sub> str</sub>
badge label to display on hover
[*Example:*](#training_databadgesilabel) 'Open in Colab'



#### `training_data.badges.i.icon`<sub> Union</sub> ≝ `None`
badge icon
[*Example:*](#training_databadgesiicon) 'https://colab.research.google.com/assets/colab-badge.svg'

<details><summary>Union[Union[Path*, _internal.io.RelativeFilePath]*, _internal.url.HttpUrl, Url*, None]

</summary>

Union of
- Union[Path (PathType(path_type='file'); ), _internal.io.RelativeFilePath]
  (AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])
- None


</details>

#### `training_data.badges.i.url`<sub> _internal.url.HttpUrl</sub>
target URL
[*Example:*](#training_databadgesiurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



</details>

### `training_data.documentation`<sub> Optional</sub> ≝ `None`
∈📦 URL or relative path to a markdown file with additional documentation.
The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
[*Examples:*](#training_datadocumentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']

<details><summary>Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f05d14a4680>, return_type=PydanticUndefined, when_used='unless-none'))]

</details>

### `training_data.license`<sub> Union</sub> ≝ `None`
A [SPDX license identifier](https://spdx.org/licenses/).
We do not support custom license beyond the SPDX license list, if you need that please
[open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose
) to discuss your intentions with the community.
[*Examples:*](#training_datalicense) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId, str, None]

### `training_data.type`<sub> Literal[dataset]</sub> ≝ `dataset`




### `training_data.id`<sub> Optional[dataset.v0_2.DatasetId]</sub> ≝ `None`
bioimage.io-wide unique resource identifier
assigned by bioimage.io; version **un**specific.



### `training_data.source`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`
"URL to the source of the dataset.



</details>

## `uploader`<sub> Optional[generic.v0_2.Uploader]</sub> ≝ `None`
The person who uploaded the model (e.g. to bioimage.io)

<details><summary>Optional[generic.v0_2.Uploader]

</summary>


**generic.v0_2.Uploader:**
### `uploader.email`<sub> Email</sub>
Email



### `uploader.name`<sub> Optional</sub> ≝ `None`
name


Optional[str (AfterValidator(_remove_slashes))]

</details>

## `version`<sub> Optional</sub> ≝ `None`
The version of the resource following SemVer 2.0.


Optional[_internal.version_type.Version]

## `version_number`<sub> Optional[int]</sub> ≝ `None`
version number (n-th published version, not the semantic version)



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
### `parent.id`
- affable-shark
- ambitious-sloth

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

