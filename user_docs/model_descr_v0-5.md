# bioimage.io model specification
Specification of the fields used in a bioimage.io-compliant RDF to describe AI models with pretrained weights.
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




## `format_version`<sub> Literal[0.5.3]</sub> ≝ `0.5.3`




## `authors`<sub> Sequence[generic.v0_3.Author]</sub>


<details><summary>Sequence[generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
### `authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




### `authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




### `authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#authorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `authors.i.name`<sub> str</sub>




### `authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

## `cite`<sub> Sequence[generic.v0_3.CiteEntry]</sub>


<details><summary>Sequence[generic.v0_3.CiteEntry]

</summary>


**generic.v0_3.CiteEntry:**
### `cite.i.text`<sub> str</sub>




### `cite.i.doi`<sub> Optional[_internal.types.Doi]</sub> ≝ `None`




### `cite.i.url`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`




</details>

## `description`<sub> str</sub>




## `documentation`<sub> Union</sub>

[*Examples:*](#documentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']


Union[Path (PathType(path_type='file'); Predicate(is_absolute)), _internal.io.RelativeFilePath, _internal.url.HttpUrl]

## `inputs`<sub> Sequence</sub>


<details><summary>Sequence[bioimageio.spec.model.v0_5.InputTensorDescr]

</summary>


**InputTensorDescr:**
### `inputs.id`<sub> TensorId</sub> ≝ `input`




### `inputs.description`<sub> str</sub> ≝ ``




### `inputs.axes`<sub> Sequence</sub>


<details><summary>Sequence[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BatchAxis, bioimageio.spec.model.v0_5.ChannelAxis, bioimageio.spec.model.v0_5.IndexInputAxis, bioimageio.spec.model.v0_5.TimeInputAxis, bioimageio.spec.model.v0_5.SpaceInputAxis], Discriminator(discriminator='type', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

</summary>

Sequence[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BatchAxis, bioimageio.spec.model.v0_5.ChannelAxis, bioimageio.spec.model.v0_5.IndexInputAxis, bioimageio.spec.model.v0_5.TimeInputAxis, bioimageio.spec.model.v0_5.SpaceInputAxis], Discriminator(discriminator='type', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

**BatchAxis:**
#### `inputs.axes.id`<sub> AxisId</sub> ≝ `batch`




#### `inputs.axes.description`<sub> str</sub> ≝ ``




#### `inputs.axes.type`<sub> Literal[batch]</sub> ≝ `batch`




#### `inputs.axes.size`<sub> Optional[Literal[1]]</sub> ≝ `None`




**ChannelAxis:**
#### `inputs.axes.id`<sub> AxisId</sub> ≝ `channel`




#### `inputs.axes.description`<sub> str</sub> ≝ ``




#### `inputs.axes.type`<sub> Literal[channel]</sub> ≝ `channel`




#### `inputs.axes.channel_names`<sub> Sequence</sub>



Sequence[_internal.types.Identifier]

**IndexInputAxis:**
#### `inputs.axes.size`<sub> Union</sub>

[*Examples:*](#inputsaxessize) [10, {'min': 32, 'step': 16}, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), ParameterizedSize, SizeReference]

</summary>


**ParameterizedSize:**
##### `inputs.axes.size.min`<sub> int</sub>




##### `inputs.axes.size.step`<sub> int</sub>




**SizeReference:**
##### `inputs.axes.size.tensor_id`<sub> TensorId</sub>




##### `inputs.axes.size.axis_id`<sub> AxisId</sub>




##### `inputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `inputs.axes.id`<sub> AxisId</sub> ≝ `index`




#### `inputs.axes.description`<sub> str</sub> ≝ ``




#### `inputs.axes.type`<sub> Literal[index]</sub> ≝ `index`




#### `inputs.axes.concatenable`<sub> bool</sub> ≝ `False`




**TimeInputAxis:**
#### `inputs.axes.size`<sub> Union</sub>

[*Examples:*](#inputsaxessize) [10, {'min': 32, 'step': 16}, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), ParameterizedSize, SizeReference]

</summary>


**ParameterizedSize:**
##### `inputs.axes.size.min`<sub> int</sub>




##### `inputs.axes.size.step`<sub> int</sub>




**SizeReference:**
##### `inputs.axes.size.tensor_id`<sub> TensorId</sub>




##### `inputs.axes.size.axis_id`<sub> AxisId</sub>




##### `inputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `inputs.axes.id`<sub> AxisId</sub> ≝ `time`




#### `inputs.axes.description`<sub> str</sub> ≝ ``




#### `inputs.axes.type`<sub> Literal[time]</sub> ≝ `time`




#### `inputs.axes.unit`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Literal[attosecond, ..., zettasecond]]

</summary>

Optional[Literal of
- attosecond
- centisecond
- day
- decisecond
- exasecond
- femtosecond
- gigasecond
- hectosecond
- hour
- kilosecond
- megasecond
- microsecond
- millisecond
- minute
- nanosecond
- petasecond
- picosecond
- second
- terasecond
- yoctosecond
- yottasecond
- zeptosecond
- zettasecond
]

</details>

#### `inputs.axes.scale`<sub> float</sub> ≝ `1.0`




#### `inputs.axes.concatenable`<sub> bool</sub> ≝ `False`




**SpaceInputAxis:**
#### `inputs.axes.size`<sub> Union</sub>

[*Examples:*](#inputsaxessize) [10, {'min': 32, 'step': 16}, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), ParameterizedSize, SizeReference]

</summary>


**ParameterizedSize:**
##### `inputs.axes.size.min`<sub> int</sub>




##### `inputs.axes.size.step`<sub> int</sub>




**SizeReference:**
##### `inputs.axes.size.tensor_id`<sub> TensorId</sub>




##### `inputs.axes.size.axis_id`<sub> AxisId</sub>




##### `inputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `inputs.axes.id`<sub> AxisId</sub> ≝ `x`

[*Examples:*](#inputsaxesid) ['x', 'y', 'z']



#### `inputs.axes.description`<sub> str</sub> ≝ ``




#### `inputs.axes.type`<sub> Literal[space]</sub> ≝ `space`




#### `inputs.axes.unit`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Literal[attometer, ..., zettameter]]

</summary>

Optional[Literal of
- attometer
- angstrom
- centimeter
- decimeter
- exameter
- femtometer
- foot
- gigameter
- hectometer
- inch
- kilometer
- megameter
- meter
- micrometer
- mile
- millimeter
- nanometer
- parsec
- petameter
- picometer
- terameter
- yard
- yoctometer
- yottameter
- zeptometer
- zettameter
]

</details>

#### `inputs.axes.scale`<sub> float</sub> ≝ `1.0`




#### `inputs.axes.concatenable`<sub> bool</sub> ≝ `False`




</details>

### `inputs.test_tensor`<sub> _internal.io.FileDescr</sub>


<details><summary>_internal.io.FileDescr

</summary>


**_internal.io.FileDescr:**
#### `inputs.test_tensor.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

#### `inputs.test_tensor.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

</details>

### `inputs.sample_tensor`<sub> Optional[_internal.io.FileDescr]</sub> ≝ `None`


<details><summary>Optional[_internal.io.FileDescr]

</summary>


**_internal.io.FileDescr:**
#### `inputs.sample_tensor.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

#### `inputs.sample_tensor.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

</details>

### `inputs.data`<sub> Union</sub> ≝ `type='float32' range=(None, None) unit='arbitrary unit' scale=1.0 offset=None`


<details><summary>Union[NominalOrOrdinalDataDescr, IntervalOrRatioDataDescr, Sequence[typing.Union[bioimageio.spec.model.v0_5.NominalOrOrdinalDataDescr, bioimageio.spec.model.v0_5.IntervalOrRatioDataDescr]]*]

</summary>

Union of
- NominalOrOrdinalDataDescr
- IntervalOrRatioDataDescr
- Sequence[typing.Union[bioimageio.spec.model.v0_5.NominalOrOrdinalDataDescr, bioimageio.spec.model.v0_5.IntervalOrRatioDataDescr]]
  (MinLen(min_length=1))


**NominalOrOrdinalDataDescr:**
#### `inputs.data.values`<sub> Union</sub>


<details><summary>Union[Sequence[int]*, Sequence[float]*, Sequence[bool]*, Sequence[str]*]

</summary>

Union of
- Sequence[int] (MinLen(min_length=1))
- Sequence[float] (MinLen(min_length=1))
- Sequence[bool] (MinLen(min_length=1))
- Sequence[str] (MinLen(min_length=1))


</details>

#### `inputs.data.type`<sub> Literal</sub> ≝ `uint8`

[*Examples:*](#inputsdatatype) ['float32', 'uint8', 'uint16', 'int64', 'bool']


Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

#### `inputs.data.unit`<sub> Union</sub> ≝ `None`



Union[Literal[arbitrary unit], _internal.types.SiUnit, None]

**IntervalOrRatioDataDescr:**
#### `inputs.data.type`<sub> Literal</sub> ≝ `float32`

[*Examples:*](#inputsdatatype) ['float32', 'float64', 'uint8', 'uint16']


Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64]

#### `inputs.data.range`<sub> Sequence</sub> ≝ `(None, None)`



Sequence[Optional[float], Optional[float]]

#### `inputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `inputs.data.scale`<sub> float</sub> ≝ `1.0`




#### `inputs.data.offset`<sub> Optional[float]</sub> ≝ `None`




**NominalOrOrdinalDataDescr:**
#### `inputs.data.values`<sub> Union</sub>


<details><summary>Union[Sequence[int]*, Sequence[float]*, Sequence[bool]*, Sequence[str]*]

</summary>

Union of
- Sequence[int] (MinLen(min_length=1))
- Sequence[float] (MinLen(min_length=1))
- Sequence[bool] (MinLen(min_length=1))
- Sequence[str] (MinLen(min_length=1))


</details>

#### `inputs.data.type`<sub> Literal</sub> ≝ `uint8`

[*Examples:*](#inputsdatatype) ['float32', 'uint8', 'uint16', 'int64', 'bool']


Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

#### `inputs.data.unit`<sub> Union</sub> ≝ `None`



Union[Literal[arbitrary unit], _internal.types.SiUnit, None]

**IntervalOrRatioDataDescr:**
#### `inputs.data.type`<sub> Literal</sub> ≝ `float32`

[*Examples:*](#inputsdatatype) ['float32', 'float64', 'uint8', 'uint16']


Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64]

#### `inputs.data.range`<sub> Sequence</sub> ≝ `(None, None)`



Sequence[Optional[float], Optional[float]]

#### `inputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `inputs.data.scale`<sub> float</sub> ≝ `1.0`




#### `inputs.data.offset`<sub> Optional[float]</sub> ≝ `None`




</details>

### `inputs.optional`<sub> bool</sub> ≝ `False`




### `inputs.preprocessing`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[BinarizeDescr, ..., ScaleRangeDescr]*]

</summary>

Sequence of Union of
- BinarizeDescr
- ClipDescr
- EnsureDtypeDescr
- ScaleLinearDescr
- SigmoidDescr
- FixedZeroMeanUnitVarianceDescr
- ZeroMeanUnitVarianceDescr
- ScaleRangeDescr

(Discriminator(discriminator='id', custom_error_type=None, custom_error_message=None, custom_error_context=None))

**BinarizeDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[binarize]</sub> ≝ `binarize`




#### `inputs.preprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[BinarizeKwargs, BinarizeAlongAxisKwargs]

</summary>


**BinarizeKwargs:**
##### `inputs.preprocessing.i.kwargs.threshold`<sub> float</sub>




**BinarizeAlongAxisKwargs:**
##### `inputs.preprocessing.i.kwargs.threshold`<sub> Sequence[float]</sub>




##### `inputs.preprocessing.i.kwargs.axis`<sub> AxisId</sub>

[*Example:*](#inputspreprocessingikwargsaxis) 'channel'



</details>

**ClipDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[clip]</sub> ≝ `clip`




#### `inputs.preprocessing.i.kwargs`<sub> model.v0_4.ClipKwargs</sub>


<details><summary>model.v0_4.ClipKwargs

</summary>


**model.v0_4.ClipKwargs:**
##### `inputs.preprocessing.i.kwargs.min`<sub> float</sub>




##### `inputs.preprocessing.i.kwargs.max`<sub> float</sub>




</details>

**EnsureDtypeDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[ensure_dtype]</sub> ≝ `ensure_dtype`




#### `inputs.preprocessing.i.kwargs`<sub> EnsureDtypeKwargs</sub>


<details><summary>EnsureDtypeKwargs

</summary>


**EnsureDtypeKwargs:**
##### `inputs.preprocessing.i.kwargs.dtype`<sub> Literal</sub>



Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

</details>

**ScaleLinearDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[scale_linear]</sub> ≝ `scale_linear`




#### `inputs.preprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[ScaleLinearKwargs, ScaleLinearAlongAxisKwargs]

</summary>


**ScaleLinearKwargs:**
##### `inputs.preprocessing.i.kwargs.gain`<sub> float</sub> ≝ `1.0`




##### `inputs.preprocessing.i.kwargs.offset`<sub> float</sub> ≝ `0.0`




**ScaleLinearAlongAxisKwargs:**
##### `inputs.preprocessing.i.kwargs.axis`<sub> AxisId</sub>

[*Example:*](#inputspreprocessingikwargsaxis) 'channel'



##### `inputs.preprocessing.i.kwargs.gain`<sub> Union</sub> ≝ `1.0`



Union[float, Sequence[float] (MinLen(min_length=1))]

##### `inputs.preprocessing.i.kwargs.offset`<sub> Union</sub> ≝ `0.0`



Union[float, Sequence[float] (MinLen(min_length=1))]

</details>

**SigmoidDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[sigmoid]</sub> ≝ `sigmoid`




**FixedZeroMeanUnitVarianceDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal</sub> ≝ `fixed_zero_mean_unit_variance`



Literal[fixed_zero_mean_unit_variance]

#### `inputs.preprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[FixedZeroMeanUnitVarianceKwargs, FixedZeroMeanUnitVarianceAlongAxisKwargs]

</summary>


**FixedZeroMeanUnitVarianceKwargs:**
##### `inputs.preprocessing.i.kwargs.mean`<sub> float</sub>




##### `inputs.preprocessing.i.kwargs.std`<sub> float</sub>




**FixedZeroMeanUnitVarianceAlongAxisKwargs:**
##### `inputs.preprocessing.i.kwargs.mean`<sub> Sequence[float]</sub>




##### `inputs.preprocessing.i.kwargs.std`<sub> Sequence[float (Ge(ge=1e-06))]</sub>




##### `inputs.preprocessing.i.kwargs.axis`<sub> AxisId</sub>

[*Examples:*](#inputspreprocessingikwargsaxis) ['channel', 'index']



</details>

**ZeroMeanUnitVarianceDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[zero_mean_unit_variance]</sub> ≝ `zero_mean_unit_variance`




#### `inputs.preprocessing.i.kwargs`<sub> ZeroMeanUnitVarianceKwargs</sub>


<details><summary>ZeroMeanUnitVarianceKwargs

</summary>


**ZeroMeanUnitVarianceKwargs:**
##### `inputs.preprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`

[*Example:*](#inputspreprocessingikwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `inputs.preprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`




</details>

**ScaleRangeDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[scale_range]</sub> ≝ `scale_range`




#### `inputs.preprocessing.i.kwargs`<sub> ScaleRangeKwargs</sub>


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `inputs.preprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`

[*Example:*](#inputspreprocessingikwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `inputs.preprocessing.i.kwargs.min_percentile`<sub> float</sub> ≝ `0.0`




##### `inputs.preprocessing.i.kwargs.max_percentile`<sub> float</sub> ≝ `100.0`




##### `inputs.preprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`




##### `inputs.preprocessing.i.kwargs.reference_tensor`<sub> Optional[TensorId]</sub> ≝ `None`




</details>

</details>

</details>

## `license`<sub> Union</sub>

[*Examples:*](#license) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId]

## `name`<sub> str</sub>




## `outputs`<sub> Sequence</sub>


<details><summary>Sequence[bioimageio.spec.model.v0_5.OutputTensorDescr]

</summary>


**OutputTensorDescr:**
### `outputs.id`<sub> TensorId</sub> ≝ `output`




### `outputs.description`<sub> str</sub> ≝ ``




### `outputs.axes`<sub> Sequence</sub>


<details><summary>Sequence[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BatchAxis, bioimageio.spec.model.v0_5.ChannelAxis, bioimageio.spec.model.v0_5.IndexOutputAxis, typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7f1d7acf7ec0>, custom_error_type=None, custom_error_message=None, custom_error_context=None)], typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7f1d7acf7ec0>, custom_error_type=None, custom_error_message=None, custom_error_context=None)]], Discriminator(discriminator='type', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

</summary>

Sequence[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BatchAxis, bioimageio.spec.model.v0_5.ChannelAxis, bioimageio.spec.model.v0_5.IndexOutputAxis, typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7f1d7acf7ec0>, custom_error_type=None, custom_error_message=None, custom_error_context=None)], typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7f1d7acf7ec0>, custom_error_type=None, custom_error_message=None, custom_error_context=None)]], Discriminator(discriminator='type', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

**BatchAxis:**
#### `outputs.axes.id`<sub> AxisId</sub> ≝ `batch`




#### `outputs.axes.description`<sub> str</sub> ≝ ``




#### `outputs.axes.type`<sub> Literal[batch]</sub> ≝ `batch`




#### `outputs.axes.size`<sub> Optional[Literal[1]]</sub> ≝ `None`




**ChannelAxis:**
#### `outputs.axes.id`<sub> AxisId</sub> ≝ `channel`




#### `outputs.axes.description`<sub> str</sub> ≝ ``




#### `outputs.axes.type`<sub> Literal[channel]</sub> ≝ `channel`




#### `outputs.axes.channel_names`<sub> Sequence</sub>



Sequence[_internal.types.Identifier]

**IndexOutputAxis:**
#### `outputs.axes.id`<sub> AxisId</sub> ≝ `index`




#### `outputs.axes.description`<sub> str</sub> ≝ ``




#### `outputs.axes.type`<sub> Literal[index]</sub> ≝ `index`




#### `outputs.axes.size`<sub> Union</sub>

[*Examples:*](#outputsaxessize) [10, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), SizeReference, DataDependentSize]

</summary>


**SizeReference:**
##### `outputs.axes.size.tensor_id`<sub> TensorId</sub>




##### `outputs.axes.size.axis_id`<sub> AxisId</sub>




##### `outputs.axes.size.offset`<sub> int</sub> ≝ `0`




**DataDependentSize:**
##### `outputs.axes.size.min`<sub> int</sub> ≝ `1`




##### `outputs.axes.size.max`<sub> Optional[int]</sub> ≝ `None`




</details>

**TimeOutputAxis:**
#### `outputs.axes.size`<sub> Union</sub>

[*Examples:*](#outputsaxessize) [10, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), SizeReference]

</summary>


**SizeReference:**
##### `outputs.axes.size.tensor_id`<sub> TensorId</sub>




##### `outputs.axes.size.axis_id`<sub> AxisId</sub>




##### `outputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `outputs.axes.id`<sub> AxisId</sub> ≝ `time`




#### `outputs.axes.description`<sub> str</sub> ≝ ``




#### `outputs.axes.type`<sub> Literal[time]</sub> ≝ `time`




#### `outputs.axes.unit`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Literal[attosecond, ..., zettasecond]]

</summary>

Optional[Literal of
- attosecond
- centisecond
- day
- decisecond
- exasecond
- femtosecond
- gigasecond
- hectosecond
- hour
- kilosecond
- megasecond
- microsecond
- millisecond
- minute
- nanosecond
- petasecond
- picosecond
- second
- terasecond
- yoctosecond
- yottasecond
- zeptosecond
- zettasecond
]

</details>

#### `outputs.axes.scale`<sub> float</sub> ≝ `1.0`




**TimeOutputAxisWithHalo:**
#### `outputs.axes.halo`<sub> int</sub>




#### `outputs.axes.size`<sub> SizeReference</sub>

[*Examples:*](#outputsaxessize) [10, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>SizeReference

</summary>


**SizeReference:**
##### `outputs.axes.size.tensor_id`<sub> TensorId</sub>




##### `outputs.axes.size.axis_id`<sub> AxisId</sub>




##### `outputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `outputs.axes.id`<sub> AxisId</sub> ≝ `time`




#### `outputs.axes.description`<sub> str</sub> ≝ ``




#### `outputs.axes.type`<sub> Literal[time]</sub> ≝ `time`




#### `outputs.axes.unit`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Literal[attosecond, ..., zettasecond]]

</summary>

Optional[Literal of
- attosecond
- centisecond
- day
- decisecond
- exasecond
- femtosecond
- gigasecond
- hectosecond
- hour
- kilosecond
- megasecond
- microsecond
- millisecond
- minute
- nanosecond
- petasecond
- picosecond
- second
- terasecond
- yoctosecond
- yottasecond
- zeptosecond
- zettasecond
]

</details>

#### `outputs.axes.scale`<sub> float</sub> ≝ `1.0`




**SpaceOutputAxis:**
#### `outputs.axes.size`<sub> Union</sub>

[*Examples:*](#outputsaxessize) [10, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), SizeReference]

</summary>


**SizeReference:**
##### `outputs.axes.size.tensor_id`<sub> TensorId</sub>




##### `outputs.axes.size.axis_id`<sub> AxisId</sub>




##### `outputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `outputs.axes.id`<sub> AxisId</sub> ≝ `x`

[*Examples:*](#outputsaxesid) ['x', 'y', 'z']



#### `outputs.axes.description`<sub> str</sub> ≝ ``




#### `outputs.axes.type`<sub> Literal[space]</sub> ≝ `space`




#### `outputs.axes.unit`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Literal[attometer, ..., zettameter]]

</summary>

Optional[Literal of
- attometer
- angstrom
- centimeter
- decimeter
- exameter
- femtometer
- foot
- gigameter
- hectometer
- inch
- kilometer
- megameter
- meter
- micrometer
- mile
- millimeter
- nanometer
- parsec
- petameter
- picometer
- terameter
- yard
- yoctometer
- yottameter
- zeptometer
- zettameter
]

</details>

#### `outputs.axes.scale`<sub> float</sub> ≝ `1.0`




**SpaceOutputAxisWithHalo:**
#### `outputs.axes.halo`<sub> int</sub>




#### `outputs.axes.size`<sub> SizeReference</sub>

[*Examples:*](#outputsaxessize) [10, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>SizeReference

</summary>


**SizeReference:**
##### `outputs.axes.size.tensor_id`<sub> TensorId</sub>




##### `outputs.axes.size.axis_id`<sub> AxisId</sub>




##### `outputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `outputs.axes.id`<sub> AxisId</sub> ≝ `x`

[*Examples:*](#outputsaxesid) ['x', 'y', 'z']



#### `outputs.axes.description`<sub> str</sub> ≝ ``




#### `outputs.axes.type`<sub> Literal[space]</sub> ≝ `space`




#### `outputs.axes.unit`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Literal[attometer, ..., zettameter]]

</summary>

Optional[Literal of
- attometer
- angstrom
- centimeter
- decimeter
- exameter
- femtometer
- foot
- gigameter
- hectometer
- inch
- kilometer
- megameter
- meter
- micrometer
- mile
- millimeter
- nanometer
- parsec
- petameter
- picometer
- terameter
- yard
- yoctometer
- yottameter
- zeptometer
- zettameter
]

</details>

#### `outputs.axes.scale`<sub> float</sub> ≝ `1.0`




</details>

### `outputs.test_tensor`<sub> _internal.io.FileDescr</sub>


<details><summary>_internal.io.FileDescr

</summary>


**_internal.io.FileDescr:**
#### `outputs.test_tensor.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

#### `outputs.test_tensor.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

</details>

### `outputs.sample_tensor`<sub> Optional[_internal.io.FileDescr]</sub> ≝ `None`


<details><summary>Optional[_internal.io.FileDescr]

</summary>


**_internal.io.FileDescr:**
#### `outputs.sample_tensor.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

#### `outputs.sample_tensor.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

</details>

### `outputs.data`<sub> Union</sub> ≝ `type='float32' range=(None, None) unit='arbitrary unit' scale=1.0 offset=None`


<details><summary>Union[NominalOrOrdinalDataDescr, IntervalOrRatioDataDescr, Sequence[typing.Union[bioimageio.spec.model.v0_5.NominalOrOrdinalDataDescr, bioimageio.spec.model.v0_5.IntervalOrRatioDataDescr]]*]

</summary>

Union of
- NominalOrOrdinalDataDescr
- IntervalOrRatioDataDescr
- Sequence[typing.Union[bioimageio.spec.model.v0_5.NominalOrOrdinalDataDescr, bioimageio.spec.model.v0_5.IntervalOrRatioDataDescr]]
  (MinLen(min_length=1))


**NominalOrOrdinalDataDescr:**
#### `outputs.data.values`<sub> Union</sub>


<details><summary>Union[Sequence[int]*, Sequence[float]*, Sequence[bool]*, Sequence[str]*]

</summary>

Union of
- Sequence[int] (MinLen(min_length=1))
- Sequence[float] (MinLen(min_length=1))
- Sequence[bool] (MinLen(min_length=1))
- Sequence[str] (MinLen(min_length=1))


</details>

#### `outputs.data.type`<sub> Literal</sub> ≝ `uint8`

[*Examples:*](#outputsdatatype) ['float32', 'uint8', 'uint16', 'int64', 'bool']


Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

#### `outputs.data.unit`<sub> Union</sub> ≝ `None`



Union[Literal[arbitrary unit], _internal.types.SiUnit, None]

**IntervalOrRatioDataDescr:**
#### `outputs.data.type`<sub> Literal</sub> ≝ `float32`

[*Examples:*](#outputsdatatype) ['float32', 'float64', 'uint8', 'uint16']


Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64]

#### `outputs.data.range`<sub> Sequence</sub> ≝ `(None, None)`



Sequence[Optional[float], Optional[float]]

#### `outputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `outputs.data.scale`<sub> float</sub> ≝ `1.0`




#### `outputs.data.offset`<sub> Optional[float]</sub> ≝ `None`




**NominalOrOrdinalDataDescr:**
#### `outputs.data.values`<sub> Union</sub>


<details><summary>Union[Sequence[int]*, Sequence[float]*, Sequence[bool]*, Sequence[str]*]

</summary>

Union of
- Sequence[int] (MinLen(min_length=1))
- Sequence[float] (MinLen(min_length=1))
- Sequence[bool] (MinLen(min_length=1))
- Sequence[str] (MinLen(min_length=1))


</details>

#### `outputs.data.type`<sub> Literal</sub> ≝ `uint8`

[*Examples:*](#outputsdatatype) ['float32', 'uint8', 'uint16', 'int64', 'bool']


Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

#### `outputs.data.unit`<sub> Union</sub> ≝ `None`



Union[Literal[arbitrary unit], _internal.types.SiUnit, None]

**IntervalOrRatioDataDescr:**
#### `outputs.data.type`<sub> Literal</sub> ≝ `float32`

[*Examples:*](#outputsdatatype) ['float32', 'float64', 'uint8', 'uint16']


Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64]

#### `outputs.data.range`<sub> Sequence</sub> ≝ `(None, None)`



Sequence[Optional[float], Optional[float]]

#### `outputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `outputs.data.scale`<sub> float</sub> ≝ `1.0`




#### `outputs.data.offset`<sub> Optional[float]</sub> ≝ `None`




</details>

### `outputs.postprocessing`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[BinarizeDescr, ..., ScaleMeanVarianceDescr]*]

</summary>

Sequence of Union of
- BinarizeDescr
- ClipDescr
- EnsureDtypeDescr
- ScaleLinearDescr
- SigmoidDescr
- FixedZeroMeanUnitVarianceDescr
- ZeroMeanUnitVarianceDescr
- ScaleRangeDescr
- ScaleMeanVarianceDescr

(Discriminator(discriminator='id', custom_error_type=None, custom_error_message=None, custom_error_context=None))

**BinarizeDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[binarize]</sub> ≝ `binarize`




#### `outputs.postprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[BinarizeKwargs, BinarizeAlongAxisKwargs]

</summary>


**BinarizeKwargs:**
##### `outputs.postprocessing.i.kwargs.threshold`<sub> float</sub>




**BinarizeAlongAxisKwargs:**
##### `outputs.postprocessing.i.kwargs.threshold`<sub> Sequence[float]</sub>




##### `outputs.postprocessing.i.kwargs.axis`<sub> AxisId</sub>

[*Example:*](#outputspostprocessingikwargsaxis) 'channel'



</details>

**ClipDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[clip]</sub> ≝ `clip`




#### `outputs.postprocessing.i.kwargs`<sub> model.v0_4.ClipKwargs</sub>


<details><summary>model.v0_4.ClipKwargs

</summary>


**model.v0_4.ClipKwargs:**
##### `outputs.postprocessing.i.kwargs.min`<sub> float</sub>




##### `outputs.postprocessing.i.kwargs.max`<sub> float</sub>




</details>

**EnsureDtypeDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[ensure_dtype]</sub> ≝ `ensure_dtype`




#### `outputs.postprocessing.i.kwargs`<sub> EnsureDtypeKwargs</sub>


<details><summary>EnsureDtypeKwargs

</summary>


**EnsureDtypeKwargs:**
##### `outputs.postprocessing.i.kwargs.dtype`<sub> Literal</sub>



Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

</details>

**ScaleLinearDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[scale_linear]</sub> ≝ `scale_linear`




#### `outputs.postprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[ScaleLinearKwargs, ScaleLinearAlongAxisKwargs]

</summary>


**ScaleLinearKwargs:**
##### `outputs.postprocessing.i.kwargs.gain`<sub> float</sub> ≝ `1.0`




##### `outputs.postprocessing.i.kwargs.offset`<sub> float</sub> ≝ `0.0`




**ScaleLinearAlongAxisKwargs:**
##### `outputs.postprocessing.i.kwargs.axis`<sub> AxisId</sub>

[*Example:*](#outputspostprocessingikwargsaxis) 'channel'



##### `outputs.postprocessing.i.kwargs.gain`<sub> Union</sub> ≝ `1.0`



Union[float, Sequence[float] (MinLen(min_length=1))]

##### `outputs.postprocessing.i.kwargs.offset`<sub> Union</sub> ≝ `0.0`



Union[float, Sequence[float] (MinLen(min_length=1))]

</details>

**SigmoidDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[sigmoid]</sub> ≝ `sigmoid`




**FixedZeroMeanUnitVarianceDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal</sub> ≝ `fixed_zero_mean_unit_variance`



Literal[fixed_zero_mean_unit_variance]

#### `outputs.postprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[FixedZeroMeanUnitVarianceKwargs, FixedZeroMeanUnitVarianceAlongAxisKwargs]

</summary>


**FixedZeroMeanUnitVarianceKwargs:**
##### `outputs.postprocessing.i.kwargs.mean`<sub> float</sub>




##### `outputs.postprocessing.i.kwargs.std`<sub> float</sub>




**FixedZeroMeanUnitVarianceAlongAxisKwargs:**
##### `outputs.postprocessing.i.kwargs.mean`<sub> Sequence[float]</sub>




##### `outputs.postprocessing.i.kwargs.std`<sub> Sequence[float (Ge(ge=1e-06))]</sub>




##### `outputs.postprocessing.i.kwargs.axis`<sub> AxisId</sub>

[*Examples:*](#outputspostprocessingikwargsaxis) ['channel', 'index']



</details>

**ZeroMeanUnitVarianceDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[zero_mean_unit_variance]</sub> ≝ `zero_mean_unit_variance`




#### `outputs.postprocessing.i.kwargs`<sub> ZeroMeanUnitVarianceKwargs</sub>


<details><summary>ZeroMeanUnitVarianceKwargs

</summary>


**ZeroMeanUnitVarianceKwargs:**
##### `outputs.postprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`

[*Example:*](#outputspostprocessingikwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `outputs.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`




</details>

**ScaleRangeDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[scale_range]</sub> ≝ `scale_range`




#### `outputs.postprocessing.i.kwargs`<sub> ScaleRangeKwargs</sub>


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `outputs.postprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`

[*Example:*](#outputspostprocessingikwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `outputs.postprocessing.i.kwargs.min_percentile`<sub> float</sub> ≝ `0.0`




##### `outputs.postprocessing.i.kwargs.max_percentile`<sub> float</sub> ≝ `100.0`




##### `outputs.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`




##### `outputs.postprocessing.i.kwargs.reference_tensor`<sub> Optional[TensorId]</sub> ≝ `None`




</details>

**ScaleMeanVarianceDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[scale_mean_variance]</sub> ≝ `scale_mean_variance`




#### `outputs.postprocessing.i.kwargs`<sub> ScaleMeanVarianceKwargs</sub>


<details><summary>ScaleMeanVarianceKwargs

</summary>


**ScaleMeanVarianceKwargs:**
##### `outputs.postprocessing.i.kwargs.reference_tensor`<sub> TensorId</sub>




##### `outputs.postprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`

[*Example:*](#outputspostprocessingikwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `outputs.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`




</details>

</details>

</details>

## `weights`<sub> WeightsDescr</sub>


<details><summary>WeightsDescr

</summary>


**WeightsDescr:**
### `weights.keras_hdf5`<sub> Optional[KerasHdf5WeightsDescr]</sub> ≝ `None`


<details><summary>Optional[KerasHdf5WeightsDescr]

</summary>


**KerasHdf5WeightsDescr:**
#### `weights.keras_hdf5.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

#### `weights.keras_hdf5.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

#### `weights.keras_hdf5.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
##### `weights.keras_hdf5.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.keras_hdf5.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.keras_hdf5.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightskeras_hdf5authorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.keras_hdf5.authors.i.name`<sub> str</sub>




##### `weights.keras_hdf5.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.keras_hdf5.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightskeras_hdf5parent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.keras_hdf5.tensorflow_version`<sub> _internal.version_type.Version</sub>




</details>

### `weights.onnx`<sub> Optional[OnnxWeightsDescr]</sub> ≝ `None`


<details><summary>Optional[OnnxWeightsDescr]

</summary>


**OnnxWeightsDescr:**
#### `weights.onnx.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

#### `weights.onnx.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

#### `weights.onnx.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
##### `weights.onnx.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.onnx.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.onnx.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightsonnxauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.onnx.authors.i.name`<sub> str</sub>




##### `weights.onnx.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.onnx.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightsonnxparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.onnx.opset_version`<sub> int</sub>




</details>

### `weights.pytorch_state_dict`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[PytorchStateDictWeightsDescr]

</summary>


**PytorchStateDictWeightsDescr:**
#### `weights.pytorch_state_dict.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

#### `weights.pytorch_state_dict.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

#### `weights.pytorch_state_dict.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
##### `weights.pytorch_state_dict.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.pytorch_state_dict.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.pytorch_state_dict.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightspytorch_state_dictauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.pytorch_state_dict.authors.i.name`<sub> str</sub>




##### `weights.pytorch_state_dict.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.pytorch_state_dict.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightspytorch_state_dictparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.pytorch_state_dict.architecture`<sub> Union</sub>


<details><summary>Union[ArchitectureFromFileDescr, ArchitectureFromLibraryDescr]

</summary>


**ArchitectureFromFileDescr:**
##### `weights.pytorch_state_dict.architecture.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

##### `weights.pytorch_state_dict.architecture.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

##### `weights.pytorch_state_dict.architecture.callable`<sub> _internal.types.Identifier</sub>

[*Examples:*](#weightspytorch_state_dictarchitecturecallable) ['MyNetworkClass', 'get_my_model']



##### `weights.pytorch_state_dict.architecture.kwargs`<sub> Dict[str, YamlValue]</sub> ≝ `{}`




**ArchitectureFromLibraryDescr:**
##### `weights.pytorch_state_dict.architecture.callable`<sub> _internal.types.Identifier</sub>

[*Examples:*](#weightspytorch_state_dictarchitecturecallable) ['MyNetworkClass', 'get_my_model']



##### `weights.pytorch_state_dict.architecture.kwargs`<sub> Dict[str, YamlValue]</sub> ≝ `{}`




##### `weights.pytorch_state_dict.architecture.import_from`<sub> str</sub>




</details>

#### `weights.pytorch_state_dict.pytorch_version`<sub> _internal.version_type.Version</sub>




#### `weights.pytorch_state_dict.dependencies`<sub> Optional[EnvironmentFileDescr]</sub> ≝ `None`


<details><summary>Optional[EnvironmentFileDescr]

</summary>


**EnvironmentFileDescr:**
##### `weights.pytorch_state_dict.dependencies.source`<sub> Union</sub>

[*Example:*](#weightspytorch_state_dictdependenciessource) 'environment.yaml'


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

##### `weights.pytorch_state_dict.dependencies.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

</details>

</details>

### `weights.tensorflow_js`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TensorflowJsWeightsDescr]

</summary>


**TensorflowJsWeightsDescr:**
#### `weights.tensorflow_js.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

#### `weights.tensorflow_js.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

#### `weights.tensorflow_js.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
##### `weights.tensorflow_js.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.tensorflow_js.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.tensorflow_js.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstensorflow_jsauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.tensorflow_js.authors.i.name`<sub> str</sub>




##### `weights.tensorflow_js.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.tensorflow_js.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstensorflow_jsparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.tensorflow_js.tensorflow_version`<sub> _internal.version_type.Version</sub>




</details>

### `weights.tensorflow_saved_model_bundle`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TensorflowSavedModelBundleWeightsDescr]

</summary>


**TensorflowSavedModelBundleWeightsDescr:**
#### `weights.tensorflow_saved_model_bundle.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

#### `weights.tensorflow_saved_model_bundle.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

#### `weights.tensorflow_saved_model_bundle.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
##### `weights.tensorflow_saved_model_bundle.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.tensorflow_saved_model_bundle.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.tensorflow_saved_model_bundle.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstensorflow_saved_model_bundleauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.tensorflow_saved_model_bundle.authors.i.name`<sub> str</sub>




##### `weights.tensorflow_saved_model_bundle.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.tensorflow_saved_model_bundle.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstensorflow_saved_model_bundleparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.tensorflow_saved_model_bundle.tensorflow_version`<sub> _internal.version_type.Version</sub>




#### `weights.tensorflow_saved_model_bundle.dependencies`<sub> Optional[EnvironmentFileDescr]</sub> ≝ `None`


<details><summary>Optional[EnvironmentFileDescr]

</summary>


**EnvironmentFileDescr:**
##### `weights.tensorflow_saved_model_bundle.dependencies.source`<sub> Union</sub>

[*Example:*](#weightstensorflow_saved_model_bundledependenciessource) 'environment.yaml'


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

##### `weights.tensorflow_saved_model_bundle.dependencies.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

</details>

</details>

### `weights.torchscript`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TorchscriptWeightsDescr]

</summary>


**TorchscriptWeightsDescr:**
#### `weights.torchscript.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

#### `weights.torchscript.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

#### `weights.torchscript.authors`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
##### `weights.torchscript.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




##### `weights.torchscript.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




##### `weights.torchscript.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstorchscriptauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

##### `weights.torchscript.authors.i.name`<sub> str</sub>




##### `weights.torchscript.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

#### `weights.torchscript.parent`<sub> Optional</sub> ≝ `None`

[*Example:*](#weightstorchscriptparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.torchscript.pytorch_version`<sub> _internal.version_type.Version</sub>




</details>

</details>

## `attachments`<sub> Sequence[_internal.io.FileDescr]</sub> ≝ `[]`


<details><summary>Sequence[_internal.io.FileDescr]

</summary>


**_internal.io.FileDescr:**
### `attachments.i.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

### `attachments.i.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

</details>

## `config`<sub> Dict[str, YamlValue]</sub> ≝ `{}`

[*Example:*](#config) {'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}



## `covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1 or 1:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')

<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl]*]

</summary>

Sequence of Union[Path (PathType(path_type='file'); Predicate(is_absolute)), _internal.io.RelativeFilePath, _internal.url.HttpUrl]
(union_mode='left_to_right'; WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False); PlainSerializer(func=<function _package at 0x7f1d8780d440>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

## `git_repo`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`

[*Example:*](#git_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



## `icon`<sub> Union</sub> ≝ `None`


<details><summary>Union[str*, Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]
  (union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f1d8780d440>, return_type=PydanticUndefined, when_used='unless-none'))
- None


</details>

## `id`<sub> Optional[ModelId]</sub> ≝ `None`




## `id_emoji`<sub> Optional</sub> ≝ `None`



Optional[str (Len(min_length=1, max_length=2))]

## `links`<sub> Sequence[str]</sub> ≝ `[]`

[*Example:*](#links) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



## `maintainers`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[generic.v0_3.Maintainer]

</summary>


**generic.v0_3.Maintainer:**
### `maintainers.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




### `maintainers.i.email`<sub> Optional[Email]</sub> ≝ `None`




### `maintainers.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#maintainersiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `maintainers.i.name`<sub> Optional</sub> ≝ `None`



Optional[str (Predicate(_has_no_slash))]

### `maintainers.i.github_user`<sub> str</sub>




</details>

## `packaged_by`<sub> Sequence[generic.v0_3.Author]</sub> ≝ `[]`


<details><summary>Sequence[generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
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




</details>

## `run_mode`<sub> Optional[model.v0_4.RunMode]</sub> ≝ `None`


<details><summary>Optional[model.v0_4.RunMode]

</summary>


**model.v0_4.RunMode:**
### `run_mode.name`<sub> Union[Literal[deepimagej], str]</sub>




### `run_mode.kwargs`<sub> Dict[str, Any]</sub> ≝ `{}`




</details>

## `tags`<sub> Sequence[str]</sub> ≝ `[]`

[*Example:*](#tags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



## `timestamp`<sub> _internal.types.Datetime</sub> ≝ `root=datetime.datetime(2024, 6, 11, 1, 9, 13, 450967)`




## `training_data`<sub> Union</sub> ≝ `None`


<details><summary>Union[None, dataset.v0_3.LinkedDataset, dataset.v0_3.DatasetDescr, dataset.v0_2.DatasetDescr]

</summary>


**dataset.v0_3.LinkedDataset:**
### `training_data.id`<sub> dataset.v0_3.DatasetId</sub>




**dataset.v0_3.DatasetDescr:**
### `training_data.name`<sub> str</sub>




### `training_data.description`<sub> str</sub>




### `training_data.covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1 or 1:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')

<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl]*]

</summary>

Sequence of Union[Path (PathType(path_type='file'); Predicate(is_absolute)), _internal.io.RelativeFilePath, _internal.url.HttpUrl]
(union_mode='left_to_right'; WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False); PlainSerializer(func=<function _package at 0x7f1d8780d440>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

### `training_data.id_emoji`<sub> Optional</sub> ≝ `None`



Optional[str (Len(min_length=1, max_length=2))]

### `training_data.authors`<sub> Sequence[generic.v0_3.Author]</sub>


<details><summary>Sequence[generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
#### `training_data.authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




#### `training_data.authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




#### `training_data.authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#training_dataauthorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

#### `training_data.authors.i.name`<sub> str</sub>




#### `training_data.authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

### `training_data.attachments`<sub> Sequence[_internal.io.FileDescr]</sub> ≝ `[]`


<details><summary>Sequence[_internal.io.FileDescr]

</summary>


**_internal.io.FileDescr:**
#### `training_data.attachments.i.source`<sub> Union</sub>



Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]

#### `training_data.attachments.i.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

</details>

### `training_data.cite`<sub> Sequence[generic.v0_3.CiteEntry]</sub>


<details><summary>Sequence[generic.v0_3.CiteEntry]

</summary>


**generic.v0_3.CiteEntry:**
#### `training_data.cite.i.text`<sub> str</sub>




#### `training_data.cite.i.doi`<sub> Optional[_internal.types.Doi]</sub> ≝ `None`




#### `training_data.cite.i.url`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`




</details>

### `training_data.license`<sub> Union</sub>

[*Examples:*](#training_datalicense) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId]

### `training_data.config`<sub> Dict[str, YamlValue]</sub> ≝ `{}`

[*Example:*](#training_dataconfig) {'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}



### `training_data.git_repo`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`

[*Example:*](#training_datagit_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



### `training_data.icon`<sub> Union</sub> ≝ `None`


<details><summary>Union[str*, Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]
  (union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f1d8780d440>, return_type=PydanticUndefined, when_used='unless-none'))
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


<details><summary>Sequence[generic.v0_3.Maintainer]

</summary>


**generic.v0_3.Maintainer:**
#### `training_data.maintainers.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




#### `training_data.maintainers.i.email`<sub> Optional[Email]</sub> ≝ `None`




#### `training_data.maintainers.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#training_datamaintainersiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

#### `training_data.maintainers.i.name`<sub> Optional</sub> ≝ `None`



Optional[str (Predicate(_has_no_slash))]

#### `training_data.maintainers.i.github_user`<sub> str</sub>




</details>

### `training_data.tags`<sub> Sequence[str]</sub> ≝ `[]`

[*Example:*](#training_datatags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



### `training_data.version`<sub> Optional</sub> ≝ `None`



Optional[_internal.version_type.Version]

### `training_data.format_version`<sub> Literal[0.3.0]</sub> ≝ `0.3.0`




### `training_data.documentation`<sub> Optional</sub> ≝ `None`

[*Examples:*](#training_datadocumentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']

<details><summary>Optional[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl]*]

</summary>

Optional[Union[Path (PathType(path_type='file'); Predicate(is_absolute)), _internal.io.RelativeFilePath, _internal.url.HttpUrl]
(union_mode='left_to_right'; AfterValidator(_validate_md_suffix); PlainSerializer(func=<function _package at 0x7f1d8780d440>, return_type=PydanticUndefined, when_used='unless-none'))]

</details>

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
  (AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f1d8780d440>, return_type=PydanticUndefined, when_used='unless-none'))
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])
- None


</details>

#### `training_data.badges.i.url`<sub> _internal.url.HttpUrl</sub>

[*Example:*](#training_databadgesiurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



</details>

### `training_data.type`<sub> Literal[dataset]</sub> ≝ `dataset`




### `training_data.id`<sub> Optional[dataset.v0_3.DatasetId]</sub> ≝ `None`




### `training_data.parent`<sub> Optional[dataset.v0_3.DatasetId]</sub> ≝ `None`




### `training_data.source`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`




**dataset.v0_2.DatasetDescr:**
### `training_data.name`<sub> str</sub>




### `training_data.description`<sub> str</sub>




### `training_data.covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff')
[*Example:*](#training_datacovers) 'cover.png'

<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl]*]

</summary>

Sequence of Union[Path (PathType(path_type='file'); Predicate(is_absolute)), _internal.io.RelativeFilePath, _internal.url.HttpUrl]
(union_mode='left_to_right'; WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False); PlainSerializer(func=<function _package at 0x7f1d8780d440>, return_type=PydanticUndefined, when_used='unless-none'))

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


<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f1d8780d440>, return_type=PydanticUndefined, when_used='unless-none'))

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


<details><summary>Union[str*, Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]
  (union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f1d8780d440>, return_type=PydanticUndefined, when_used='unless-none'))
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

### `training_data.rdf_source`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]
(union_mode='left_to_right')]

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
  (AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f1d8780d440>, return_type=PydanticUndefined, when_used='unless-none'))
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])
- None


</details>

#### `training_data.badges.i.url`<sub> _internal.url.HttpUrl</sub>

[*Example:*](#training_databadgesiurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



</details>

### `training_data.documentation`<sub> Optional</sub> ≝ `None`

[*Examples:*](#training_datadocumentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']

<details><summary>Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'))]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f1d8780d440>, return_type=PydanticUndefined, when_used='unless-none'))]

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

# Example values
### `authors.i.orcid`
0000-0001-2345-6789
### `documentation`
- https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md
- README.md

### `inputs.axes.size`
- 10
- {'min': 32, 'step': 16}
- {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

### `inputs.axes.size`
- 10
- {'min': 32, 'step': 16}
- {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

### `inputs.axes.size`
- 10
- {'min': 32, 'step': 16}
- {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

### `inputs.axes.id`
- x
- y
- z

### `inputs.data.type`
- float32
- uint8
- uint16
- int64
- bool

### `inputs.data.type`
- float32
- float64
- uint8
- uint16

### `inputs.data.type`
- float32
- uint8
- uint16
- int64
- bool

### `inputs.data.type`
- float32
- float64
- uint8
- uint16

### `inputs.preprocessing.i.kwargs.axis`
channel
### `inputs.preprocessing.i.kwargs.axis`
channel
### `inputs.preprocessing.i.kwargs.axis`
- channel
- index

### `inputs.preprocessing.i.kwargs.axes`
('batch', 'x', 'y')
### `inputs.preprocessing.i.kwargs.axes`
('batch', 'x', 'y')
### `license`
- CC0-1.0
- MIT
- BSD-2-Clause

### `outputs.axes.size`
- 10
- {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

### `outputs.axes.size`
- 10
- {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

### `outputs.axes.size`
- 10
- {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

### `outputs.axes.size`
- 10
- {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

### `outputs.axes.id`
- x
- y
- z

### `outputs.axes.size`
- 10
- {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

### `outputs.axes.id`
- x
- y
- z

### `outputs.data.type`
- float32
- uint8
- uint16
- int64
- bool

### `outputs.data.type`
- float32
- float64
- uint8
- uint16

### `outputs.data.type`
- float32
- uint8
- uint16
- int64
- bool

### `outputs.data.type`
- float32
- float64
- uint8
- uint16

### `outputs.postprocessing.i.kwargs.axis`
channel
### `outputs.postprocessing.i.kwargs.axis`
channel
### `outputs.postprocessing.i.kwargs.axis`
- channel
- index

### `outputs.postprocessing.i.kwargs.axes`
('batch', 'x', 'y')
### `outputs.postprocessing.i.kwargs.axes`
('batch', 'x', 'y')
### `outputs.postprocessing.i.kwargs.axes`
('batch', 'x', 'y')
### `weights.keras_hdf5.authors.i.orcid`
0000-0001-2345-6789
### `weights.keras_hdf5.parent`
pytorch_state_dict
### `weights.onnx.authors.i.orcid`
0000-0001-2345-6789
### `weights.onnx.parent`
pytorch_state_dict
### `weights.pytorch_state_dict.authors.i.orcid`
0000-0001-2345-6789
### `weights.pytorch_state_dict.parent`
pytorch_state_dict
### `weights.pytorch_state_dict.architecture.callable`
- MyNetworkClass
- get_my_model

### `weights.pytorch_state_dict.architecture.callable`
- MyNetworkClass
- get_my_model

### `weights.pytorch_state_dict.dependencies.source`
environment.yaml
### `weights.tensorflow_js.authors.i.orcid`
0000-0001-2345-6789
### `weights.tensorflow_js.parent`
pytorch_state_dict
### `weights.tensorflow_saved_model_bundle.authors.i.orcid`
0000-0001-2345-6789
### `weights.tensorflow_saved_model_bundle.parent`
pytorch_state_dict
### `weights.tensorflow_saved_model_bundle.dependencies.source`
environment.yaml
### `weights.torchscript.authors.i.orcid`
0000-0001-2345-6789
### `weights.torchscript.parent`
pytorch_state_dict
### `config`
{'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}
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
### `training_data.authors.i.orcid`
0000-0001-2345-6789
### `training_data.license`
- CC0-1.0
- MIT
- BSD-2-Clause

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
### `training_data.documentation`
- https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md
- README.md

### `training_data.badges.i.label`
Open in Colab
### `training_data.badges.i.icon`
https://colab.research.google.com/assets/colab-badge.svg
### `training_data.badges.i.url`
https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb
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

