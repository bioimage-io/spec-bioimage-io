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
| `field` ≝ `default` | Default field values are indicated after '≝' and make a field optional. However, `type` and `format_version` alwyas need to be set for resource descriptions written as YAML files and determine which bioimage.io specification applies. They are optional only when creating a resource description in Python code using the appropriate, `type` and `format_version` specific class (here: [bioimageio.spec.model.v0_4.ModelDescr](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/model/v0_4.html#ModelDescr)).|
| `field` ≝ 🡇 | Default field value is not displayed in-line, but in the code block below. |
are included when packaging the resource to a .zip archive. The resource description YAML file (RDF) is always included as well as 'rdf.yaml'. |

## `type`<sub> Literal[model]</sub>
Specialized resource type 'model'



## `format_version`<sub> Literal[0.4.10]</sub>
Version of the bioimage.io model description specification used.
When creating a new model always use the latest micro/patch version described here.
The `format_version` is important for any consumer software to understand how to parse the fields.



## `authors`<sub> list</sub>
The authors are the creators of the model RDF and the primary points of contact.

<details><summary>list[bioimageio.spec.generic.v0_2.Author]

</summary>


**generic.v0_2.Author:**
### `authors.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



### `authors.email`<sub> Email | None</sub> ≝ `None`
Email



### `authors.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#authorsorcid) '0000-0001-2345-6789'



### `authors.name`<sub> str</sub>




### `authors.github_user`<sub> str | None</sub> ≝ `None`




</details>

## `description`<sub> str</sub>




## `documentation`<sub> Union</sub>
FileSource: 
URL or relative path to a markdown file with additional documentation.
The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
The documentation should include a '[#[#]]# Validation' (sub)section
with details on how to quantitatively validate the model on unseen data.
[*Examples:*](#documentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

## `inputs`<sub> list</sub>
Describes the input tensors expected by this model.

<details><summary>list[bioimageio.spec.model.v0_4.InputTensorDescr]

</summary>


**InputTensorDescr:**
### `inputs.name`<sub> TensorName</sub>
Tensor name. No duplicates are allowed.



### `inputs.description`<sub> str</sub> ≝ ``




### `inputs.axes`<sub> str</sub>
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



### `inputs.data_range`<sub> tuple</sub> ≝ `None`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
If not specified, the full data range that can be expressed in `data_type` is allowed.

<details><summary>tuple[typing.Annotated[float, AllowInfNan(allow_inf_nan=True)], typing.Annotated[float, AllowInfNan(allow_inf_nan=True)]] | None

</summary>

tuple[typing.Annotated[float, AllowInfNan(allow_inf_nan=True)], typing.Annotated[float, AllowInfNan(allow_inf_nan=True)]] | None

</details>

### `inputs.data_type`<sub> Literal[float32, uint8, uint16]</sub>
For now an input tensor is expected to be given as `float32`.
The data flow in bioimage.io models is explained
[in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).



### `inputs.shape`<sub> Union</sub>
Specification of input tensor shape.
[*Examples:*](#inputsshape) [(1, 512, 512, 1), {'min': (1, 64, 64, 1), 'step': (0, 32, 32, 0)}]

<details><summary>Union[Sequence[int], ParameterizedInputShape]

</summary>


**ParameterizedInputShape:**
#### `inputs.shape.min`<sub> list[int]</sub>
The minimum input shape



#### `inputs.shape.step`<sub> list[int]</sub>
The minimum shape change



</details>

### `inputs.preprocessing`<sub> list</sub> ≝ `[]`
Description of how this input should be preprocessed.

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec.model.v0_4.BinarizeDescr, bioimageio.spec.model.v0_4.ClipDescr, bioimageio.spec.model.v0_4.ScaleLinearDescr, bioimageio.spec.model.v0_4.SigmoidDescr, bioimageio.spec.model.v0_4.ZeroMeanUnitVarianceDescr, bioimageio.spec.model.v0_4.ScaleRangeDescr], Discriminator(discriminator='name', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec.model.v0_4.BinarizeDescr, bioimageio.spec.model.v0_4.ClipDescr, bioimageio.spec.model.v0_4.ScaleLinearDescr, bioimageio.spec.model.v0_4.SigmoidDescr, bioimageio.spec.model.v0_4.ZeroMeanUnitVarianceDescr, bioimageio.spec.model.v0_4.ScaleRangeDescr], Discriminator(discriminator='name', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

**BinarizeDescr:**
#### `inputs.preprocessing.name`<sub> Literal[binarize]</sub>




#### `inputs.preprocessing.kwargs`<sub> BinarizeKwargs</sub>


<details><summary>BinarizeKwargs

</summary>


**BinarizeKwargs:**
##### `inputs.preprocessing.kwargs.threshold`<sub> float</sub>
The fixed threshold



</details>

**ClipDescr:**
#### `inputs.preprocessing.name`<sub> Literal[clip]</sub>




#### `inputs.preprocessing.kwargs`<sub> ClipKwargs</sub>


<details><summary>ClipKwargs

</summary>


**ClipKwargs:**
##### `inputs.preprocessing.kwargs.min`<sub> float</sub>
minimum value for clipping



##### `inputs.preprocessing.kwargs.max`<sub> float</sub>
maximum value for clipping



</details>

**ScaleLinearDescr:**
#### `inputs.preprocessing.name`<sub> Literal[scale_linear]</sub>




#### `inputs.preprocessing.kwargs`<sub> ScaleLinearKwargs</sub>


<details><summary>ScaleLinearKwargs

</summary>


**ScaleLinearKwargs:**
##### `inputs.preprocessing.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to scale jointly.
For example xy to scale the two image axes for 2d data jointly.
[*Example:*](#inputspreprocessingkwargsaxes) 'xy'


Optional[str (RestrictCharacters(alphabet='czyx'); AfterValidator(validate_unique_entries))]

##### `inputs.preprocessing.kwargs.gain`<sub> float | list[float]</sub> ≝ `1.0`
multiplicative factor



##### `inputs.preprocessing.kwargs.offset`<sub> float | list[float]</sub> ≝ `0.0`
additive term



</details>

**SigmoidDescr:**
#### `inputs.preprocessing.name`<sub> Literal[sigmoid]</sub>




**ZeroMeanUnitVarianceDescr:**
#### `inputs.preprocessing.name`<sub> Literal[zero_mean_unit_variance]</sub>




#### `inputs.preprocessing.kwargs`<sub> ZeroMeanUnitVarianceKwargs</sub>


<details><summary>ZeroMeanUnitVarianceKwargs

</summary>


**ZeroMeanUnitVarianceKwargs:**
##### `inputs.preprocessing.kwargs.mode`<sub> Literal</sub> ≝ `fixed`
Mode for computing mean and variance.
|     mode    |             description              |
| ----------- | ------------------------------------ |
|   fixed     | Fixed values for mean and variance   |
| per_dataset | Compute for the entire dataset       |
| per_sample  | Compute for each sample individually |


Literal[fixed, per_dataset, per_sample]

##### `inputs.preprocessing.kwargs.axes`<sub> str</sub>
The subset of axes to normalize jointly.
For example `xy` to normalize the two image axes for 2d data jointly.
[*Example:*](#inputspreprocessingkwargsaxes) 'xy'



##### `inputs.preprocessing.kwargs.mean`<sub> Union</sub> ≝ `None`
The mean value(s) to use for `mode: fixed`.
For example `[1.1, 2.2, 3.3]` in the case of a 3 channel image with `axes: xy`.
[*Example:*](#inputspreprocessingkwargsmean) (1.1, 2.2, 3.3)


Union[float, list[float] (MinLen(min_length=1)), None]

##### `inputs.preprocessing.kwargs.std`<sub> Union</sub> ≝ `None`
The standard deviation values to use for `mode: fixed`. Analogous to mean.
[*Example:*](#inputspreprocessingkwargsstd) (0.1, 0.2, 0.3)


Union[float, list[float] (MinLen(min_length=1)), None]

##### `inputs.preprocessing.kwargs.eps`<sub> float</sub> ≝ `1e-06`
epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`.



</details>

**ScaleRangeDescr:**
#### `inputs.preprocessing.name`<sub> Literal[scale_range]</sub>




#### `inputs.preprocessing.kwargs`<sub> ScaleRangeKwargs</sub>


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `inputs.preprocessing.kwargs.mode`<sub> Literal[per_dataset, per_sample]</sub>
Mode for computing percentiles.
|     mode    |             description              |
| ----------- | ------------------------------------ |
| per_dataset | compute for the entire dataset       |
| per_sample  | compute for each sample individually |



##### `inputs.preprocessing.kwargs.axes`<sub> str</sub>
The subset of axes to normalize jointly.
For example xy to normalize the two image axes for 2d data jointly.
[*Example:*](#inputspreprocessingkwargsaxes) 'xy'



##### `inputs.preprocessing.kwargs.min_percentile`<sub> int | float</sub> ≝ `0.0`
The lower percentile used to determine the value to align with zero.



##### `inputs.preprocessing.kwargs.max_percentile`<sub> int | float</sub> ≝ `100.0`
The upper percentile used to determine the value to align with one.
Has to be bigger than `min_percentile`.
The range is 1 to 100 instead of 0 to 100 to avoid mistakenly
accepting percentiles specified in the range 0.0 to 1.0.



##### `inputs.preprocessing.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability.
`out = (tensor - v_lower) / (v_upper - v_lower + eps)`;
with `v_lower,v_upper` values at the respective percentiles.



##### `inputs.preprocessing.kwargs.reference_tensor`<sub> TensorName | None</sub> ≝ `None`
Tensor name to compute the percentiles from. Default: The tensor itself.
For any tensor in `inputs` only input tensor references are allowed.
For a tensor in `outputs` only input tensor refereences are allowed if `mode: per_dataset`



</details>

</details>

</details>

## `license`<sub> _internal.license_id.LicenseId |</sub>
A [SPDX license identifier](https://spdx.org/licenses/).
We do notsupport custom license beyond the SPDX license list, if you need that please
[open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose
) to discuss your intentions with the community.
[*Examples:*](#license) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


_internal.license_id.LicenseId | str

## `name`<sub> str</sub>
A human-readable name of this model.
It should be no longer than 64 characters and only contain letter, number, underscore, minus or space characters.



## `outputs`<sub> list</sub>
Describes the output tensors.

<details><summary>list[bioimageio.spec.model.v0_4.OutputTensorDescr]

</summary>


**OutputTensorDescr:**
### `outputs.name`<sub> TensorName</sub>
Tensor name. No duplicates are allowed.



### `outputs.description`<sub> str</sub> ≝ ``




### `outputs.axes`<sub> str</sub>
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



### `outputs.data_range`<sub> tuple</sub> ≝ `None`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
If not specified, the full data range that can be expressed in `data_type` is allowed.

<details><summary>tuple[typing.Annotated[float, AllowInfNan(allow_inf_nan=True)], typing.Annotated[float, AllowInfNan(allow_inf_nan=True)]] | None

</summary>

tuple[typing.Annotated[float, AllowInfNan(allow_inf_nan=True)], typing.Annotated[float, AllowInfNan(allow_inf_nan=True)]] | None

</details>

### `outputs.data_type`<sub> Literal</sub>
Data type.
The data flow in bioimage.io models is explained
[in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).


Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

### `outputs.shape`<sub> Union</sub>
Output tensor shape.

<details><summary>Union[Sequence[int], ImplicitOutputShape]

</summary>


**ImplicitOutputShape:**
#### `outputs.shape.reference_tensor`<sub> TensorName</sub>
Name of the reference tensor.



#### `outputs.shape.scale`<sub> list[float | None]</sub>
output_pix/input_pix for each dimension.
'null' values indicate new dimensions, whose length is defined by 2*`offset`



#### `outputs.shape.offset`<sub> list</sub>
Position of origin wrt to input.


list[typing.Union[int, typing.Annotated[float, MultipleOf(multiple_of=0.5)]]]

</details>

### `outputs.halo`<sub> Optional[Sequence[int]]</sub> ≝ `None`
The `halo` that should be cropped from the output tensor to avoid boundary effects.
The `halo` is to be cropped from both sides, i.e. `shape_after_crop = shape - 2 * halo`.
To document a `halo` that is already cropped by the model `shape.offset` has to be used instead.



### `outputs.postprocessing`<sub> list</sub> ≝ `[]`
Description of how this output should be postprocessed.

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec.model.v0_4.BinarizeDescr, bioimageio.spec.model.v0_4.ClipDescr, bioimageio.spec.model.v0_4.ScaleLinearDescr, bioimageio.spec.model.v0_4.SigmoidDescr, bioimageio.spec.model.v0_4.ZeroMeanUnitVarianceDescr, bioimageio.spec.model.v0_4.ScaleRangeDescr, bioimageio.spec.model.v0_4.ScaleMeanVarianceDescr], Discriminator(discriminator='name', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec.model.v0_4.BinarizeDescr, bioimageio.spec.model.v0_4.ClipDescr, bioimageio.spec.model.v0_4.ScaleLinearDescr, bioimageio.spec.model.v0_4.SigmoidDescr, bioimageio.spec.model.v0_4.ZeroMeanUnitVarianceDescr, bioimageio.spec.model.v0_4.ScaleRangeDescr, bioimageio.spec.model.v0_4.ScaleMeanVarianceDescr], Discriminator(discriminator='name', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

**BinarizeDescr:**
#### `outputs.postprocessing.name`<sub> Literal[binarize]</sub>




#### `outputs.postprocessing.kwargs`<sub> BinarizeKwargs</sub>


<details><summary>BinarizeKwargs

</summary>


**BinarizeKwargs:**
##### `outputs.postprocessing.kwargs.threshold`<sub> float</sub>
The fixed threshold



</details>

**ClipDescr:**
#### `outputs.postprocessing.name`<sub> Literal[clip]</sub>




#### `outputs.postprocessing.kwargs`<sub> ClipKwargs</sub>


<details><summary>ClipKwargs

</summary>


**ClipKwargs:**
##### `outputs.postprocessing.kwargs.min`<sub> float</sub>
minimum value for clipping



##### `outputs.postprocessing.kwargs.max`<sub> float</sub>
maximum value for clipping



</details>

**ScaleLinearDescr:**
#### `outputs.postprocessing.name`<sub> Literal[scale_linear]</sub>




#### `outputs.postprocessing.kwargs`<sub> ScaleLinearKwargs</sub>


<details><summary>ScaleLinearKwargs

</summary>


**ScaleLinearKwargs:**
##### `outputs.postprocessing.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to scale jointly.
For example xy to scale the two image axes for 2d data jointly.
[*Example:*](#outputspostprocessingkwargsaxes) 'xy'


Optional[str (RestrictCharacters(alphabet='czyx'); AfterValidator(validate_unique_entries))]

##### `outputs.postprocessing.kwargs.gain`<sub> float | list[float]</sub> ≝ `1.0`
multiplicative factor



##### `outputs.postprocessing.kwargs.offset`<sub> float | list[float]</sub> ≝ `0.0`
additive term



</details>

**SigmoidDescr:**
#### `outputs.postprocessing.name`<sub> Literal[sigmoid]</sub>




**ZeroMeanUnitVarianceDescr:**
#### `outputs.postprocessing.name`<sub> Literal[zero_mean_unit_variance]</sub>




#### `outputs.postprocessing.kwargs`<sub> ZeroMeanUnitVarianceKwargs</sub>


<details><summary>ZeroMeanUnitVarianceKwargs

</summary>


**ZeroMeanUnitVarianceKwargs:**
##### `outputs.postprocessing.kwargs.mode`<sub> Literal</sub> ≝ `fixed`
Mode for computing mean and variance.
|     mode    |             description              |
| ----------- | ------------------------------------ |
|   fixed     | Fixed values for mean and variance   |
| per_dataset | Compute for the entire dataset       |
| per_sample  | Compute for each sample individually |


Literal[fixed, per_dataset, per_sample]

##### `outputs.postprocessing.kwargs.axes`<sub> str</sub>
The subset of axes to normalize jointly.
For example `xy` to normalize the two image axes for 2d data jointly.
[*Example:*](#outputspostprocessingkwargsaxes) 'xy'



##### `outputs.postprocessing.kwargs.mean`<sub> Union</sub> ≝ `None`
The mean value(s) to use for `mode: fixed`.
For example `[1.1, 2.2, 3.3]` in the case of a 3 channel image with `axes: xy`.
[*Example:*](#outputspostprocessingkwargsmean) (1.1, 2.2, 3.3)


Union[float, list[float] (MinLen(min_length=1)), None]

##### `outputs.postprocessing.kwargs.std`<sub> Union</sub> ≝ `None`
The standard deviation values to use for `mode: fixed`. Analogous to mean.
[*Example:*](#outputspostprocessingkwargsstd) (0.1, 0.2, 0.3)


Union[float, list[float] (MinLen(min_length=1)), None]

##### `outputs.postprocessing.kwargs.eps`<sub> float</sub> ≝ `1e-06`
epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`.



</details>

**ScaleRangeDescr:**
#### `outputs.postprocessing.name`<sub> Literal[scale_range]</sub>




#### `outputs.postprocessing.kwargs`<sub> ScaleRangeKwargs</sub>


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `outputs.postprocessing.kwargs.mode`<sub> Literal[per_dataset, per_sample]</sub>
Mode for computing percentiles.
|     mode    |             description              |
| ----------- | ------------------------------------ |
| per_dataset | compute for the entire dataset       |
| per_sample  | compute for each sample individually |



##### `outputs.postprocessing.kwargs.axes`<sub> str</sub>
The subset of axes to normalize jointly.
For example xy to normalize the two image axes for 2d data jointly.
[*Example:*](#outputspostprocessingkwargsaxes) 'xy'



##### `outputs.postprocessing.kwargs.min_percentile`<sub> int | float</sub> ≝ `0.0`
The lower percentile used to determine the value to align with zero.



##### `outputs.postprocessing.kwargs.max_percentile`<sub> int | float</sub> ≝ `100.0`
The upper percentile used to determine the value to align with one.
Has to be bigger than `min_percentile`.
The range is 1 to 100 instead of 0 to 100 to avoid mistakenly
accepting percentiles specified in the range 0.0 to 1.0.



##### `outputs.postprocessing.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability.
`out = (tensor - v_lower) / (v_upper - v_lower + eps)`;
with `v_lower,v_upper` values at the respective percentiles.



##### `outputs.postprocessing.kwargs.reference_tensor`<sub> TensorName | None</sub> ≝ `None`
Tensor name to compute the percentiles from. Default: The tensor itself.
For any tensor in `inputs` only input tensor references are allowed.
For a tensor in `outputs` only input tensor refereences are allowed if `mode: per_dataset`



</details>

**ScaleMeanVarianceDescr:**
#### `outputs.postprocessing.name`<sub> Literal[scale_mean_variance]</sub>




#### `outputs.postprocessing.kwargs`<sub> ScaleMeanVarianceKwargs</sub>


<details><summary>ScaleMeanVarianceKwargs

</summary>


**ScaleMeanVarianceKwargs:**
##### `outputs.postprocessing.kwargs.mode`<sub> Literal[per_dataset, per_sample]</sub>
Mode for computing mean and variance.
|     mode    |             description              |
| ----------- | ------------------------------------ |
| per_dataset | Compute for the entire dataset       |
| per_sample  | Compute for each sample individually |



##### `outputs.postprocessing.kwargs.reference_tensor`<sub> TensorName</sub>
Name of tensor to match.



##### `outputs.postprocessing.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to scale jointly.
For example xy to normalize the two image axes for 2d data jointly.
Default: scale all non-batch axes jointly.
[*Example:*](#outputspostprocessingkwargsaxes) 'xy'


Optional[str (RestrictCharacters(alphabet='czyx'); AfterValidator(validate_unique_entries))]

##### `outputs.postprocessing.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability:
"`out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean.



</details>

</details>

</details>

## `test_inputs`<sub> list</sub>
Test input tensors compatible with the `inputs` description for a **single test case**.
This means if your model has more than one input, you should provide one URL/relative path for each input.
Each test input should be a file with an ndarray in
[numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).
The extension must be '.npy'.

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix='.npy', case_sensitive=True, allow_any_parent_suffix=False)]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix='.npy', case_sensitive=True, allow_any_parent_suffix=False)]]

</details>

## `test_outputs`<sub> list</sub>
Analog to `test_inputs`.

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix='.npy', case_sensitive=True, allow_any_parent_suffix=False)]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix='.npy', case_sensitive=True, allow_any_parent_suffix=False)]]

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
### `weights.keras_hdf5`<sub> KerasHdf5WeightsDescr | None</sub> ≝ `None`


<details><summary>KerasHdf5WeightsDescr | None

</summary>


**KerasHdf5WeightsDescr:**
#### `weights.keras_hdf5.source`<sub> Union</sub>
FileSource: The weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.keras_hdf5.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.keras_hdf5.attachments`<sub> generic.v0_2.AttachmentsDescr | </sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>generic.v0_2.AttachmentsDescr | None

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.keras_hdf5.attachments.files`<sub> list</sub> ≝ `[]`
File attachments

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</details>

</details>

#### `weights.keras_hdf5.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_2.Author] | None

</summary>


**generic.v0_2.Author:**
##### `weights.keras_hdf5.authors.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



##### `weights.keras_hdf5.authors.email`<sub> Email | None</sub> ≝ `None`
Email



##### `weights.keras_hdf5.authors.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightskeras_hdf5authorsorcid) '0000-0001-2345-6789'



##### `weights.keras_hdf5.authors.name`<sub> str</sub>




##### `weights.keras_hdf5.authors.github_user`<sub> str | None</sub> ≝ `None`




</details>

#### `weights.keras_hdf5.dependencies`<sub> Dependencies | None</sub> ≝ `None`
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

#### `weights.keras_hdf5.tensorflow_version`<sub> _internal.version_type.Version |</sub> ≝ `None`
TensorFlow version used to create these weights


_internal.version_type.Version | None

</details>

### `weights.onnx`<sub> OnnxWeightsDescr | None</sub> ≝ `None`


<details><summary>OnnxWeightsDescr | None

</summary>


**OnnxWeightsDescr:**
#### `weights.onnx.source`<sub> Union</sub>
FileSource: The weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.onnx.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.onnx.attachments`<sub> generic.v0_2.AttachmentsDescr | </sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>generic.v0_2.AttachmentsDescr | None

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.onnx.attachments.files`<sub> list</sub> ≝ `[]`
File attachments

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</details>

</details>

#### `weights.onnx.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_2.Author] | None

</summary>


**generic.v0_2.Author:**
##### `weights.onnx.authors.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



##### `weights.onnx.authors.email`<sub> Email | None</sub> ≝ `None`
Email



##### `weights.onnx.authors.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightsonnxauthorsorcid) '0000-0001-2345-6789'



##### `weights.onnx.authors.name`<sub> str</sub>




##### `weights.onnx.authors.github_user`<sub> str | None</sub> ≝ `None`




</details>

#### `weights.onnx.dependencies`<sub> Dependencies | None</sub> ≝ `None`
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

### `weights.pytorch_state_dict`<sub> PytorchStateDictWeightsDescr | N</sub> ≝ `None`


<details><summary>PytorchStateDictWeightsDescr | None

</summary>


**PytorchStateDictWeightsDescr:**
#### `weights.pytorch_state_dict.source`<sub> Union</sub>
FileSource: The weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.pytorch_state_dict.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.pytorch_state_dict.attachments`<sub> generic.v0_2.AttachmentsDescr | </sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>generic.v0_2.AttachmentsDescr | None

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.pytorch_state_dict.attachments.files`<sub> list</sub> ≝ `[]`
File attachments

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</details>

</details>

#### `weights.pytorch_state_dict.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_2.Author] | None

</summary>


**generic.v0_2.Author:**
##### `weights.pytorch_state_dict.authors.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



##### `weights.pytorch_state_dict.authors.email`<sub> Email | None</sub> ≝ `None`
Email



##### `weights.pytorch_state_dict.authors.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightspytorch_state_dictauthorsorcid) '0000-0001-2345-6789'



##### `weights.pytorch_state_dict.authors.name`<sub> str</sub>




##### `weights.pytorch_state_dict.authors.github_user`<sub> str | None</sub> ≝ `None`




</details>

#### `weights.pytorch_state_dict.dependencies`<sub> Dependencies | None</sub> ≝ `None`
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

#### `weights.pytorch_state_dict.architecture_sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
The SHA256 of the architecture source file, if the architecture is not defined in a module listed in `dependencies`
You can drag and drop your file to this
[online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate a SHA256 in your browser.
Or you can generate a SHA256 checksum with Python's `hashlib`,
[here is a codesnippet](https://gist.github.com/FynnBe/e64460463df89439cff218bbf59c1100).


_internal.io_basics.Sha256 | None

#### `weights.pytorch_state_dict.kwargs`<sub> dict[str, typing.Any]</sub> ≝ `{}`
key word arguments for the `architecture` callable



#### `weights.pytorch_state_dict.pytorch_version`<sub> _internal.version_type.Version |</sub> ≝ `None`
Version of the PyTorch library used.
If `depencencies` is specified it should include pytorch and the verison has to match.
(`dependencies` overrules `pytorch_version`)


_internal.version_type.Version | None

</details>

### `weights.tensorflow_js`<sub> TensorflowJsWeightsDescr | None</sub> ≝ `None`


<details><summary>TensorflowJsWeightsDescr | None

</summary>


**TensorflowJsWeightsDescr:**
#### `weights.tensorflow_js.source`<sub> Union</sub>
FileSource: 
The multi-file weights.
All required files/folders should be a zip archive.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.tensorflow_js.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.tensorflow_js.attachments`<sub> generic.v0_2.AttachmentsDescr | </sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>generic.v0_2.AttachmentsDescr | None

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.tensorflow_js.attachments.files`<sub> list</sub> ≝ `[]`
File attachments

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</details>

</details>

#### `weights.tensorflow_js.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_2.Author] | None

</summary>


**generic.v0_2.Author:**
##### `weights.tensorflow_js.authors.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



##### `weights.tensorflow_js.authors.email`<sub> Email | None</sub> ≝ `None`
Email



##### `weights.tensorflow_js.authors.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightstensorflow_jsauthorsorcid) '0000-0001-2345-6789'



##### `weights.tensorflow_js.authors.name`<sub> str</sub>




##### `weights.tensorflow_js.authors.github_user`<sub> str | None</sub> ≝ `None`




</details>

#### `weights.tensorflow_js.dependencies`<sub> Dependencies | None</sub> ≝ `None`
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

#### `weights.tensorflow_js.tensorflow_version`<sub> _internal.version_type.Version |</sub> ≝ `None`
Version of the TensorFlow library used.


_internal.version_type.Version | None

</details>

### `weights.tensorflow_saved_model_bundle`<sub> TensorflowSavedModelBundleWeight</sub> ≝ `None`


<details><summary>TensorflowSavedModelBundleWeightsDescr | None

</summary>


**TensorflowSavedModelBundleWeightsDescr:**
#### `weights.tensorflow_saved_model_bundle.source`<sub> Union</sub>
FileSource: The weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.tensorflow_saved_model_bundle.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.tensorflow_saved_model_bundle.attachments`<sub> generic.v0_2.AttachmentsDescr | </sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>generic.v0_2.AttachmentsDescr | None

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.tensorflow_saved_model_bundle.attachments.files`<sub> list</sub> ≝ `[]`
File attachments

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</details>

</details>

#### `weights.tensorflow_saved_model_bundle.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_2.Author] | None

</summary>


**generic.v0_2.Author:**
##### `weights.tensorflow_saved_model_bundle.authors.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



##### `weights.tensorflow_saved_model_bundle.authors.email`<sub> Email | None</sub> ≝ `None`
Email



##### `weights.tensorflow_saved_model_bundle.authors.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightstensorflow_saved_model_bundleauthorsorcid) '0000-0001-2345-6789'



##### `weights.tensorflow_saved_model_bundle.authors.name`<sub> str</sub>




##### `weights.tensorflow_saved_model_bundle.authors.github_user`<sub> str | None</sub> ≝ `None`




</details>

#### `weights.tensorflow_saved_model_bundle.dependencies`<sub> Dependencies | None</sub> ≝ `None`
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

#### `weights.tensorflow_saved_model_bundle.tensorflow_version`<sub> _internal.version_type.Version |</sub> ≝ `None`
Version of the TensorFlow library used.


_internal.version_type.Version | None

</details>

### `weights.torchscript`<sub> TorchscriptWeightsDescr | None</sub> ≝ `None`


<details><summary>TorchscriptWeightsDescr | None

</summary>


**TorchscriptWeightsDescr:**
#### `weights.torchscript.source`<sub> Union</sub>
FileSource: The weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.torchscript.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.torchscript.attachments`<sub> generic.v0_2.AttachmentsDescr | </sub> ≝ `None`
Attachments that are specific to this weights entry.

<details><summary>generic.v0_2.AttachmentsDescr | None

</summary>


**generic.v0_2.AttachmentsDescr:**
##### `weights.torchscript.attachments.files`<sub> list</sub> ≝ `[]`
File attachments

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</details>

</details>

#### `weights.torchscript.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_2.Author] | None

</summary>


**generic.v0_2.Author:**
##### `weights.torchscript.authors.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



##### `weights.torchscript.authors.email`<sub> Email | None</sub> ≝ `None`
Email



##### `weights.torchscript.authors.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightstorchscriptauthorsorcid) '0000-0001-2345-6789'



##### `weights.torchscript.authors.name`<sub> str</sub>




##### `weights.torchscript.authors.github_user`<sub> str | None</sub> ≝ `None`




</details>

#### `weights.torchscript.dependencies`<sub> Dependencies | None</sub> ≝ `None`
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

#### `weights.torchscript.pytorch_version`<sub> _internal.version_type.Version |</sub> ≝ `None`
Version of the PyTorch library used.


_internal.version_type.Version | None

</details>

</details>

## `attachments`<sub> generic.v0_2.AttachmentsDescr | </sub> ≝ `None`
file and other attachments

<details><summary>generic.v0_2.AttachmentsDescr | None

</summary>


**generic.v0_2.AttachmentsDescr:**
### `attachments.files`<sub> list</sub> ≝ `[]`
File attachments

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</details>

</details>

## `cite`<sub> list</sub> ≝ `[]`
citations

<details><summary>list[bioimageio.spec.generic.v0_2.CiteEntry]

</summary>


**generic.v0_2.CiteEntry:**
### `cite.text`<sub> str</sub>
free text description



### `cite.doi`<sub> _internal.types.Doi | None</sub> ≝ `None`
A digital object identifier (DOI) is the prefered citation reference.
See https://www.doi.org/ for details. (alternatively specify `url`)



### `cite.url`<sub> str | None</sub> ≝ `None`
URL to cite (preferably specify a `doi` instead)



</details>

## `config`<sub> dict[str, YamlValue]</sub> ≝ `{}`
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



## `covers`<sub> list</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff')
[*Example:*](#covers) ['cover.png']

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False, allow_any_parent_suffix=False)]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False, allow_any_parent_suffix=False)]]

</details>

## `download_url`<sub> _internal.url.HttpUrl | None</sub> ≝ `None`
URL to download the resource from (deprecated)



## `git_repo`<sub> str | None</sub> ≝ `None`
A URL to the Git repository where the resource is being developed.
[*Example:*](#git_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



## `icon`<sub> Union</sub> ≝ `None`
An icon for illustration

<details><summary>Union[str*, Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
  (union_mode='left_to_right')
- None


</details>

## `id`<sub> ModelId | None</sub> ≝ `None`
bioimage.io-wide unique resource identifier
assigned by bioimage.io; version **un**specific.



## `id_emoji`<sub> Optional</sub> ≝ `None`
UTF-8 emoji for display alongside the `id`.


Optional[str (Len(min_length=1, max_length=1); )]

## `links`<sub> list[str]</sub> ≝ `[]`
IDs of other bioimage.io resources
[*Example:*](#links) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



## `maintainers`<sub> list</sub> ≝ `[]`
Maintainers of this resource.
If not specified `authors` are maintainers and at least some of them should specify their `github_user` name

<details><summary>list[bioimageio.spec.generic.v0_2.Maintainer]

</summary>


**generic.v0_2.Maintainer:**
### `maintainers.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



### `maintainers.email`<sub> Email | None</sub> ≝ `None`
Email



### `maintainers.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#maintainersorcid) '0000-0001-2345-6789'



### `maintainers.name`<sub> Optional</sub> ≝ `None`



Optional[str (AfterValidator(_remove_slashes))]

### `maintainers.github_user`<sub> str</sub>




</details>

## `packaged_by`<sub> list</sub> ≝ `[]`
The persons that have packaged and uploaded this model.
Only required if those persons differ from the `authors`.

<details><summary>list[bioimageio.spec.generic.v0_2.Author]

</summary>


**generic.v0_2.Author:**
### `packaged_by.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



### `packaged_by.email`<sub> Email | None</sub> ≝ `None`
Email



### `packaged_by.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#packaged_byorcid) '0000-0001-2345-6789'



### `packaged_by.name`<sub> str</sub>




### `packaged_by.github_user`<sub> str | None</sub> ≝ `None`




</details>

## `parent`<sub> LinkedModel | None</sub> ≝ `None`
The model from which this model is derived, e.g. by fine-tuning the weights.

<details><summary>LinkedModel | None

</summary>


**LinkedModel:**
### `parent.id`<sub> ModelId</sub>
A valid model `id` from the bioimage.io collection.
[*Examples:*](#parentid) ['affable-shark', 'ambitious-sloth']



### `parent.version_number`<sub> int | None</sub> ≝ `None`
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

## `run_mode`<sub> RunMode | None</sub> ≝ `None`
Custom run mode for this model: for more complex prediction procedures like test time
data augmentation that currently cannot be expressed in the specification.
No standard run modes are defined yet.

<details><summary>RunMode | None

</summary>


**RunMode:**
### `run_mode.name`<sub> Union[Literal[deepimagej], str]</sub>
Run mode name



### `run_mode.kwargs`<sub> dict[str, typing.Any]</sub> ≝ `{}`
Run mode specific key word arguments



</details>

## `sample_inputs`<sub> list</sub> ≝ `[]`
URLs/relative paths to sample inputs to illustrate possible inputs for the model,
for example stored as PNG or TIFF images.
The sample files primarily serve to inform a human user about an example use case

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</details>

## `sample_outputs`<sub> list</sub> ≝ `[]`
URLs/relative paths to sample outputs corresponding to the `sample_inputs`.

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</details>

## `tags`<sub> list[str]</sub> ≝ `[]`
Associated tags
[*Example:*](#tags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



## `training_data`<sub> dataset.v0_2.LinkedDataset | bio</sub> ≝ `None`
The dataset used to train this model

<details><summary>dataset.v0_2.LinkedDataset | bioimageio.spec.dataset.v0_2.DatasetDescr | None

</summary>


**dataset.v0_2.LinkedDataset:**
### `training_data.id`<sub> dataset.v0_2.DatasetId</sub>
A valid dataset `id` from the bioimage.io collection.



### `training_data.version_number`<sub> int | None</sub> ≝ `None`
version number (n-th published version, not the semantic version) of linked dataset



**dataset.v0_2.DatasetDescr:**
### `training_data.name`<sub> str</sub>
A human-friendly name of the resource description



### `training_data.description`<sub> str</sub>




### `training_data.covers`<sub> list</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff')
[*Example:*](#training_datacovers) ['cover.png']

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False, allow_any_parent_suffix=False)]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False, allow_any_parent_suffix=False)]]

</details>

### `training_data.id_emoji`<sub> Optional</sub> ≝ `None`
UTF-8 emoji for display alongside the `id`.


Optional[str (Len(min_length=1, max_length=1); )]

### `training_data.authors`<sub> list</sub> ≝ `[]`
The authors are the creators of the RDF and the primary points of contact.

<details><summary>list[bioimageio.spec.generic.v0_2.Author]

</summary>


**generic.v0_2.Author:**
#### `training_data.authors.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



#### `training_data.authors.email`<sub> Email | None</sub> ≝ `None`
Email



#### `training_data.authors.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#training_dataauthorsorcid) '0000-0001-2345-6789'



#### `training_data.authors.name`<sub> str</sub>




#### `training_data.authors.github_user`<sub> str | None</sub> ≝ `None`




</details>

### `training_data.attachments`<sub> generic.v0_2.AttachmentsDescr | </sub> ≝ `None`
file and other attachments

<details><summary>generic.v0_2.AttachmentsDescr | None

</summary>


**generic.v0_2.AttachmentsDescr:**
#### `training_data.attachments.files`<sub> list</sub> ≝ `[]`
File attachments

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7f3bdfd88c20>), PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none')]]

</details>

</details>

### `training_data.cite`<sub> list</sub> ≝ `[]`
citations

<details><summary>list[bioimageio.spec.generic.v0_2.CiteEntry]

</summary>


**generic.v0_2.CiteEntry:**
#### `training_data.cite.text`<sub> str</sub>
free text description



#### `training_data.cite.doi`<sub> _internal.types.Doi | None</sub> ≝ `None`
A digital object identifier (DOI) is the prefered citation reference.
See https://www.doi.org/ for details. (alternatively specify `url`)



#### `training_data.cite.url`<sub> str | None</sub> ≝ `None`
URL to cite (preferably specify a `doi` instead)



</details>

### `training_data.config`<sub> dict[str, YamlValue]</sub> ≝ `{}`
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



### `training_data.download_url`<sub> _internal.url.HttpUrl | None</sub> ≝ `None`
URL to download the resource from (deprecated)



### `training_data.git_repo`<sub> str | None</sub> ≝ `None`
A URL to the Git repository where the resource is being developed.
[*Example:*](#training_datagit_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



### `training_data.icon`<sub> Union</sub> ≝ `None`
An icon for illustration

<details><summary>Union[str*, Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
  (union_mode='left_to_right')
- None


</details>

### `training_data.links`<sub> list[str]</sub> ≝ `[]`
IDs of other bioimage.io resources
[*Example:*](#training_datalinks) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



### `training_data.uploader`<sub> generic.v0_2.Uploader | None</sub> ≝ `None`
The person who uploaded the model (e.g. to bioimage.io)

<details><summary>generic.v0_2.Uploader | None

</summary>


**generic.v0_2.Uploader:**
#### `training_data.uploader.email`<sub> Email</sub>
Email



#### `training_data.uploader.name`<sub> Optional</sub> ≝ `None`
name


Optional[str (AfterValidator(_remove_slashes))]

</details>

### `training_data.maintainers`<sub> list</sub> ≝ `[]`
Maintainers of this resource.
If not specified `authors` are maintainers and at least some of them should specify their `github_user` name

<details><summary>list[bioimageio.spec.generic.v0_2.Maintainer]

</summary>


**generic.v0_2.Maintainer:**
#### `training_data.maintainers.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



#### `training_data.maintainers.email`<sub> Email | None</sub> ≝ `None`
Email



#### `training_data.maintainers.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#training_datamaintainersorcid) '0000-0001-2345-6789'



#### `training_data.maintainers.name`<sub> Optional</sub> ≝ `None`



Optional[str (AfterValidator(_remove_slashes))]

#### `training_data.maintainers.github_user`<sub> str</sub>




</details>

### `training_data.rdf_source`<sub> Optional</sub> ≝ `None`
Resource description file (RDF) source; used to keep track of where an rdf.yaml was loaded from.
Do not set this field in a YAML file.

<details><summary>Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right')]

</details>

### `training_data.tags`<sub> list[str]</sub> ≝ `[]`
Associated tags
[*Example:*](#training_datatags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



### `training_data.version`<sub> _internal.version_type.Version |</sub> ≝ `None`
The version of the resource following SemVer 2.0.


_internal.version_type.Version | None

### `training_data.version_number`<sub> int | None</sub> ≝ `None`
version number (n-th published version, not the semantic version)



### `training_data.format_version`<sub> Literal[0.2.4]</sub>
The format version of this resource specification
(not the `version` of the resource description)
When creating a new resource always use the latest micro/patch version described here.
The `format_version` is important for any consumer software to understand how to parse the fields.



### `training_data.badges`<sub> list</sub> ≝ `[]`
badges associated with this resource

<details><summary>list[bioimageio.spec.generic.v0_2.BadgeDescr]

</summary>


**generic.v0_2.BadgeDescr:**
#### `training_data.badges.label`<sub> str</sub>
badge label to display on hover
[*Example:*](#training_databadgeslabel) 'Open in Colab'



#### `training_data.badges.icon`<sub> Union</sub> ≝ `None`
badge icon (included in bioimage.io package if not a URL)
[*Example:*](#training_databadgesicon) 'https://colab.research.google.com/assets/colab-badge.svg'

<details><summary>Union[Union[Path*, _internal.io.RelativeFilePath]*, _internal.url.HttpUrl, pydantic.networks.HttpUrl, None]

</summary>

Union of
- Union[Path (PathType(path_type='file'); ), _internal.io.RelativeFilePath]
  (AfterValidator(wo_special_file_name); PrettyPlainSerializer(func=<function _package_serializer at 0x7f3be09bf6a0>, return_type=PydanticUndefined, when_used='unless-none'))
- _internal.url.HttpUrl
- pydantic.networks.HttpUrl
- None


</details>

#### `training_data.badges.url`<sub> _internal.url.HttpUrl</sub>
target URL
[*Example:*](#training_databadgesurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



</details>

### `training_data.documentation`<sub> Optional</sub> ≝ `None`
URL or relative path to a markdown file with additional documentation.
The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
[*Examples:*](#training_datadocumentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']

<details><summary>Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right')]

</details>

### `training_data.license`<sub> _internal.license_id.LicenseId |</sub> ≝ `None`
A [SPDX license identifier](https://spdx.org/licenses/).
We do not support custom license beyond the SPDX license list, if you need that please
[open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose
) to discuss your intentions with the community.
[*Examples:*](#training_datalicense) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


_internal.license_id.LicenseId | bioimageio.spec._internal.license_id.DeprecatedLicenseId | str | None

### `training_data.type`<sub> Literal[dataset]</sub>




### `training_data.id`<sub> dataset.v0_2.DatasetId | None</sub> ≝ `None`
bioimage.io-wide unique resource identifier
assigned by bioimage.io; version **un**specific.



### `training_data.source`<sub> _internal.url.HttpUrl | None</sub> ≝ `None`
"URL to the source of the dataset.



</details>

## `uploader`<sub> generic.v0_2.Uploader | None</sub> ≝ `None`
The person who uploaded the model (e.g. to bioimage.io)

<details><summary>generic.v0_2.Uploader | None

</summary>


**generic.v0_2.Uploader:**
### `uploader.email`<sub> Email</sub>
Email



### `uploader.name`<sub> Optional</sub> ≝ `None`
name


Optional[str (AfterValidator(_remove_slashes))]

</details>

## `version`<sub> _internal.version_type.Version |</sub> ≝ `None`
The version of the resource following SemVer 2.0.


_internal.version_type.Version | None

## `version_number`<sub> int | None</sub> ≝ `None`
version number (n-th published version, not the semantic version)



# Example values
### `authors.orcid`
0000-0001-2345-6789
### `documentation`
- https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md
- README.md

### `inputs.shape`
- (1, 512, 512, 1)
- {'min': (1, 64, 64, 1), 'step': (0, 32, 32, 0)}

### `inputs.preprocessing.kwargs.axes`
xy
### `inputs.preprocessing.kwargs.axes`
xy
### `inputs.preprocessing.kwargs.mean`
(1.1, 2.2, 3.3)
### `inputs.preprocessing.kwargs.std`
(0.1, 0.2, 0.3)
### `inputs.preprocessing.kwargs.axes`
xy
### `license`
- CC0-1.0
- MIT
- BSD-2-Clause

### `outputs.postprocessing.kwargs.axes`
xy
### `outputs.postprocessing.kwargs.axes`
xy
### `outputs.postprocessing.kwargs.mean`
(1.1, 2.2, 3.3)
### `outputs.postprocessing.kwargs.std`
(0.1, 0.2, 0.3)
### `outputs.postprocessing.kwargs.axes`
xy
### `outputs.postprocessing.kwargs.axes`
xy
### `weights.keras_hdf5.authors.orcid`
0000-0001-2345-6789
### `weights.keras_hdf5.dependencies`
- conda:environment.yaml
- maven:./pom.xml
- pip:./requirements.txt

### `weights.keras_hdf5.parent`
pytorch_state_dict
### `weights.onnx.authors.orcid`
0000-0001-2345-6789
### `weights.onnx.dependencies`
- conda:environment.yaml
- maven:./pom.xml
- pip:./requirements.txt

### `weights.onnx.parent`
pytorch_state_dict
### `weights.pytorch_state_dict.authors.orcid`
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

### `weights.tensorflow_js.authors.orcid`
0000-0001-2345-6789
### `weights.tensorflow_js.dependencies`
- conda:environment.yaml
- maven:./pom.xml
- pip:./requirements.txt

### `weights.tensorflow_js.parent`
pytorch_state_dict
### `weights.tensorflow_saved_model_bundle.authors.orcid`
0000-0001-2345-6789
### `weights.tensorflow_saved_model_bundle.dependencies`
- conda:environment.yaml
- maven:./pom.xml
- pip:./requirements.txt

### `weights.tensorflow_saved_model_bundle.parent`
pytorch_state_dict
### `weights.torchscript.authors.orcid`
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
['cover.png']
### `git_repo`
https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad
### `links`
('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')
### `maintainers.orcid`
0000-0001-2345-6789
### `packaged_by.orcid`
0000-0001-2345-6789
### `parent.id`
- affable-shark
- ambitious-sloth

### `tags`
('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')
### `training_data.covers`
['cover.png']
### `training_data.authors.orcid`
0000-0001-2345-6789
### `training_data.config`
{'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}
### `training_data.git_repo`
https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad
### `training_data.links`
('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')
### `training_data.maintainers.orcid`
0000-0001-2345-6789
### `training_data.tags`
('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')
### `training_data.badges.label`
Open in Colab
### `training_data.badges.icon`
https://colab.research.google.com/assets/colab-badge.svg
### `training_data.badges.url`
https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb
### `training_data.documentation`
- https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md
- README.md

### `training_data.license`
- CC0-1.0
- MIT
- BSD-2-Clause

