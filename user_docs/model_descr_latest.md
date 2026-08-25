# 
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
| `field` ≝ `default` | Default field values are indicated after '≝' and make a field optional. However, `type` and `format_version` alwyas need to be set for resource descriptions written as YAML files and determine which bioimage.io specification applies. They are optional only when creating a resource description in Python code using the appropriate, `type` and `format_version` specific class (here: [bioimageio.spec.model.v0_5.ModelDescr](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/model/v0_5.html#ModelDescr)).|
| `field` ≝ 🡇 | Default field value is not displayed in-line, but in the code block below. |
are included when packaging the resource to a .zip archive. The resource description YAML file (RDF) is always included as well as 'rdf.yaml'. |

## `type`<sub> Literal[model]</sub>
Specialized resource type 'model'



## `format_version`<sub> Literal[0.5.14]</sub>
Version of the bioimage.io model description specification used.
When creating a new model always use the latest micro/patch version described here.
The `format_version` is important for any consumer software to understand how to parse the fields.



## `inputs`<sub> Sequence</sub>
Describes the input tensors expected by this model.

<details><summary>Sequence[bioimageio.spec.model.v0_5.InputTensorDescr]

</summary>


**InputTensorDescr:**
### `inputs.id`<sub> TensorId</sub> ≝ `input`
Input tensor id.
No duplicates are allowed across all inputs and outputs.



### `inputs.description`<sub> str</sub> ≝ ``
free text description



### `inputs.axes`<sub> Sequence</sub>
tensor axes

<details><summary>Sequence[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BatchAxis, bioimageio.spec.model.v0_5.ChannelAxis, bioimageio.spec.model.v0_5.IndexInputAxis, bioimageio.spec.model.v0_5.TimeInputAxis, bioimageio.spec.model.v0_5.SpaceInputAxis], Discriminator(discriminator='type', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

</summary>

Sequence[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BatchAxis, bioimageio.spec.model.v0_5.ChannelAxis, bioimageio.spec.model.v0_5.IndexInputAxis, bioimageio.spec.model.v0_5.TimeInputAxis, bioimageio.spec.model.v0_5.SpaceInputAxis], Discriminator(discriminator='type', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

**BatchAxis:**
#### `inputs.axes.id`<sub> AxisId</sub> ≝ `batch`




#### `inputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `inputs.axes.type`<sub> Literal[batch]</sub>




#### `inputs.axes.size`<sub> Optional[Literal[1]]</sub> ≝ `None`
The batch size may be fixed to 1,
otherwise (the default) it may be chosen arbitrarily depending on available memory



**ChannelAxis:**
#### `inputs.axes.id`<sub> AxisId</sub> ≝ `channel`




#### `inputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `inputs.axes.type`<sub> Literal[channel]</sub>




#### `inputs.axes.channel_names`<sub> list[str]</sub>
Name/label for each channel. The number of channels is given by `len(channel_names)`.



**IndexInputAxis:**
#### `inputs.axes.size`<sub> Union</sub>
The size/length of this axis can be specified as
- fixed integer
- parameterized series of valid sizes ([ParameterizedSize][])
- reference to another axis with an optional offset ([SizeReference][])
[*Examples:*](#inputsaxessize) [10, {'min': 32, 'step': 16}, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), ParameterizedSize, SizeReference]

</summary>


**ParameterizedSize:**
##### `inputs.axes.size.min`<sub> int</sub>




##### `inputs.axes.size.step`<sub> int</sub>




**SizeReference:**
##### `inputs.axes.size.tensor_id`<sub> TensorId</sub>
tensor id of the reference axis



##### `inputs.axes.size.axis_id`<sub> AxisId</sub>
axis id of the reference axis



##### `inputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `inputs.axes.id`<sub> AxisId</sub> ≝ `index`




#### `inputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `inputs.axes.type`<sub> Literal[index]</sub>




#### `inputs.axes.concatenable`<sub> bool</sub> ≝ `False`
If a model has a `concatenable` input axis, it can be processed blockwise,
splitting a longer sample axis into blocks matching its input tensor description.
Output axes are concatenable if they have a [SizeReference][] to a concatenable
input axis.



**TimeInputAxis:**
#### `inputs.axes.size`<sub> Union</sub>
The size/length of this axis can be specified as
- fixed integer
- parameterized series of valid sizes ([ParameterizedSize][])
- reference to another axis with an optional offset ([SizeReference][])
[*Examples:*](#inputsaxessize) [10, {'min': 32, 'step': 16}, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), ParameterizedSize, SizeReference]

</summary>


**ParameterizedSize:**
##### `inputs.axes.size.min`<sub> int</sub>




##### `inputs.axes.size.step`<sub> int</sub>




**SizeReference:**
##### `inputs.axes.size.tensor_id`<sub> TensorId</sub>
tensor id of the reference axis



##### `inputs.axes.size.axis_id`<sub> AxisId</sub>
axis id of the reference axis



##### `inputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `inputs.axes.id`<sub> AxisId</sub> ≝ `time`




#### `inputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `inputs.axes.type`<sub> Literal[time]</sub>




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
If a model has a `concatenable` input axis, it can be processed blockwise,
splitting a longer sample axis into blocks matching its input tensor description.
Output axes are concatenable if they have a [SizeReference][] to a concatenable
input axis.



**SpaceInputAxis:**
#### `inputs.axes.size`<sub> Union</sub>
The size/length of this axis can be specified as
- fixed integer
- parameterized series of valid sizes ([ParameterizedSize][])
- reference to another axis with an optional offset ([SizeReference][])
[*Examples:*](#inputsaxessize) [10, {'min': 32, 'step': 16}, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), ParameterizedSize, SizeReference]

</summary>


**ParameterizedSize:**
##### `inputs.axes.size.min`<sub> int</sub>




##### `inputs.axes.size.step`<sub> int</sub>




**SizeReference:**
##### `inputs.axes.size.tensor_id`<sub> TensorId</sub>
tensor id of the reference axis



##### `inputs.axes.size.axis_id`<sub> AxisId</sub>
axis id of the reference axis



##### `inputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `inputs.axes.id`<sub> AxisId</sub> ≝ `x`

[*Examples:*](#inputsaxesid) ['x', 'y', 'z']



#### `inputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `inputs.axes.type`<sub> Literal[space]</sub>




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
If a model has a `concatenable` input axis, it can be processed blockwise,
splitting a longer sample axis into blocks matching its input tensor description.
Output axes are concatenable if they have a [SizeReference][] to a concatenable
input axis.



</details>

### `inputs.test_tensor`<sub> Optional</sub> ≝ `None`
An example tensor to use for testing.
Using the model with the test input tensors is expected to yield the test output tensors.
Each test tensor has be a an ndarray in the
[numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).
The file extension must be '.npy'.

<details><summary>Optional[_internal.io.FileDescr*]

</summary>

Optional[_internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'))]

**_internal.io.FileDescr:**
#### `inputs.test_tensor.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `inputs.test_tensor.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

### `inputs.sample_tensor`<sub> Optional</sub> ≝ `None`
A sample tensor to illustrate a possible input/output for the model,
The sample image primarily serves to inform a human user about an example use case
and is typically stored as .hdf5, .png or .tiff.
It has to be readable by the [imageio library](https://imageio.readthedocs.io/en/stable/formats/index.html#supported-formats)
(numpy's `.npy` format is not supported).
The image dimensionality has to match the number of axes specified in this tensor description.

<details><summary>Optional[_internal.io.FileDescr*]

</summary>

Optional[_internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'))]

**_internal.io.FileDescr:**
#### `inputs.sample_tensor.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `inputs.sample_tensor.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

### `inputs.data`<sub> Union</sub> ≝ `type='float32' range=(None, None) unit='arbitrary unit' scale=1.0 offset=None`
Description of the tensor's data values, optionally per channel.
If specified per channel, the data `type` needs to match across channels.

<details><summary>Union[NominalOrOrdinalDataDescr, IntervalOrRatioDataDescr, Sequence[typing.Union[bioimageio.spec.model.v0_5.NominalOrOrdinalDataDescr, bioimageio.spec.model.v0_5.IntervalOrRatioDataDescr]]*]

</summary>

Union of
- NominalOrOrdinalDataDescr
- IntervalOrRatioDataDescr
- Sequence[typing.Union[bioimageio.spec.model.v0_5.NominalOrOrdinalDataDescr, bioimageio.spec.model.v0_5.IntervalOrRatioDataDescr]]
  (MinLen(min_length=1))


**NominalOrOrdinalDataDescr:**
#### `inputs.data.values`<sub> Union</sub>
A fixed set of nominal or an ascending sequence of ordinal values.
In this case `data.type` is required to be an unsigend integer type, e.g. 'uint8'.
String `values` are interpreted as labels for tensor values 0, ..., N.
Note: as YAML 1.2 does not natively support a "set" datatype,
nominal values should be given as a sequence (aka list/array) as well.

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

#### `inputs.data.range`<sub> tuple</sub> ≝ `(None, None)`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
`None` corresponds to min/max of what can be expressed by **type**.


tuple[float | None, float | None]

#### `inputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `inputs.data.scale`<sub> float</sub> ≝ `1.0`
Scale for data on an interval (or ratio) scale.



#### `inputs.data.offset`<sub> float | None</sub> ≝ `None`
Offset for data on a ratio scale.



**NominalOrOrdinalDataDescr:**
#### `inputs.data.values`<sub> Union</sub>
A fixed set of nominal or an ascending sequence of ordinal values.
In this case `data.type` is required to be an unsigend integer type, e.g. 'uint8'.
String `values` are interpreted as labels for tensor values 0, ..., N.
Note: as YAML 1.2 does not natively support a "set" datatype,
nominal values should be given as a sequence (aka list/array) as well.

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

#### `inputs.data.range`<sub> tuple</sub> ≝ `(None, None)`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
`None` corresponds to min/max of what can be expressed by **type**.


tuple[float | None, float | None]

#### `inputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `inputs.data.scale`<sub> float</sub> ≝ `1.0`
Scale for data on an interval (or ratio) scale.



#### `inputs.data.offset`<sub> float | None</sub> ≝ `None`
Offset for data on a ratio scale.



</details>

### `inputs.output_of`<sub> ModelId | None</sub> ≝ `None`
If this input tensor is the output of another model, specify the model id here.
This model's input id must match the output id of the referenced model.



### `inputs.optional`<sub> bool</sub> ≝ `False`
indicates that this tensor may be `None`



### `inputs.pad`<sub> Union</sub> ≝ `None`
Explicitly specify how to pad this input tensor.

Use `axes[i].pad` to specify padding width.

Note:
  Non-blockwise sample prediction only applies padding for axes with a `pad` specification.

<details><summary>Union[ConstantPadding, EdgePadding, ReflectPadding, SymmetricPadding, None]

</summary>


**ConstantPadding:**
#### `inputs.pad.mode`<sub> Literal[constant]</sub> ≝ `constant`




#### `inputs.pad.value`<sub> int | float</sub> ≝ `0`




**EdgePadding:**
#### `inputs.pad.mode`<sub> Literal[edge]</sub> ≝ `edge`




**ReflectPadding:**
#### `inputs.pad.mode`<sub> Literal[reflect]</sub> ≝ `reflect`




**SymmetricPadding:**
#### `inputs.pad.mode`<sub> Literal[symmetric]</sub> ≝ `symmetric`




</details>

### `inputs.preprocessing`<sub> list</sub> ≝ `[]`
Description of how this input should be preprocessed.

notes:
- If preprocessing does not start with an 'ensure_dtype' entry, it is added
  to ensure an input tensor's data type matches the input tensor's data description.
- If preprocessing does not end with an 'ensure_dtype' or 'binarize' entry, an
  'ensure_dtype' step is added to ensure preprocessing steps are not unintentionally
  changing the data type.

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BinarizeDescr, bioimageio.spec.model.v0_5.ClipDescr, bioimageio.spec.model.v0_5.EnsureDtypeDescr, bioimageio.spec.model.v0_5.FixedZeroMeanUnitVarianceDescr, bioimageio.spec.model.v0_5.ScaleLinearDescr, bioimageio.spec.model.v0_5.ScaleRangeDescr, bioimageio.spec.model.v0_5.SigmoidDescr, bioimageio.spec.model.v0_5.SoftmaxDescr, bioimageio.spec.model.v0_5.ZeroMeanUnitVarianceDescr], Discriminator(discriminator='id', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BinarizeDescr, bioimageio.spec.model.v0_5.ClipDescr, bioimageio.spec.model.v0_5.EnsureDtypeDescr, bioimageio.spec.model.v0_5.FixedZeroMeanUnitVarianceDescr, bioimageio.spec.model.v0_5.ScaleLinearDescr, bioimageio.spec.model.v0_5.ScaleRangeDescr, bioimageio.spec.model.v0_5.SigmoidDescr, bioimageio.spec.model.v0_5.SoftmaxDescr, bioimageio.spec.model.v0_5.ZeroMeanUnitVarianceDescr], Discriminator(discriminator='id', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

**BinarizeDescr:**
#### `inputs.preprocessing.id`<sub> Literal[binarize]</sub>




#### `inputs.preprocessing.kwargs`<sub> BinarizeKwargs | bioimageio.spec</sub>


<details><summary>BinarizeKwargs | bioimageio.spec.model.v0_5.BinarizeAlongAxisKwargs

</summary>


**BinarizeKwargs:**
##### `inputs.preprocessing.kwargs.threshold`<sub> float</sub>
The fixed threshold



**BinarizeAlongAxisKwargs:**
##### `inputs.preprocessing.kwargs.threshold`<sub> list[float]</sub>
The fixed threshold values along `axis`



##### `inputs.preprocessing.kwargs.axis`<sub> AxisId</sub>
The `threshold` axis
[*Example:*](#inputspreprocessingkwargsaxis) 'channel'



</details>

**ClipDescr:**
#### `inputs.preprocessing.id`<sub> Literal[clip]</sub>




#### `inputs.preprocessing.kwargs`<sub> ClipKwargs</sub>


<details><summary>ClipKwargs

</summary>


**ClipKwargs:**
##### `inputs.preprocessing.kwargs.min`<sub> float | None</sub> ≝ `None`
Minimum value for clipping.

Exclusive with [min_percentile][]



##### `inputs.preprocessing.kwargs.min_percentile`<sub> Optional</sub> ≝ `None`
Minimum percentile for clipping.

Exclusive with [min][].

In range [0, 100).


Optional[float (Interval(gt=None, ge=0, lt=100, le=None))]

##### `inputs.preprocessing.kwargs.max`<sub> float | None</sub> ≝ `None`
Maximum value for clipping.

Exclusive with `max_percentile`.



##### `inputs.preprocessing.kwargs.max_percentile`<sub> Optional</sub> ≝ `None`
Maximum percentile for clipping.

Exclusive with `max`.

In range (1, 100].


Optional[float (Interval(gt=1, ge=None, lt=None, le=100))]

##### `inputs.preprocessing.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to determine percentiles jointly,

i.e. axes to reduce to compute min/max from `min_percentile`/`max_percentile`.
For example to clip 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape with clipped values per channel, specify `axes=('batch', 'x', 'y')`.
To clip samples independently, leave out the 'batch' axis.

Only valid if `min_percentile` and/or `max_percentile` are set.

Default: Compute percentiles over all axes jointly.
[*Example:*](#inputspreprocessingkwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

</details>

**EnsureDtypeDescr:**
#### `inputs.preprocessing.id`<sub> Literal[ensure_dtype]</sub>




#### `inputs.preprocessing.kwargs`<sub> EnsureDtypeKwargs</sub>


<details><summary>EnsureDtypeKwargs

</summary>


**EnsureDtypeKwargs:**
##### `inputs.preprocessing.kwargs.dtype`<sub> Literal</sub>



Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

</details>

**FixedZeroMeanUnitVarianceDescr:**
#### `inputs.preprocessing.id`<sub> Literal</sub>



Literal[fixed_zero_mean_unit_variance]

#### `inputs.preprocessing.kwargs`<sub> FixedZeroMeanUnitVarianceKwargs </sub>


<details><summary>FixedZeroMeanUnitVarianceKwargs | bioimageio.spec.model.v0_5.FixedZeroMeanUnitVarianceAlongAxisKwargs

</summary>


**FixedZeroMeanUnitVarianceKwargs:**
##### `inputs.preprocessing.kwargs.mean`<sub> float</sub>
The mean value to normalize with.



##### `inputs.preprocessing.kwargs.std`<sub> float</sub>
The standard deviation value to normalize with.



**FixedZeroMeanUnitVarianceAlongAxisKwargs:**
##### `inputs.preprocessing.kwargs.mean`<sub> list[float]</sub>
The mean value(s) to normalize with.



##### `inputs.preprocessing.kwargs.std`<sub> list</sub>
The standard deviation value(s) to normalize with.
Size must match `mean` values.


list[typing.Annotated[float, Ge(ge=1e-06)]]

##### `inputs.preprocessing.kwargs.axis`<sub> AxisId</sub>
The axis of the mean/std values to normalize each entry along that dimension
separately.
[*Examples:*](#inputspreprocessingkwargsaxis) ['channel', 'index']



</details>

**ScaleLinearDescr:**
#### `inputs.preprocessing.id`<sub> Literal[scale_linear]</sub>




#### `inputs.preprocessing.kwargs`<sub> ScaleLinearKwargs | bioimageio.s</sub>


<details><summary>ScaleLinearKwargs | bioimageio.spec.model.v0_5.ScaleLinearAlongAxisKwargs

</summary>


**ScaleLinearKwargs:**
##### `inputs.preprocessing.kwargs.gain`<sub> float</sub> ≝ `1.0`
multiplicative factor



##### `inputs.preprocessing.kwargs.offset`<sub> float</sub> ≝ `0.0`
additive term



**ScaleLinearAlongAxisKwargs:**
##### `inputs.preprocessing.kwargs.axis`<sub> AxisId</sub>
The axis of gain and offset values.
[*Example:*](#inputspreprocessingkwargsaxis) 'channel'



##### `inputs.preprocessing.kwargs.gain`<sub> Union</sub> ≝ `1.0`
multiplicative factor


Union[float, list[float] (MinLen(min_length=1))]

##### `inputs.preprocessing.kwargs.offset`<sub> Union</sub> ≝ `0.0`
additive term


Union[float, list[float] (MinLen(min_length=1))]

</details>

**ScaleRangeDescr:**
#### `inputs.preprocessing.id`<sub> Literal[scale_range]</sub>




#### `inputs.preprocessing.kwargs`<sub> ScaleRangeKwargs</sub> ≝ `axes=None min_percentile=0.0 max_percentile=100.0 eps=1e-06 reference_tensor=None`


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `inputs.preprocessing.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to normalize jointly, i.e. axes to reduce to compute the min/max percentile value.
For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
To normalize samples independently, leave out the "batch" axis.
Default: Scale all axes jointly.
[*Example:*](#inputspreprocessingkwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `inputs.preprocessing.kwargs.min_percentile`<sub> float</sub> ≝ `0.0`
The lower percentile used to determine the value to align with zero.



##### `inputs.preprocessing.kwargs.max_percentile`<sub> float</sub> ≝ `100.0`
The upper percentile used to determine the value to align with one.
Has to be bigger than `min_percentile`.
The range is 1 to 100 instead of 0 to 100 to avoid mistakenly
accepting percentiles specified in the range 0.0 to 1.0.



##### `inputs.preprocessing.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability.
`out = (tensor - v_lower) / (v_upper - v_lower + eps)`;
with `v_lower,v_upper` values at the respective percentiles.



##### `inputs.preprocessing.kwargs.reference_tensor`<sub> TensorId | None</sub> ≝ `None`
ID of the unprocessed input tensor to compute the percentiles from.
Default: The tensor itself.



</details>

**SigmoidDescr:**
#### `inputs.preprocessing.id`<sub> Literal[sigmoid]</sub>




**SoftmaxDescr:**
#### `inputs.preprocessing.id`<sub> Literal[softmax]</sub>




#### `inputs.preprocessing.kwargs`<sub> SoftmaxKwargs</sub> ≝ `axis='channel'`


<details><summary>SoftmaxKwargs

</summary>


**SoftmaxKwargs:**
##### `inputs.preprocessing.kwargs.axis`<sub> AxisId</sub> ≝ `channel`
The axis to apply the softmax function along.
Note:
    Defaults to 'channel' axis
    (which may not exist, in which case
    a different axis id has to be specified).
[*Example:*](#inputspreprocessingkwargsaxis) 'channel'



</details>

**ZeroMeanUnitVarianceDescr:**
#### `inputs.preprocessing.id`<sub> Literal[zero_mean_unit_variance]</sub>




#### `inputs.preprocessing.kwargs`<sub> ZeroMeanUnitVarianceKwargs</sub> ≝ `axes=None eps=1e-06`


<details><summary>ZeroMeanUnitVarianceKwargs

</summary>


**ZeroMeanUnitVarianceKwargs:**
##### `inputs.preprocessing.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to normalize jointly, i.e. axes to reduce to compute mean/std.
For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
To normalize each sample independently leave out the 'batch' axis.
Default: Scale all axes jointly.
[*Example:*](#inputspreprocessingkwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `inputs.preprocessing.kwargs.eps`<sub> float</sub> ≝ `1e-06`
epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`.



</details>

</details>

</details>

## `name`<sub> str</sub>
A human-readable name of this model.
It should be no longer than 64 characters
and may only contain letter, number, underscore, minus, parentheses and spaces.
We recommend to chose a name that refers to the model's task and image modality.



## `outputs`<sub> Sequence</sub>
Describes the output tensors.

<details><summary>Sequence[bioimageio.spec.model.v0_5.OutputTensorDescr]

</summary>


**OutputTensorDescr:**
### `outputs.id`<sub> TensorId</sub> ≝ `output`
Output tensor id.
No duplicates are allowed across all inputs and outputs.



### `outputs.description`<sub> str</sub> ≝ ``
free text description



### `outputs.axes`<sub> Sequence</sub>
tensor axes

<details><summary>Sequence[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BatchAxis, bioimageio.spec.model.v0_5.ChannelAxis, bioimageio.spec.model.v0_5.IndexOutputAxis, typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7fa5d1371760>, custom_error_type=None, custom_error_message=None, custom_error_context=None)], typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7fa5d1371760>, custom_error_type=None, custom_error_message=None, custom_error_context=None)]], Discriminator(discriminator='type', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

</summary>

Sequence[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BatchAxis, bioimageio.spec.model.v0_5.ChannelAxis, bioimageio.spec.model.v0_5.IndexOutputAxis, typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7fa5d1371760>, custom_error_type=None, custom_error_message=None, custom_error_context=None)], typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7fa5d1371760>, custom_error_type=None, custom_error_message=None, custom_error_context=None)]], Discriminator(discriminator='type', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

**BatchAxis:**
#### `outputs.axes.id`<sub> AxisId</sub> ≝ `batch`




#### `outputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `outputs.axes.type`<sub> Literal[batch]</sub>




#### `outputs.axes.size`<sub> Optional[Literal[1]]</sub> ≝ `None`
The batch size may be fixed to 1,
otherwise (the default) it may be chosen arbitrarily depending on available memory



**ChannelAxis:**
#### `outputs.axes.id`<sub> AxisId</sub> ≝ `channel`




#### `outputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `outputs.axes.type`<sub> Literal[channel]</sub>




#### `outputs.axes.channel_names`<sub> list[str]</sub>
Name/label for each channel. The number of channels is given by `len(channel_names)`.



**IndexOutputAxis:**
#### `outputs.axes.id`<sub> AxisId</sub> ≝ `index`




#### `outputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `outputs.axes.type`<sub> Literal[index]</sub>




#### `outputs.axes.size`<sub> Union</sub>
The size/length of this axis can be specified as
- fixed integer
- reference to another axis with an optional offset ([SizeReference][])
- data dependent size using [DataDependentSize][] (size is only known after model inference)
[*Examples:*](#outputsaxessize) [10, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), SizeReference, DataDependentSize]

</summary>


**SizeReference:**
##### `outputs.axes.size.tensor_id`<sub> TensorId</sub>
tensor id of the reference axis



##### `outputs.axes.size.axis_id`<sub> AxisId</sub>
axis id of the reference axis



##### `outputs.axes.size.offset`<sub> int</sub> ≝ `0`




**DataDependentSize:**
##### `outputs.axes.size.min`<sub> int</sub> ≝ `1`




##### `outputs.axes.size.max`<sub> int | None</sub> ≝ `None`




</details>

**TimeOutputAxis:**
#### `outputs.axes.size`<sub> Union</sub>
The size/length of this axis can be specified as
- fixed integer
- reference to another axis with an optional offset (see [SizeReference][])
[*Examples:*](#outputsaxessize) [10, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), SizeReference]

</summary>


**SizeReference:**
##### `outputs.axes.size.tensor_id`<sub> TensorId</sub>
tensor id of the reference axis



##### `outputs.axes.size.axis_id`<sub> AxisId</sub>
axis id of the reference axis



##### `outputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `outputs.axes.id`<sub> AxisId</sub> ≝ `time`




#### `outputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `outputs.axes.type`<sub> Literal[time]</sub>




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
The halo should be cropped from the output tensor to avoid boundary effects.
It is to be cropped from both sides, i.e. `size_after_crop = size - 2 * halo`.
To document a halo that is already cropped by the model use `size.offset` instead.



#### `outputs.axes.size`<sub> SizeReference</sub>
reference to another axis with an optional offset (see [SizeReference][])
[*Example:*](#outputsaxessize) {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

<details><summary>SizeReference

</summary>


**SizeReference:**
##### `outputs.axes.size.tensor_id`<sub> TensorId</sub>
tensor id of the reference axis



##### `outputs.axes.size.axis_id`<sub> AxisId</sub>
axis id of the reference axis



##### `outputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `outputs.axes.id`<sub> AxisId</sub> ≝ `time`




#### `outputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `outputs.axes.type`<sub> Literal[time]</sub>




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
The size/length of this axis can be specified as
- fixed integer
- reference to another axis with an optional offset (see [SizeReference][])
[*Examples:*](#outputsaxessize) [10, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

<details><summary>Union[int (Gt(gt=0)), SizeReference]

</summary>


**SizeReference:**
##### `outputs.axes.size.tensor_id`<sub> TensorId</sub>
tensor id of the reference axis



##### `outputs.axes.size.axis_id`<sub> AxisId</sub>
axis id of the reference axis



##### `outputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `outputs.axes.id`<sub> AxisId</sub> ≝ `x`

[*Examples:*](#outputsaxesid) ['x', 'y', 'z']



#### `outputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `outputs.axes.type`<sub> Literal[space]</sub>




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
The halo should be cropped from the output tensor to avoid boundary effects.
It is to be cropped from both sides, i.e. `size_after_crop = size - 2 * halo`.
To document a halo that is already cropped by the model use `size.offset` instead.



#### `outputs.axes.size`<sub> SizeReference</sub>
reference to another axis with an optional offset (see [SizeReference][])
[*Example:*](#outputsaxessize) {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

<details><summary>SizeReference

</summary>


**SizeReference:**
##### `outputs.axes.size.tensor_id`<sub> TensorId</sub>
tensor id of the reference axis



##### `outputs.axes.size.axis_id`<sub> AxisId</sub>
axis id of the reference axis



##### `outputs.axes.size.offset`<sub> int</sub> ≝ `0`




</details>

#### `outputs.axes.id`<sub> AxisId</sub> ≝ `x`

[*Examples:*](#outputsaxesid) ['x', 'y', 'z']



#### `outputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `outputs.axes.type`<sub> Literal[space]</sub>




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

### `outputs.test_tensor`<sub> Optional</sub> ≝ `None`
An example tensor to use for testing.
Using the model with the test input tensors is expected to yield the test output tensors.
Each test tensor has be a an ndarray in the
[numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).
The file extension must be '.npy'.

<details><summary>Optional[_internal.io.FileDescr*]

</summary>

Optional[_internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'))]

**_internal.io.FileDescr:**
#### `outputs.test_tensor.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `outputs.test_tensor.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

### `outputs.sample_tensor`<sub> Optional</sub> ≝ `None`
A sample tensor to illustrate a possible input/output for the model,
The sample image primarily serves to inform a human user about an example use case
and is typically stored as .hdf5, .png or .tiff.
It has to be readable by the [imageio library](https://imageio.readthedocs.io/en/stable/formats/index.html#supported-formats)
(numpy's `.npy` format is not supported).
The image dimensionality has to match the number of axes specified in this tensor description.

<details><summary>Optional[_internal.io.FileDescr*]

</summary>

Optional[_internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'))]

**_internal.io.FileDescr:**
#### `outputs.sample_tensor.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `outputs.sample_tensor.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

### `outputs.data`<sub> Union</sub> ≝ `type='float32' range=(None, None) unit='arbitrary unit' scale=1.0 offset=None`
Description of the tensor's data values, optionally per channel.
If specified per channel, the data `type` needs to match across channels.

<details><summary>Union[NominalOrOrdinalDataDescr, IntervalOrRatioDataDescr, Sequence[typing.Union[bioimageio.spec.model.v0_5.NominalOrOrdinalDataDescr, bioimageio.spec.model.v0_5.IntervalOrRatioDataDescr]]*]

</summary>

Union of
- NominalOrOrdinalDataDescr
- IntervalOrRatioDataDescr
- Sequence[typing.Union[bioimageio.spec.model.v0_5.NominalOrOrdinalDataDescr, bioimageio.spec.model.v0_5.IntervalOrRatioDataDescr]]
  (MinLen(min_length=1))


**NominalOrOrdinalDataDescr:**
#### `outputs.data.values`<sub> Union</sub>
A fixed set of nominal or an ascending sequence of ordinal values.
In this case `data.type` is required to be an unsigend integer type, e.g. 'uint8'.
String `values` are interpreted as labels for tensor values 0, ..., N.
Note: as YAML 1.2 does not natively support a "set" datatype,
nominal values should be given as a sequence (aka list/array) as well.

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

#### `outputs.data.range`<sub> tuple</sub> ≝ `(None, None)`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
`None` corresponds to min/max of what can be expressed by **type**.


tuple[float | None, float | None]

#### `outputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `outputs.data.scale`<sub> float</sub> ≝ `1.0`
Scale for data on an interval (or ratio) scale.



#### `outputs.data.offset`<sub> float | None</sub> ≝ `None`
Offset for data on a ratio scale.



**NominalOrOrdinalDataDescr:**
#### `outputs.data.values`<sub> Union</sub>
A fixed set of nominal or an ascending sequence of ordinal values.
In this case `data.type` is required to be an unsigend integer type, e.g. 'uint8'.
String `values` are interpreted as labels for tensor values 0, ..., N.
Note: as YAML 1.2 does not natively support a "set" datatype,
nominal values should be given as a sequence (aka list/array) as well.

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

#### `outputs.data.range`<sub> tuple</sub> ≝ `(None, None)`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
`None` corresponds to min/max of what can be expressed by **type**.


tuple[float | None, float | None]

#### `outputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `outputs.data.scale`<sub> float</sub> ≝ `1.0`
Scale for data on an interval (or ratio) scale.



#### `outputs.data.offset`<sub> float | None</sub> ≝ `None`
Offset for data on a ratio scale.



</details>

### `outputs.postprocessing`<sub> list</sub> ≝ `[]`
Description of how this output should be postprocessed.

note: `postprocessing` always ends with an 'ensure_dtype' operation.
      If not given this is added to cast to this tensor's `data.type`.

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BinarizeDescr, bioimageio.spec.model.v0_5.CellposeFlowDynamicsDescr, bioimageio.spec.model.v0_5.ClipDescr, bioimageio.spec.model.v0_5.CustomProcessingDescr, bioimageio.spec.model.v0_5.EnsureDtypeDescr, bioimageio.spec.model.v0_5.FixedZeroMeanUnitVarianceDescr, bioimageio.spec.model.v0_5.ScaleLinearDescr, bioimageio.spec.model.v0_5.ScaleMeanVarianceDescr, bioimageio.spec.model.v0_5.ScaleRangeDescr, bioimageio.spec.model.v0_5.SigmoidDescr, bioimageio.spec.model.v0_5.SoftmaxDescr, bioimageio.spec.model.v0_5.StardistPostprocessingDescr, bioimageio.spec.model.v0_5.ZeroMeanUnitVarianceDescr], Discriminator(discriminator='id', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BinarizeDescr, bioimageio.spec.model.v0_5.CellposeFlowDynamicsDescr, bioimageio.spec.model.v0_5.ClipDescr, bioimageio.spec.model.v0_5.CustomProcessingDescr, bioimageio.spec.model.v0_5.EnsureDtypeDescr, bioimageio.spec.model.v0_5.FixedZeroMeanUnitVarianceDescr, bioimageio.spec.model.v0_5.ScaleLinearDescr, bioimageio.spec.model.v0_5.ScaleMeanVarianceDescr, bioimageio.spec.model.v0_5.ScaleRangeDescr, bioimageio.spec.model.v0_5.SigmoidDescr, bioimageio.spec.model.v0_5.SoftmaxDescr, bioimageio.spec.model.v0_5.StardistPostprocessingDescr, bioimageio.spec.model.v0_5.ZeroMeanUnitVarianceDescr], Discriminator(discriminator='id', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

**BinarizeDescr:**
#### `outputs.postprocessing.id`<sub> Literal[binarize]</sub>




#### `outputs.postprocessing.kwargs`<sub> BinarizeKwargs | bioimageio.spec</sub>


<details><summary>BinarizeKwargs | bioimageio.spec.model.v0_5.BinarizeAlongAxisKwargs

</summary>


**BinarizeKwargs:**
##### `outputs.postprocessing.kwargs.threshold`<sub> float</sub>
The fixed threshold



**BinarizeAlongAxisKwargs:**
##### `outputs.postprocessing.kwargs.threshold`<sub> list[float]</sub>
The fixed threshold values along `axis`



##### `outputs.postprocessing.kwargs.axis`<sub> AxisId</sub>
The `threshold` axis
[*Example:*](#outputspostprocessingkwargsaxis) 'channel'



</details>

**CellposeFlowDynamicsDescr:**
#### `outputs.postprocessing.id`<sub> Literal[cellpose_flow_dynamics]</sub>




#### `outputs.postprocessing.kwargs`<sub> CellposeFlowDynamicsKwargs</sub>


<details><summary>CellposeFlowDynamicsKwargs

</summary>


**CellposeFlowDynamicsKwargs:**
##### `outputs.postprocessing.kwargs.cellprob_threshold`<sub> float</sub>




##### `outputs.postprocessing.kwargs.flow_threshold`<sub> float</sub>




##### `outputs.postprocessing.kwargs.do_3D`<sub> bool</sub>




##### `outputs.postprocessing.kwargs.min_size`<sub> int</sub> ≝ `15`
Minimum size of objects to keep, in pixels. Default is 15, which is the default in Cellpose. Set to 0 to disable filtering by size.



##### `outputs.postprocessing.kwargs.output_dtype`<sub> Literal[uint16, uint32]</sub> ≝ `uint16`




</details>

**ClipDescr:**
#### `outputs.postprocessing.id`<sub> Literal[clip]</sub>




#### `outputs.postprocessing.kwargs`<sub> ClipKwargs</sub>


<details><summary>ClipKwargs

</summary>


**ClipKwargs:**
##### `outputs.postprocessing.kwargs.min`<sub> float | None</sub> ≝ `None`
Minimum value for clipping.

Exclusive with [min_percentile][]



##### `outputs.postprocessing.kwargs.min_percentile`<sub> Optional</sub> ≝ `None`
Minimum percentile for clipping.

Exclusive with [min][].

In range [0, 100).


Optional[float (Interval(gt=None, ge=0, lt=100, le=None))]

##### `outputs.postprocessing.kwargs.max`<sub> float | None</sub> ≝ `None`
Maximum value for clipping.

Exclusive with `max_percentile`.



##### `outputs.postprocessing.kwargs.max_percentile`<sub> Optional</sub> ≝ `None`
Maximum percentile for clipping.

Exclusive with `max`.

In range (1, 100].


Optional[float (Interval(gt=1, ge=None, lt=None, le=100))]

##### `outputs.postprocessing.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to determine percentiles jointly,

i.e. axes to reduce to compute min/max from `min_percentile`/`max_percentile`.
For example to clip 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape with clipped values per channel, specify `axes=('batch', 'x', 'y')`.
To clip samples independently, leave out the 'batch' axis.

Only valid if `min_percentile` and/or `max_percentile` are set.

Default: Compute percentiles over all axes jointly.
[*Example:*](#outputspostprocessingkwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

</details>

**CustomProcessingDescr:**
#### `outputs.postprocessing.source`<sub> Union</sub>
FileSource: Python source file (included when packaging the model).


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `outputs.postprocessing.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `outputs.postprocessing.id`<sub> Literal[custom]</sub>




#### `outputs.postprocessing.callable`<sub> str</sub>
Name of the callable class or factory function defined in ``source``.

At runtime: ``op = callable(**kwargs)``, then ``result = op(*output_tensors)``
per image.  Both a class with ``__call__`` and a factory function returning
a callable satisfy this protocol.
[*Examples:*](#outputspostprocessingcallable) ['my_postprocess_factory', 'MyPostprocessClass']



#### `outputs.postprocessing.kwargs`<sub> dict[str, YamlValue]</sub> ≝ `{}`
Keyword arguments forwarded to the callable (``__init__`` or factory).



**EnsureDtypeDescr:**
#### `outputs.postprocessing.id`<sub> Literal[ensure_dtype]</sub>




#### `outputs.postprocessing.kwargs`<sub> EnsureDtypeKwargs</sub>


<details><summary>EnsureDtypeKwargs

</summary>


**EnsureDtypeKwargs:**
##### `outputs.postprocessing.kwargs.dtype`<sub> Literal</sub>



Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

</details>

**FixedZeroMeanUnitVarianceDescr:**
#### `outputs.postprocessing.id`<sub> Literal</sub>



Literal[fixed_zero_mean_unit_variance]

#### `outputs.postprocessing.kwargs`<sub> FixedZeroMeanUnitVarianceKwargs </sub>


<details><summary>FixedZeroMeanUnitVarianceKwargs | bioimageio.spec.model.v0_5.FixedZeroMeanUnitVarianceAlongAxisKwargs

</summary>


**FixedZeroMeanUnitVarianceKwargs:**
##### `outputs.postprocessing.kwargs.mean`<sub> float</sub>
The mean value to normalize with.



##### `outputs.postprocessing.kwargs.std`<sub> float</sub>
The standard deviation value to normalize with.



**FixedZeroMeanUnitVarianceAlongAxisKwargs:**
##### `outputs.postprocessing.kwargs.mean`<sub> list[float]</sub>
The mean value(s) to normalize with.



##### `outputs.postprocessing.kwargs.std`<sub> list</sub>
The standard deviation value(s) to normalize with.
Size must match `mean` values.


list[typing.Annotated[float, Ge(ge=1e-06)]]

##### `outputs.postprocessing.kwargs.axis`<sub> AxisId</sub>
The axis of the mean/std values to normalize each entry along that dimension
separately.
[*Examples:*](#outputspostprocessingkwargsaxis) ['channel', 'index']



</details>

**ScaleLinearDescr:**
#### `outputs.postprocessing.id`<sub> Literal[scale_linear]</sub>




#### `outputs.postprocessing.kwargs`<sub> ScaleLinearKwargs | bioimageio.s</sub>


<details><summary>ScaleLinearKwargs | bioimageio.spec.model.v0_5.ScaleLinearAlongAxisKwargs

</summary>


**ScaleLinearKwargs:**
##### `outputs.postprocessing.kwargs.gain`<sub> float</sub> ≝ `1.0`
multiplicative factor



##### `outputs.postprocessing.kwargs.offset`<sub> float</sub> ≝ `0.0`
additive term



**ScaleLinearAlongAxisKwargs:**
##### `outputs.postprocessing.kwargs.axis`<sub> AxisId</sub>
The axis of gain and offset values.
[*Example:*](#outputspostprocessingkwargsaxis) 'channel'



##### `outputs.postprocessing.kwargs.gain`<sub> Union</sub> ≝ `1.0`
multiplicative factor


Union[float, list[float] (MinLen(min_length=1))]

##### `outputs.postprocessing.kwargs.offset`<sub> Union</sub> ≝ `0.0`
additive term


Union[float, list[float] (MinLen(min_length=1))]

</details>

**ScaleMeanVarianceDescr:**
#### `outputs.postprocessing.id`<sub> Literal[scale_mean_variance]</sub>




#### `outputs.postprocessing.kwargs`<sub> ScaleMeanVarianceKwargs</sub>


<details><summary>ScaleMeanVarianceKwargs

</summary>


**ScaleMeanVarianceKwargs:**
##### `outputs.postprocessing.kwargs.reference_tensor`<sub> TensorId</sub>
ID of unprocessed input tensor to match.



##### `outputs.postprocessing.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to normalize jointly, i.e. axes to reduce to compute mean/std.
For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
To normalize samples independently, leave out the 'batch' axis.
Default: Scale all axes jointly.
[*Example:*](#outputspostprocessingkwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `outputs.postprocessing.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability:
`out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean.`



</details>

**ScaleRangeDescr:**
#### `outputs.postprocessing.id`<sub> Literal[scale_range]</sub>




#### `outputs.postprocessing.kwargs`<sub> ScaleRangeKwargs</sub> ≝ `axes=None min_percentile=0.0 max_percentile=100.0 eps=1e-06 reference_tensor=None`


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `outputs.postprocessing.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to normalize jointly, i.e. axes to reduce to compute the min/max percentile value.
For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
To normalize samples independently, leave out the "batch" axis.
Default: Scale all axes jointly.
[*Example:*](#outputspostprocessingkwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `outputs.postprocessing.kwargs.min_percentile`<sub> float</sub> ≝ `0.0`
The lower percentile used to determine the value to align with zero.



##### `outputs.postprocessing.kwargs.max_percentile`<sub> float</sub> ≝ `100.0`
The upper percentile used to determine the value to align with one.
Has to be bigger than `min_percentile`.
The range is 1 to 100 instead of 0 to 100 to avoid mistakenly
accepting percentiles specified in the range 0.0 to 1.0.



##### `outputs.postprocessing.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability.
`out = (tensor - v_lower) / (v_upper - v_lower + eps)`;
with `v_lower,v_upper` values at the respective percentiles.



##### `outputs.postprocessing.kwargs.reference_tensor`<sub> TensorId | None</sub> ≝ `None`
ID of the unprocessed input tensor to compute the percentiles from.
Default: The tensor itself.



</details>

**SigmoidDescr:**
#### `outputs.postprocessing.id`<sub> Literal[sigmoid]</sub>




**SoftmaxDescr:**
#### `outputs.postprocessing.id`<sub> Literal[softmax]</sub>




#### `outputs.postprocessing.kwargs`<sub> SoftmaxKwargs</sub> ≝ `axis='channel'`


<details><summary>SoftmaxKwargs

</summary>


**SoftmaxKwargs:**
##### `outputs.postprocessing.kwargs.axis`<sub> AxisId</sub> ≝ `channel`
The axis to apply the softmax function along.
Note:
    Defaults to 'channel' axis
    (which may not exist, in which case
    a different axis id has to be specified).
[*Example:*](#outputspostprocessingkwargsaxis) 'channel'



</details>

**StardistPostprocessingDescr:**
#### `outputs.postprocessing.id`<sub> Literal[stardist_postprocessing]</sub>




#### `outputs.postprocessing.kwargs`<sub> StardistPostprocessingKwargs2D |</sub>


<details><summary>StardistPostprocessingKwargs2D | bioimageio.spec.model.v0_5.StardistPostprocessingKwargs3D

</summary>


**StardistPostprocessingKwargs2D:**
##### `outputs.postprocessing.kwargs.prob_threshold`<sub> float</sub>
The probability threshold for object candidate selection.



##### `outputs.postprocessing.kwargs.nms_threshold`<sub> float</sub>
The IoU threshold for non-maximum suppression.



##### `outputs.postprocessing.kwargs.n_rays`<sub> int</sub>
Number of radial lines (rays) cast from the center of an object to its boundary.



##### `outputs.postprocessing.kwargs.grid`<sub> tuple[int, int]</sub>
Grid size of network predictions.



##### `outputs.postprocessing.kwargs.b`<sub> int | tuple</sub>
Border region in which object probability is set to zero.


int | tuple[tuple[int, int], tuple[int, int]]

**StardistPostprocessingKwargs3D:**
##### `outputs.postprocessing.kwargs.prob_threshold`<sub> float</sub>
The probability threshold for object candidate selection.



##### `outputs.postprocessing.kwargs.nms_threshold`<sub> float</sub>
The IoU threshold for non-maximum suppression.



##### `outputs.postprocessing.kwargs.n_rays`<sub> int</sub>
Number of radial lines (rays) cast from the center of an object to its boundary.



##### `outputs.postprocessing.kwargs.grid`<sub> tuple[int, int, int]</sub>
Grid size of network predictions.



##### `outputs.postprocessing.kwargs.b`<sub> int | tuple</sub>
Border region in which object probability is set to zero.


int | tuple[tuple[int, int], tuple[int, int], tuple[int, int]]

##### `outputs.postprocessing.kwargs.anisotropy`<sub> tuple[float, float, float]</sub>
Anisotropy factors for 3D star-convex polyhedra, i.e. the physical pixel size along each spatial axis.



##### `outputs.postprocessing.kwargs.overlap_label`<sub> int | None</sub> ≝ `None`
Optional label to apply to any area of overlapping predicted objects.



</details>

**ZeroMeanUnitVarianceDescr:**
#### `outputs.postprocessing.id`<sub> Literal[zero_mean_unit_variance]</sub>




#### `outputs.postprocessing.kwargs`<sub> ZeroMeanUnitVarianceKwargs</sub> ≝ `axes=None eps=1e-06`


<details><summary>ZeroMeanUnitVarianceKwargs

</summary>


**ZeroMeanUnitVarianceKwargs:**
##### `outputs.postprocessing.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to normalize jointly, i.e. axes to reduce to compute mean/std.
For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
To normalize each sample independently leave out the 'batch' axis.
Default: Scale all axes jointly.
[*Example:*](#outputspostprocessingkwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `outputs.postprocessing.kwargs.eps`<sub> float</sub> ≝ `1e-06`
epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`.



</details>

</details>

</details>

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
FileSource: Source of the weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.keras_hdf5.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.keras_hdf5.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_3.Author] | None

</summary>


**generic.v0_3.Author:**
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

#### `weights.keras_hdf5.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightskeras_hdf5parent) 'pytorch_state_dict'

<details><summary>Optional[Literal[keras_hdf5, ..., torchscript]]

</summary>

Optional[Literal[keras_hdf5, keras_v3, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

</details>

#### `weights.keras_hdf5.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.keras_hdf5.tensorflow_version`<sub> _internal.version_type.Version</sub>
TensorFlow version used to create these weights.



</details>

### `weights.keras_v3`<sub> KerasV3WeightsDescr | None</sub> ≝ `None`


<details><summary>KerasV3WeightsDescr | None

</summary>


**KerasV3WeightsDescr:**
#### `weights.keras_v3.source`<sub> Union</sub>
FileSource: Source of the .keras weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.keras_v3.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.keras_v3.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_3.Author] | None

</summary>


**generic.v0_3.Author:**
##### `weights.keras_v3.authors.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



##### `weights.keras_v3.authors.email`<sub> Email | None</sub> ≝ `None`
Email



##### `weights.keras_v3.authors.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#weightskeras_v3authorsorcid) '0000-0001-2345-6789'



##### `weights.keras_v3.authors.name`<sub> str</sub>




##### `weights.keras_v3.authors.github_user`<sub> str | None</sub> ≝ `None`




</details>

#### `weights.keras_v3.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightskeras_v3parent) 'pytorch_state_dict'

<details><summary>Optional[Literal[keras_hdf5, ..., torchscript]]

</summary>

Optional[Literal[keras_hdf5, keras_v3, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

</details>

#### `weights.keras_v3.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.keras_v3.keras_version`<sub> _internal.version_type.Version</sub>
Keras version used to create these weights.



#### `weights.keras_v3.backend`<sub> tuple</sub>
Keras backend used to create these weights.


tuple[typing.Literal['tensorflow', 'jax', 'torch'], bioimageio.spec._internal.version_type.Version]

</details>

### `weights.onnx`<sub> OnnxWeightsDescr | None</sub> ≝ `None`


<details><summary>OnnxWeightsDescr | None

</summary>


**OnnxWeightsDescr:**
#### `weights.onnx.source`<sub> Union</sub>
FileSource: Source of the weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.onnx.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.onnx.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_3.Author] | None

</summary>


**generic.v0_3.Author:**
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

#### `weights.onnx.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightsonnxparent) 'pytorch_state_dict'

<details><summary>Optional[Literal[keras_hdf5, ..., torchscript]]

</summary>

Optional[Literal[keras_hdf5, keras_v3, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

</details>

#### `weights.onnx.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.onnx.opset_version`<sub> int</sub>
ONNX opset version



#### `weights.onnx.external_data`<sub> Optional</sub> ≝ `None`
Source of the external ONNX data file holding the weights.
(If present **source** holds the ONNX architecture without weights).

<details><summary>Optional[_internal.io.FileDescr*]

</summary>

Optional[_internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix='.data', case_sensitive=True, allow_any_parent_suffix=False); )]

**_internal.io.FileDescr:**
##### `weights.onnx.external_data.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

##### `weights.onnx.external_data.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

</details>

### `weights.pytorch_state_dict`<sub> PytorchStateDictWeightsDescr | N</sub> ≝ `None`


<details><summary>PytorchStateDictWeightsDescr | None

</summary>


**PytorchStateDictWeightsDescr:**
#### `weights.pytorch_state_dict.source`<sub> Union</sub>
FileSource: Source of the weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.pytorch_state_dict.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.pytorch_state_dict.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_3.Author] | None

</summary>


**generic.v0_3.Author:**
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

#### `weights.pytorch_state_dict.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightspytorch_state_dictparent) 'pytorch_state_dict'

<details><summary>Optional[Literal[keras_hdf5, ..., torchscript]]

</summary>

Optional[Literal[keras_hdf5, keras_v3, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

</details>

#### `weights.pytorch_state_dict.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.pytorch_state_dict.architecture`<sub> ArchitectureFromFileDescr | bioi</sub>


<details><summary>ArchitectureFromFileDescr | bioimageio.spec.model.v0_5.ArchitectureFromLibraryDescr

</summary>


**ArchitectureFromFileDescr:**
##### `weights.pytorch_state_dict.architecture.source`<sub> Union</sub>
FileSource: Architecture source file


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

##### `weights.pytorch_state_dict.architecture.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

##### `weights.pytorch_state_dict.architecture.callable`<sub> _internal.types.Identifier</sub>
Identifier of the callable that returns a torch.nn.Module instance.
[*Examples:*](#weightspytorch_state_dictarchitecturecallable) ['MyNetworkClass', 'get_my_model']



##### `weights.pytorch_state_dict.architecture.kwargs`<sub> dict[str, YamlValue]</sub> ≝ `{}`
key word arguments for the `callable`



**ArchitectureFromLibraryDescr:**
##### `weights.pytorch_state_dict.architecture.callable`<sub> _internal.types.Identifier</sub>
Identifier of the callable that returns a torch.nn.Module instance.
[*Examples:*](#weightspytorch_state_dictarchitecturecallable) ['MyNetworkClass', 'get_my_model']



##### `weights.pytorch_state_dict.architecture.kwargs`<sub> dict[str, YamlValue]</sub> ≝ `{}`
key word arguments for the `callable`



##### `weights.pytorch_state_dict.architecture.import_from`<sub> str</sub>
Where to import the callable from, i.e. `from <import_from> import <callable>`



</details>

#### `weights.pytorch_state_dict.pytorch_version`<sub> _internal.version_type.Version</sub>
Version of the PyTorch library used.
If `architecture.depencencies` is specified it has to include pytorch and any version pinning has to be compatible.



#### `weights.pytorch_state_dict.dependencies`<sub> Optional</sub> ≝ `None`
Custom depencies beyond pytorch described in a Conda environment file.
Allows to specify custom dependencies, see conda docs:
- [Exporting an environment file across platforms](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#exporting-an-environment-file-across-platforms)
- [Creating an environment file manually](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually)

The conda environment file should include pytorch and any version pinning has to be compatible with
**pytorch_version**.

<details><summary>Optional[_internal.io.FileDescr*]

</summary>

Optional[_internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix=('.yaml', '.yml'), case_sensitive=True, allow_any_parent_suffix=False); )]

**_internal.io.FileDescr:**
##### `weights.pytorch_state_dict.dependencies.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

##### `weights.pytorch_state_dict.dependencies.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

#### `weights.pytorch_state_dict.strict`<sub> bool</sub> ≝ `True`
Whether to allow missing or unexpected keys or to be strict about the architecture matching the state dict weights.



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

#### `weights.tensorflow_js.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_3.Author] | None

</summary>


**generic.v0_3.Author:**
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

#### `weights.tensorflow_js.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightstensorflow_jsparent) 'pytorch_state_dict'

<details><summary>Optional[Literal[keras_hdf5, ..., torchscript]]

</summary>

Optional[Literal[keras_hdf5, keras_v3, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

</details>

#### `weights.tensorflow_js.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.tensorflow_js.tensorflow_version`<sub> _internal.version_type.Version</sub>
Version of the TensorFlow library used.



</details>

### `weights.tensorflow_saved_model_bundle`<sub> TensorflowSavedModelBundleWeight</sub> ≝ `None`


<details><summary>TensorflowSavedModelBundleWeightsDescr | None

</summary>


**TensorflowSavedModelBundleWeightsDescr:**
#### `weights.tensorflow_saved_model_bundle.source`<sub> Union</sub>
FileSource: 
The multi-file weights.
All required files/folders should be a zip archive.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.tensorflow_saved_model_bundle.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.tensorflow_saved_model_bundle.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_3.Author] | None

</summary>


**generic.v0_3.Author:**
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

#### `weights.tensorflow_saved_model_bundle.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightstensorflow_saved_model_bundleparent) 'pytorch_state_dict'

<details><summary>Optional[Literal[keras_hdf5, ..., torchscript]]

</summary>

Optional[Literal[keras_hdf5, keras_v3, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

</details>

#### `weights.tensorflow_saved_model_bundle.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.tensorflow_saved_model_bundle.tensorflow_version`<sub> _internal.version_type.Version</sub>
Version of the TensorFlow library used.



#### `weights.tensorflow_saved_model_bundle.dependencies`<sub> Optional</sub> ≝ `None`
Custom dependencies beyond tensorflow.
Should include tensorflow and any version pinning has to be compatible with **tensorflow_version**.

<details><summary>Optional[_internal.io.FileDescr*]

</summary>

Optional[_internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix=('.yaml', '.yml'), case_sensitive=True, allow_any_parent_suffix=False); )]

**_internal.io.FileDescr:**
##### `weights.tensorflow_saved_model_bundle.dependencies.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

##### `weights.tensorflow_saved_model_bundle.dependencies.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

</details>

### `weights.torchscript`<sub> TorchscriptWeightsDescr | None</sub> ≝ `None`


<details><summary>TorchscriptWeightsDescr | None

</summary>


**TorchscriptWeightsDescr:**
#### `weights.torchscript.source`<sub> Union</sub>
FileSource: Source of the weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.torchscript.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

#### `weights.torchscript.authors`<sub> list</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>list[bioimageio.spec.generic.v0_3.Author] | None

</summary>


**generic.v0_3.Author:**
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

#### `weights.torchscript.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightstorchscriptparent) 'pytorch_state_dict'

<details><summary>Optional[Literal[keras_hdf5, ..., torchscript]]

</summary>

Optional[Literal[keras_hdf5, keras_v3, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

</details>

#### `weights.torchscript.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.torchscript.pytorch_version`<sub> _internal.version_type.Version</sub>
Version of the PyTorch library used.



</details>

</details>

## `attachments`<sub> list</sub> ≝ `[]`
file attachments

<details><summary>list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none')]]

**_internal.io.FileDescr:**
### `attachments.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `attachments.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

## `authors`<sub> list</sub> ≝ `[]`
The authors are the creators of the model RDF and the primary points of contact.

<details><summary>list[bioimageio.spec.generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
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

## `cite`<sub> list</sub> ≝ `[]`
citations

<details><summary>list[bioimageio.spec.generic.v0_3.CiteEntry]

</summary>


**generic.v0_3.CiteEntry:**
### `cite.text`<sub> str</sub>
free text description



### `cite.doi`<sub> _internal.types.Doi | None</sub> ≝ `None`
A digital object identifier (DOI) is the prefered citation reference.
See https://www.doi.org/ for details.
Note:
    Either **doi** or **url** have to be specified.



### `cite.url`<sub> _internal.url.HttpUrl | None</sub> ≝ `None`
URL to cite (preferably specify a **doi** instead/also).
Note:
    Either **doi** or **url** have to be specified.



</details>

## `config`<sub> Config</sub> ≝ 🡇
```python
Config(bioimageio=BioimageioConfig(reproducibility_tolerance=(), funded_by=None, architecture_type=None, architecture_description=None, modality=None, target_structure=[], task=None, new_version=None, out_of_scope_use=None, bias_risks_limitations=BiasRisksLimitations(known_biases='In general bioimage models may suffer from biases caused by:\n\n- Imaging protocol dependencies\n- Use of a specific cell type\n- Species-specific training data limitations\n\n', risks='Common risks in bioimage analysis include:\n\n- Erroneously assuming generalization to unseen experimental conditions\n- Trusting (overconfident) model outputs without validation\n- Misinterpretation of results\n\n', limitations=None, recommendations='Users (both direct and downstream) should be made aware of the risks, biases and limitations of the model.'), model_parameter_count=None, training=TrainingDetails(training_preprocessing=None, training_epochs=None, training_batch_size=None, initial_learning_rate=None, learning_rate_schedule=None, loss_function=None, loss_function_kwargs={}, optimizer=None, optimizer_kwargs={}, regularization=None, training_duration=None), inference_time=None, memory_requirements_inference=None, memory_requirements_training=None, evaluations=[], environmental_impact=EnvironmentalImpact(hardware_type=None, hours_used=None, cloud_provider=None, compute_region=None, co2_emitted=None)), stardist=None)
```



<details><summary>Config

</summary>


**Config:**
### `config.bioimageio`<sub> BioimageioConfig</sub> ≝ 🡇
```python
BioimageioConfig(reproducibility_tolerance=(), funded_by=None, architecture_type=None, architecture_description=None, modality=None, target_structure=[], task=None, new_version=None, out_of_scope_use=None, bias_risks_limitations=BiasRisksLimitations(known_biases='In general bioimage models may suffer from biases caused by:\n\n- Imaging protocol dependencies\n- Use of a specific cell type\n- Species-specific training data limitations\n\n', risks='Common risks in bioimage analysis include:\n\n- Erroneously assuming generalization to unseen experimental conditions\n- Trusting (overconfident) model outputs without validation\n- Misinterpretation of results\n\n', limitations=None, recommendations='Users (both direct and downstream) should be made aware of the risks, biases and limitations of the model.'), model_parameter_count=None, training=TrainingDetails(training_preprocessing=None, training_epochs=None, training_batch_size=None, initial_learning_rate=None, learning_rate_schedule=None, loss_function=None, loss_function_kwargs={}, optimizer=None, optimizer_kwargs={}, regularization=None, training_duration=None), inference_time=None, memory_requirements_inference=None, memory_requirements_training=None, evaluations=[], environmental_impact=EnvironmentalImpact(hardware_type=None, hours_used=None, cloud_provider=None, compute_region=None, co2_emitted=None))
```



<details><summary>BioimageioConfig

</summary>


**BioimageioConfig:**
#### `config.bioimageio.reproducibility_tolerance`<sub> Sequence</sub> ≝ `()`
Tolerances to allow when reproducing the model's test outputs
from the model's test inputs.
Only the first entry matching tensor id and weights format is considered.

<details><summary>Sequence[bioimageio.spec.model.v0_5.ReproducibilityTolerance]

</summary>


**ReproducibilityTolerance:**
##### `config.bioimageio.reproducibility_tolerance.relative_tolerance`<sub> float</sub> ≝ `0.001`
Maximum relative tolerance of reproduced test tensor.



##### `config.bioimageio.reproducibility_tolerance.absolute_tolerance`<sub> float</sub> ≝ `0.001`
Maximum absolute tolerance of reproduced test tensor.



##### `config.bioimageio.reproducibility_tolerance.mismatched_elements_per_million`<sub> int</sub> ≝ `100`
Maximum number of mismatched elements/pixels per million to tolerate.



##### `config.bioimageio.reproducibility_tolerance.output_ids`<sub> Sequence</sub> ≝ `()`
Limits the output tensor IDs these reproducibility details apply to.


Sequence[bioimageio.spec.model.v0_5.TensorId]

##### `config.bioimageio.reproducibility_tolerance.weights_formats`<sub> Sequence</sub> ≝ `()`
Limits the weights formats these details apply to.

<details><summary>Sequence[typing.Literal['keras_hdf5', 'keras_v3', 'onnx', 'pytorch_state_dict', 'tensorflow_js', 'tensorflow_saved_model_bundle', 'torchscript']]

</summary>

Sequence[typing.Literal['keras_hdf5', 'keras_v3', 'onnx', 'pytorch_state_dict', 'tensorflow_js', 'tensorflow_saved_model_bundle', 'torchscript']]

</details>

</details>

#### `config.bioimageio.funded_by`<sub> str | None</sub> ≝ `None`
Funding agency, grant number if applicable



#### `config.bioimageio.architecture_type`<sub> Optional</sub> ≝ `None`
Model architecture type, e.g., 3D U-Net, ResNet, transformer


Optional[str (MaxLen(max_length=32))]

#### `config.bioimageio.architecture_description`<sub> str | None</sub> ≝ `None`
Text description of model architecture.



#### `config.bioimageio.modality`<sub> str | None</sub> ≝ `None`
Input modality, e.g., fluorescence microscopy, electron microscopy



#### `config.bioimageio.target_structure`<sub> list[str]</sub> ≝ `[]`
Biological structure(s) the model is designed to analyze, e.g., nuclei, mitochondria, cells



#### `config.bioimageio.task`<sub> str | None</sub> ≝ `None`
Bioimage-specific task type, e.g., segmentation, classification, detection, denoising



#### `config.bioimageio.new_version`<sub> ModelId | None</sub> ≝ `None`
A new version of this model exists with a different model id.



#### `config.bioimageio.out_of_scope_use`<sub> str | None</sub> ≝ `None`
Describe how the model may be misused in bioimage analysis contexts and what users should **not** do with the model.



#### `config.bioimageio.bias_risks_limitations`<sub> BiasRisksLimitations</sub> ≝ 🡇
```python
BiasRisksLimitations(known_biases='In general bioimage models may suffer from biases caused by:\n\n- Imaging protocol dependencies\n- Use of a specific cell type\n- Species-specific training data limitations\n\n', risks='Common risks in bioimage analysis include:\n\n- Erroneously assuming generalization to unseen experimental conditions\n- Trusting (overconfident) model outputs without validation\n- Misinterpretation of results\n\n', limitations=None, recommendations='Users (both direct and downstream) should be made aware of the risks, biases and limitations of the model.')
```

Description of known bias, risks, and technical limitations for in-scope model use.

<details><summary>BiasRisksLimitations

</summary>


**BiasRisksLimitations:**
##### `config.bioimageio.bias_risks_limitations.known_biases`<sub> str</sub> ≝ 🡇
```python
('In general bioimage models may suffer from biases caused by:\n'
 '\n'
 '- Imaging protocol dependencies\n'
 '- Use of a specific cell type\n'
 '- Species-specific training data limitations\n'
 '\n')
```

Biases in training data or model behavior.



##### `config.bioimageio.bias_risks_limitations.risks`<sub> str</sub> ≝ 🡇
```python
('Common risks in bioimage analysis include:\n'
 '\n'
 '- Erroneously assuming generalization to unseen experimental conditions\n'
 '- Trusting (overconfident) model outputs without validation\n'
 '- Misinterpretation of results\n'
 '\n')
```

Potential risks in the context of bioimage analysis.



##### `config.bioimageio.bias_risks_limitations.limitations`<sub> str | None</sub> ≝ `None`
Technical limitations and failure modes.



##### `config.bioimageio.bias_risks_limitations.recommendations`<sub> str</sub> ≝ 🡇
```python
'Users (both direct and downstream) should be made aware of the risks, biases and limitations of the model.'
```

Mitigation strategies regarding `known_biases`, `risks`, and `limitations`, as well as applicable best practices.

Consider:
- How to use a validation dataset?
- How to manually validate?
- Feasibility of domain adaptation for different experimental setups?



</details>

#### `config.bioimageio.model_parameter_count`<sub> int | None</sub> ≝ `None`
Total number of model parameters.



#### `config.bioimageio.training`<sub> TrainingDetails</sub> ≝ 🡇
```python
TrainingDetails(training_preprocessing=None, training_epochs=None, training_batch_size=None, initial_learning_rate=None, learning_rate_schedule=None, loss_function=None, loss_function_kwargs={}, optimizer=None, optimizer_kwargs={}, regularization=None, training_duration=None)
```

Details on how the model was trained.

<details><summary>TrainingDetails

</summary>


**TrainingDetails:**
##### `config.bioimageio.training.training_preprocessing`<sub> str | None</sub> ≝ `None`
Detailed image preprocessing steps during model training:

Mention:
- *Normalization methods*
- *Augmentation strategies*
- *Resizing/resampling procedures*
- *Artifact handling*



##### `config.bioimageio.training.training_epochs`<sub> float | None</sub> ≝ `None`
Number of training epochs.



##### `config.bioimageio.training.training_batch_size`<sub> float | None</sub> ≝ `None`
Batch size used in training.



##### `config.bioimageio.training.initial_learning_rate`<sub> float | None</sub> ≝ `None`
Initial learning rate used in training.



##### `config.bioimageio.training.learning_rate_schedule`<sub> str | None</sub> ≝ `None`
Learning rate schedule used in training.



##### `config.bioimageio.training.loss_function`<sub> str | None</sub> ≝ `None`
Loss function used in training, e.g. nn.MSELoss.



##### `config.bioimageio.training.loss_function_kwargs`<sub> dict[str, YamlValue]</sub> ≝ `{}`
key word arguments for the `loss_function`



##### `config.bioimageio.training.optimizer`<sub> str | None</sub> ≝ `None`
optimizer, e.g. torch.optim.Adam



##### `config.bioimageio.training.optimizer_kwargs`<sub> dict[str, YamlValue]</sub> ≝ `{}`
key word arguments for the `optimizer`



##### `config.bioimageio.training.regularization`<sub> str | None</sub> ≝ `None`
Regularization techniques used during training, e.g. drop-out or weight decay.



##### `config.bioimageio.training.training_duration`<sub> float | None</sub> ≝ `None`
Total training duration in hours.



</details>

#### `config.bioimageio.inference_time`<sub> str | None</sub> ≝ `None`
Average inference time per image/tile. Specify hardware and image size. Multiple examples can be given.



#### `config.bioimageio.memory_requirements_inference`<sub> str | None</sub> ≝ `None`
GPU memory needed for inference. Multiple examples with different image size can be given.



#### `config.bioimageio.memory_requirements_training`<sub> str | None</sub> ≝ `None`
GPU memory needed for training. Multiple examples with different image/batch sizes can be given.



#### `config.bioimageio.evaluations`<sub> list</sub> ≝ `[]`
Quantitative model evaluations.

Note:
    At the moment we recommend to include only a single test dataset
    (with evaluation factors that may mark subsets of the dataset)
    to avoid confusion and make the presentation of results cleaner.

<details><summary>list[bioimageio.spec.model.v0_5.Evaluation]

</summary>


**Evaluation:**
##### `config.bioimageio.evaluations.model_id`<sub> ModelId | None</sub> ≝ `None`
Model being evaluated.



##### `config.bioimageio.evaluations.dataset_id`<sub> dataset.v0_3.DatasetId</sub>
Dataset used for evaluation.



##### `config.bioimageio.evaluations.dataset_source`<sub> _internal.url.HttpUrl</sub>
Source of the dataset.



##### `config.bioimageio.evaluations.dataset_role`<sub> Literal</sub>
Role of the dataset used for evaluation.

- `train`: dataset was (part of) the training data
- `validation`: dataset was (part of) the validation data used during training, e.g. used for model selection or hyperparameter tuning
- `test`: dataset was (part of) the designated test data; not used during training or validation, but acquired from the same source/distribution as training data
- `independent`: dataset is entirely independent test data; not used during training or validation, and acquired from a different source/distribution than training data
- `unknown`: role of the dataset is unknown; choose this if you are not certain if (a subset) of the data was seen by the model during training.


Literal[train, validation, test, independent, unknown]

##### `config.bioimageio.evaluations.sample_count`<sub> int</sub>
Number of evaluated samples.



##### `config.bioimageio.evaluations.evaluation_factors`<sub> list</sub>
(Abbreviations of) each evaluation factor.

Evaluation factors are criteria along which model performance is evaluated, e.g. different image conditions
like 'low SNR', 'high cell density', or different biological conditions like 'cell type A', 'cell type B'.
An 'overall' factor may be included to summarize performance across all conditions.


list[typing.Annotated[str, MaxLen(max_length=16)]]

##### `config.bioimageio.evaluations.evaluation_factors_long`<sub> list[str]</sub>
Descriptions (long form) of each evaluation factor.



##### `config.bioimageio.evaluations.metrics`<sub> list</sub>
(Abbreviations of) metrics used for evaluation.


list[typing.Annotated[str, MaxLen(max_length=16)]]

##### `config.bioimageio.evaluations.metrics_long`<sub> list[str]</sub>
Description of each metric used.



##### `config.bioimageio.evaluations.results`<sub> list[list[str | float | int]]</sub>
Results for each metric (rows; outer list) and each evaluation factor (columns; inner list).



##### `config.bioimageio.evaluations.results_summary`<sub> str | None</sub> ≝ `None`
Interpretation of results for general audience.

Consider:
    - Overall model performance
    - Comparison to existing methods
    - Limitations and areas for improvement



</details>

#### `config.bioimageio.environmental_impact`<sub> EnvironmentalImpact</sub> ≝ 🡇
```python
EnvironmentalImpact(hardware_type=None, hours_used=None, cloud_provider=None, compute_region=None, co2_emitted=None)
```

Environmental considerations for model training and deployment

<details><summary>EnvironmentalImpact

</summary>


**EnvironmentalImpact:**
##### `config.bioimageio.environmental_impact.hardware_type`<sub> str | None</sub> ≝ `None`
GPU/CPU specifications



##### `config.bioimageio.environmental_impact.hours_used`<sub> float | None</sub> ≝ `None`
Total compute hours



##### `config.bioimageio.environmental_impact.cloud_provider`<sub> str | None</sub> ≝ `None`
If applicable



##### `config.bioimageio.environmental_impact.compute_region`<sub> str | None</sub> ≝ `None`
Geographic location



##### `config.bioimageio.environmental_impact.co2_emitted`<sub> float | None</sub> ≝ `None`
kg CO2 equivalent

Carbon emissions can be estimated using the [Machine Learning Impact calculator](https://mlco2.github.io/impact#compute) presented in [Lacoste et al. (2019)](https://arxiv.org/abs/1910.09700).



</details>

</details>

### `config.stardist`<sub> YamlValue</sub> ≝ `None`




</details>

## `covers`<sub> list</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1 or 1:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')
[*Example:*](#covers) [{'source': 'cover.png'}]

<details><summary>list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg'), case_sensitive=False, allow_any_parent_suffix=False)]]

</summary>

list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg'), case_sensitive=False, allow_any_parent_suffix=False)]]

**_internal.io.FileDescr:**
### `covers.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `covers.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

## `description`<sub> str</sub> ≝ ``
A string containing a brief description.



## `documentation`<sub> Optional</sub> ≝ `None`
Additional model documentation.
The recommended documentation source file name is `README.md`. An `.md` suffix is mandatory.
The documentation should include a '#[#] Validation' (sub)section
with details on how to quantitatively validate the model on unseen data.

<details><summary>Optional[_internal.io.FileDescr*]

</summary>

Optional[_internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix='.md', case_sensitive=True, allow_any_parent_suffix=False); )]

**_internal.io.FileDescr:**
### `documentation.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `documentation.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

## `git_repo`<sub> _internal.url.HttpUrl | None</sub> ≝ `None`
A URL to the Git repository where the resource is being developed.
[*Example:*](#git_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



## `icon`<sub> Union</sub> ≝ `None`
An icon for illustration, e.g. on bioimage.io

<details><summary>Union[str*, _internal.io.FileDescr*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- _internal.io.FileDescr
  (AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'))
- None


**_internal.io.FileDescr:**
### `icon.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `icon.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

## `id`<sub> ModelId | None</sub> ≝ `None`
bioimage.io-wide unique resource identifier
assigned by bioimage.io; version **un**specific.



## `id_emoji`<sub> Optional</sub> ≝ `None`
UTF-8 emoji for display alongside the `id`.


Optional[str (Len(min_length=1, max_length=2); )]

## `license`<sub> Union</sub> ≝ `None`
A [SPDX license identifier](https://spdx.org/licenses/) or a custom license file.
[*Examples:*](#license) ['CC0-1.0', 'MIT', 'BSD-2-Clause']

<details><summary>Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId, None, _internal.io.FileDescr*]

</summary>

Union of
- _internal.license_id.LicenseId
- _internal.license_id.DeprecatedLicenseId
- None
- _internal.io.FileDescr
  (AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'))


**_internal.io.FileDescr:**
### `license.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `license.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

## `links`<sub> list[str]</sub> ≝ `[]`
IDs of other bioimage.io resources
[*Example:*](#links) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



## `maintainers`<sub> list</sub> ≝ `[]`
Maintainers of this resource.
If not specified, `authors` are maintainers and at least some of them has to specify their `github_user` name

<details><summary>list[bioimageio.spec.generic.v0_3.Maintainer]

</summary>


**generic.v0_3.Maintainer:**
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



Optional[str (Predicate(_has_no_slash))]

### `maintainers.github_user`<sub> str</sub>




</details>

## `packaged_by`<sub> list</sub> ≝ `[]`
The persons that have packaged and uploaded this model.
Only required if those persons differ from the `authors`.

<details><summary>list[bioimageio.spec.generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
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
### `parent.version`<sub> _internal.version_type.Version |</sub> ≝ `None`
The version of the linked resource following SemVer 2.0.


_internal.version_type.Version | None

### `parent.id`<sub> ModelId</sub>
A valid model `id` from the bioimage.io collection.



</details>

## `run_mode`<sub> model.v0_4.RunMode | None</sub> ≝ `None`
Custom run mode for this model: for more complex prediction procedures like test time
data augmentation that currently cannot be expressed in the specification.
No standard run modes are defined yet.

<details><summary>model.v0_4.RunMode | None

</summary>


**model.v0_4.RunMode:**
### `run_mode.name`<sub> Union[Literal[deepimagej], str]</sub>
Run mode name



### `run_mode.kwargs`<sub> dict[str, typing.Any]</sub> ≝ `{}`
Run mode specific key word arguments



</details>

## `tags`<sub> list[str]</sub> ≝ `[]`
Associated tags
[*Example:*](#tags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



## `timestamp`<sub> _internal.types.Datetime</sub> ≝ `root=datetime.datetime(2026, 8, 25, 13, 21, 10, 808110, tzinfo=datetime.timezone.utc)`
Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat).
(In Python a datetime object is valid, too).



## `training_data`<sub> None | bioimageio.spec.dataset.v</sub> ≝ `None`
The dataset used to train this model

<details><summary>None | bioimageio.spec.dataset.v0_3.LinkedDataset | bioimageio.spec.dataset.v0_3.DatasetDescr | bioimageio.spec.dataset.v0_2.DatasetDescr

</summary>

None | bioimageio.spec.dataset.v0_3.LinkedDataset | bioimageio.spec.dataset.v0_3.DatasetDescr | bioimageio.spec.dataset.v0_2.DatasetDescr

**dataset.v0_3.LinkedDataset:**
### `training_data.version`<sub> _internal.version_type.Version |</sub> ≝ `None`
The version of the linked resource following SemVer 2.0.


_internal.version_type.Version | None

### `training_data.id`<sub> dataset.v0_3.DatasetId</sub>
A valid dataset `id` from the bioimage.io collection.



**dataset.v0_3.DatasetDescr:**
### `training_data.name`<sub> str</sub>
A human-friendly name of the resource description.
May only contains letters, digits, underscore, minus, parentheses and spaces.



### `training_data.description`<sub> str</sub> ≝ ``
A string containing a brief description.



### `training_data.covers`<sub> list</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1 or 1:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')
[*Example:*](#training_datacovers) [{'source': 'cover.png'}]

<details><summary>list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg'), case_sensitive=False, allow_any_parent_suffix=False)]]

</summary>

list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg'), case_sensitive=False, allow_any_parent_suffix=False)]]

**_internal.io.FileDescr:**
#### `training_data.covers.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `training_data.covers.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

### `training_data.documentation`<sub> Optional</sub> ≝ `None`
Additional model documentation.
The recommended documentation source file name is `README.md`. An `.md` suffix is mandatory.

<details><summary>Optional[_internal.io.FileDescr*]

</summary>

Optional[_internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix='.md', case_sensitive=True, allow_any_parent_suffix=False); )]

**_internal.io.FileDescr:**
#### `training_data.documentation.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `training_data.documentation.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

### `training_data.id_emoji`<sub> Optional</sub> ≝ `None`
UTF-8 emoji for display alongside the `id`.


Optional[str (Len(min_length=1, max_length=2); )]

### `training_data.authors`<sub> list</sub> ≝ `[]`
The authors are the creators of this resource description and the primary points of contact.

<details><summary>list[bioimageio.spec.generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
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

### `training_data.attachments`<sub> list</sub> ≝ `[]`
file attachments

<details><summary>list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none')]]

**_internal.io.FileDescr:**
#### `training_data.attachments.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `training_data.attachments.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

### `training_data.cite`<sub> list</sub> ≝ `[]`
citations

<details><summary>list[bioimageio.spec.generic.v0_3.CiteEntry]

</summary>


**generic.v0_3.CiteEntry:**
#### `training_data.cite.text`<sub> str</sub>
free text description



#### `training_data.cite.doi`<sub> _internal.types.Doi | None</sub> ≝ `None`
A digital object identifier (DOI) is the prefered citation reference.
See https://www.doi.org/ for details.
Note:
    Either **doi** or **url** have to be specified.



#### `training_data.cite.url`<sub> _internal.url.HttpUrl | None</sub> ≝ `None`
URL to cite (preferably specify a **doi** instead/also).
Note:
    Either **doi** or **url** have to be specified.



</details>

### `training_data.license`<sub> Union</sub> ≝ `None`
A [SPDX license identifier](https://spdx.org/licenses/) or a custom license file.
[*Examples:*](#training_datalicense) ['CC0-1.0', 'MIT', 'BSD-2-Clause']

<details><summary>Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId, None, _internal.io.FileDescr*]

</summary>

Union of
- _internal.license_id.LicenseId
- _internal.license_id.DeprecatedLicenseId
- None
- _internal.io.FileDescr
  (AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'))


**_internal.io.FileDescr:**
#### `training_data.license.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `training_data.license.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

### `training_data.git_repo`<sub> _internal.url.HttpUrl | None</sub> ≝ `None`
A URL to the Git repository where the resource is being developed.
[*Example:*](#training_datagit_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



### `training_data.icon`<sub> Union</sub> ≝ `None`
An icon for illustration, e.g. on bioimage.io

<details><summary>Union[str*, _internal.io.FileDescr*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- _internal.io.FileDescr
  (AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7fa5d17e19e0>, return_type=PydanticUndefined, when_used='unless-none'))
- None


**_internal.io.FileDescr:**
#### `training_data.icon.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `training_data.icon.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

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
If not specified, `authors` are maintainers and at least some of them has to specify their `github_user` name

<details><summary>list[bioimageio.spec.generic.v0_3.Maintainer]

</summary>


**generic.v0_3.Maintainer:**
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



Optional[str (Predicate(_has_no_slash))]

#### `training_data.maintainers.github_user`<sub> str</sub>




</details>

### `training_data.tags`<sub> list[str]</sub> ≝ `[]`
Associated tags
[*Example:*](#training_datatags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



### `training_data.version`<sub> _internal.version_type.Version |</sub> ≝ `None`
The version of the resource following SemVer 2.0.


_internal.version_type.Version | None

### `training_data.version_comment`<sub> Optional</sub> ≝ `None`
A comment on the version of the resource.


Optional[str (MaxLen(max_length=512))]

### `training_data.format_version`<sub> Literal[0.3.4]</sub>
The **format** version of this resource specification



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
  (AfterValidator(wo_special_file_name); PrettyPlainSerializer(func=<function _package_serializer at 0x7fa5d178d120>, return_type=PydanticUndefined, when_used='unless-none'))
- _internal.url.HttpUrl
- pydantic.networks.HttpUrl
- None


</details>

#### `training_data.badges.url`<sub> _internal.url.HttpUrl</sub>
target URL
[*Example:*](#training_databadgesurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



</details>

### `training_data.config`<sub> generic.v0_3.Config</sub> ≝ `bioimageio=BioimageioConfig()`
A field for custom configuration that can contain any keys not present in the RDF spec.
This means you should not store, for example, a GitHub repo URL in `config` since there is a `git_repo` field.
Keys in `config` may be very specific to a tool or consumer software. To avoid conflicting definitions,
it is recommended to wrap added configuration into a sub-field named with the specific domain or tool name,
for example:
```yaml
config:
    giraffe_neckometer:  # here is the domain name
        length: 3837283
        address:
            home: zoo
    imagej:              # config specific to ImageJ
        macro_dir: path/to/macro/file
```
If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.
You may want to list linked files additionally under `attachments` to include them when packaging a resource.
(Packaging a resource means downloading/copying important linked files and creating a ZIP archive that contains
an altered rdf.yaml file with local references to the downloaded files.)

<details><summary>generic.v0_3.Config

</summary>


**generic.v0_3.Config:**
#### `training_data.config.bioimageio`<sub> generic.v0_3.BioimageioConfig</sub> ≝ ``
bioimage.io internal metadata.



</details>

### `training_data.type`<sub> Literal[dataset]</sub>




### `training_data.id`<sub> dataset.v0_3.DatasetId | None</sub> ≝ `None`
bioimage.io-wide unique resource identifier
assigned by bioimage.io; version **un**specific.



### `training_data.parent`<sub> dataset.v0_3.DatasetId | None</sub> ≝ `None`
The description from which this one is derived



### `training_data.source`<sub> _internal.url.HttpUrl | None</sub> ≝ `None`
"URL to the source of the dataset.



**dataset.v0_2.DatasetDescr:**
### `training_data.name`<sub> str</sub>
A human-friendly name of the resource description



### `training_data.description`<sub> str</sub>




### `training_data.covers`<sub> list</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff')
[*Example:*](#training_datacovers) ['cover.png']

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), PrettyPlainSerializer(func=<function _package_serializer at 0x7fa5d178d120>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False, allow_any_parent_suffix=False)]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), PrettyPlainSerializer(func=<function _package_serializer at 0x7fa5d178d120>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False, allow_any_parent_suffix=False)]]

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

<details><summary>list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), PrettyPlainSerializer(func=<function _package_serializer at 0x7fa5d178d120>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[typing.Union[bioimageio.spec._internal.url.HttpUrl, bioimageio.spec._internal.io.RelativeFilePath, typing.Annotated[pathlib.Path, PathType(path_type='file'), FieldInfo(annotation=NoneType, required=True, title='FilePath')]], FieldInfo(annotation=NoneType, required=True, title='FileSource', metadata=[_PydanticGeneralMetadata(union_mode='left_to_right')]), AfterValidator(func=<function wo_special_file_name at 0x7fa5dfc10a40>), PrettyPlainSerializer(func=<function _package_serializer at 0x7fa5d178d120>, return_type=PydanticUndefined, when_used='unless-none')]]

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
  (AfterValidator(wo_special_file_name); PrettyPlainSerializer(func=<function _package_serializer at 0x7fa5d178d120>, return_type=PydanticUndefined, when_used='unless-none'))
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

## `version_comment`<sub> Optional</sub> ≝ `None`
A comment on the version of the resource.


Optional[str (MaxLen(max_length=512))]

# Example values
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

### `inputs.preprocessing.kwargs.axis`
channel
### `inputs.preprocessing.kwargs.axes`
('batch', 'x', 'y')
### `inputs.preprocessing.kwargs.axis`
- channel
- index

### `inputs.preprocessing.kwargs.axis`
channel
### `inputs.preprocessing.kwargs.axes`
('batch', 'x', 'y')
### `inputs.preprocessing.kwargs.axis`
channel
### `inputs.preprocessing.kwargs.axes`
('batch', 'x', 'y')
### `outputs.axes.size`
- 10
- {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

### `outputs.axes.size`
- 10
- {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

### `outputs.axes.size`
{'tensor_id': 't', 'axis_id': 'a', 'offset': 5}
### `outputs.axes.size`
- 10
- {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}

### `outputs.axes.id`
- x
- y
- z

### `outputs.axes.size`
{'tensor_id': 't', 'axis_id': 'a', 'offset': 5}
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

### `outputs.postprocessing.kwargs.axis`
channel
### `outputs.postprocessing.kwargs.axes`
('batch', 'x', 'y')
### `outputs.postprocessing.callable`
- my_postprocess_factory
- MyPostprocessClass

### `outputs.postprocessing.kwargs.axis`
- channel
- index

### `outputs.postprocessing.kwargs.axis`
channel
### `outputs.postprocessing.kwargs.axes`
('batch', 'x', 'y')
### `outputs.postprocessing.kwargs.axes`
('batch', 'x', 'y')
### `outputs.postprocessing.kwargs.axis`
channel
### `outputs.postprocessing.kwargs.axes`
('batch', 'x', 'y')
### `weights.keras_hdf5.authors.orcid`
0000-0001-2345-6789
### `weights.keras_hdf5.parent`
pytorch_state_dict
### `weights.keras_v3.authors.orcid`
0000-0001-2345-6789
### `weights.keras_v3.parent`
pytorch_state_dict
### `weights.onnx.authors.orcid`
0000-0001-2345-6789
### `weights.onnx.parent`
pytorch_state_dict
### `weights.pytorch_state_dict.authors.orcid`
0000-0001-2345-6789
### `weights.pytorch_state_dict.parent`
pytorch_state_dict
### `weights.pytorch_state_dict.architecture.callable`
- MyNetworkClass
- get_my_model

### `weights.pytorch_state_dict.architecture.callable`
- MyNetworkClass
- get_my_model

### `weights.tensorflow_js.authors.orcid`
0000-0001-2345-6789
### `weights.tensorflow_js.parent`
pytorch_state_dict
### `weights.tensorflow_saved_model_bundle.authors.orcid`
0000-0001-2345-6789
### `weights.tensorflow_saved_model_bundle.parent`
pytorch_state_dict
### `weights.torchscript.authors.orcid`
0000-0001-2345-6789
### `weights.torchscript.parent`
pytorch_state_dict
### `authors.orcid`
0000-0001-2345-6789
### `covers`
[{'source': 'cover.png'}]
### `git_repo`
https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad
### `license`
- CC0-1.0
- MIT
- BSD-2-Clause

### `links`
('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')
### `maintainers.orcid`
0000-0001-2345-6789
### `packaged_by.orcid`
0000-0001-2345-6789
### `tags`
('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')
### `training_data.covers`
[{'source': 'cover.png'}]
### `training_data.authors.orcid`
0000-0001-2345-6789
### `training_data.license`
- CC0-1.0
- MIT
- BSD-2-Clause

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

