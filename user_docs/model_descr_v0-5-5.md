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



## `format_version`<sub> Literal[0.5.5]</sub>
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




#### `inputs.axes.channel_names`<sub> Sequence</sub>



Sequence[_internal.types.Identifier]

**IndexInputAxis:**
#### `inputs.axes.size`<sub> Union</sub>
The size/length of this axis can be specified as
- fixed integer
- parameterized series of valid sizes (`ParameterizedSize`)
- reference to another axis with an optional offset (`SizeReference`)
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
Output axes are concatenable if they have a `SizeReference` to a concatenable
input axis.



**TimeInputAxis:**
#### `inputs.axes.size`<sub> Union</sub>
The size/length of this axis can be specified as
- fixed integer
- parameterized series of valid sizes (`ParameterizedSize`)
- reference to another axis with an optional offset (`SizeReference`)
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
Output axes are concatenable if they have a `SizeReference` to a concatenable
input axis.



**SpaceInputAxis:**
#### `inputs.axes.size`<sub> Union</sub>
The size/length of this axis can be specified as
- fixed integer
- parameterized series of valid sizes (`ParameterizedSize`)
- reference to another axis with an optional offset (`SizeReference`)
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
Output axes are concatenable if they have a `SizeReference` to a concatenable
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
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7f88b5e16ac0>, return_type=PydanticUndefined, when_used='unless-none'))]

**_internal.io.FileDescr:**
#### `inputs.test_tensor.source`<sub> Union</sub>
File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `inputs.test_tensor.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

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
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7f88b5e16ac0>, return_type=PydanticUndefined, when_used='unless-none'))]

**_internal.io.FileDescr:**
#### `inputs.sample_tensor.source`<sub> Union</sub>
File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `inputs.sample_tensor.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

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

#### `inputs.data.range`<sub> Sequence</sub> ≝ `(None, None)`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
`None` corresponds to min/max of what can be expressed by **type**.


Sequence[Optional[float], Optional[float]]

#### `inputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `inputs.data.scale`<sub> float</sub> ≝ `1.0`
Scale for data on an interval (or ratio) scale.



#### `inputs.data.offset`<sub> Optional[float]</sub> ≝ `None`
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

#### `inputs.data.range`<sub> Sequence</sub> ≝ `(None, None)`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
`None` corresponds to min/max of what can be expressed by **type**.


Sequence[Optional[float], Optional[float]]

#### `inputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `inputs.data.scale`<sub> float</sub> ≝ `1.0`
Scale for data on an interval (or ratio) scale.



#### `inputs.data.offset`<sub> Optional[float]</sub> ≝ `None`
Offset for data on a ratio scale.



</details>

### `inputs.optional`<sub> bool</sub> ≝ `False`
indicates that this tensor may be `None`



### `inputs.preprocessing`<sub> Sequence</sub> ≝ `[]`
Description of how this input should be preprocessed.

notes:
- If preprocessing does not start with an 'ensure_dtype' entry, it is added
  to ensure an input tensor's data type matches the input tensor's data description.
- If preprocessing does not end with an 'ensure_dtype' or 'binarize' entry, an
  'ensure_dtype' step is added to ensure preprocessing steps are not unintentionally
  changing the data type.

<details><summary>Sequence[Union[BinarizeDescr, ..., ZeroMeanUnitVarianceDescr]*]

</summary>

Sequence of Union of
- BinarizeDescr
- ClipDescr
- EnsureDtypeDescr
- FixedZeroMeanUnitVarianceDescr
- ScaleLinearDescr
- ScaleRangeDescr
- SigmoidDescr
- SoftmaxDescr
- ZeroMeanUnitVarianceDescr

(Discriminator(discriminator='id', custom_error_type=None, custom_error_message=None, custom_error_context=None))

**BinarizeDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[binarize]</sub>




#### `inputs.preprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[BinarizeKwargs, BinarizeAlongAxisKwargs]

</summary>


**BinarizeKwargs:**
##### `inputs.preprocessing.i.kwargs.threshold`<sub> float</sub>
The fixed threshold



**BinarizeAlongAxisKwargs:**
##### `inputs.preprocessing.i.kwargs.threshold`<sub> Sequence[float]</sub>
The fixed threshold values along `axis`



##### `inputs.preprocessing.i.kwargs.axis`<sub> AxisId</sub>
The `threshold` axis
[*Example:*](#inputspreprocessingikwargsaxis) 'channel'



</details>

**ClipDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[clip]</sub>




#### `inputs.preprocessing.i.kwargs`<sub> model.v0_4.ClipKwargs</sub>


<details><summary>model.v0_4.ClipKwargs

</summary>


**model.v0_4.ClipKwargs:**
##### `inputs.preprocessing.i.kwargs.min`<sub> float</sub>
minimum value for clipping



##### `inputs.preprocessing.i.kwargs.max`<sub> float</sub>
maximum value for clipping



</details>

**EnsureDtypeDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[ensure_dtype]</sub>




#### `inputs.preprocessing.i.kwargs`<sub> EnsureDtypeKwargs</sub>


<details><summary>EnsureDtypeKwargs

</summary>


**EnsureDtypeKwargs:**
##### `inputs.preprocessing.i.kwargs.dtype`<sub> Literal</sub>



Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

</details>

**FixedZeroMeanUnitVarianceDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal</sub>



Literal[fixed_zero_mean_unit_variance]

#### `inputs.preprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[FixedZeroMeanUnitVarianceKwargs, FixedZeroMeanUnitVarianceAlongAxisKwargs]

</summary>


**FixedZeroMeanUnitVarianceKwargs:**
##### `inputs.preprocessing.i.kwargs.mean`<sub> float</sub>
The mean value to normalize with.



##### `inputs.preprocessing.i.kwargs.std`<sub> float</sub>
The standard deviation value to normalize with.



**FixedZeroMeanUnitVarianceAlongAxisKwargs:**
##### `inputs.preprocessing.i.kwargs.mean`<sub> Sequence[float]</sub>
The mean value(s) to normalize with.



##### `inputs.preprocessing.i.kwargs.std`<sub> Sequence[float (Ge(ge=1e-06))]</sub>
The standard deviation value(s) to normalize with.
Size must match `mean` values.



##### `inputs.preprocessing.i.kwargs.axis`<sub> AxisId</sub>
The axis of the mean/std values to normalize each entry along that dimension
separately.
[*Examples:*](#inputspreprocessingikwargsaxis) ['channel', 'index']



</details>

**ScaleLinearDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[scale_linear]</sub>




#### `inputs.preprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[ScaleLinearKwargs, ScaleLinearAlongAxisKwargs]

</summary>


**ScaleLinearKwargs:**
##### `inputs.preprocessing.i.kwargs.gain`<sub> float</sub> ≝ `1.0`
multiplicative factor



##### `inputs.preprocessing.i.kwargs.offset`<sub> float</sub> ≝ `0.0`
additive term



**ScaleLinearAlongAxisKwargs:**
##### `inputs.preprocessing.i.kwargs.axis`<sub> AxisId</sub>
The axis of gain and offset values.
[*Example:*](#inputspreprocessingikwargsaxis) 'channel'



##### `inputs.preprocessing.i.kwargs.gain`<sub> Union</sub> ≝ `1.0`
multiplicative factor


Union[float, Sequence[float] (MinLen(min_length=1))]

##### `inputs.preprocessing.i.kwargs.offset`<sub> Union</sub> ≝ `0.0`
additive term


Union[float, Sequence[float] (MinLen(min_length=1))]

</details>

**ScaleRangeDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[scale_range]</sub>




#### `inputs.preprocessing.i.kwargs`<sub> ScaleRangeKwargs</sub> ≝ `axes=None min_percentile=0.0 max_percentile=100.0 eps=1e-06 reference_tensor=None`


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `inputs.preprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to normalize jointly, i.e. axes to reduce to compute the min/max percentile value.
For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
To normalize samples independently, leave out the "batch" axis.
Default: Scale all axes jointly.
[*Example:*](#inputspreprocessingikwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `inputs.preprocessing.i.kwargs.min_percentile`<sub> float</sub> ≝ `0.0`
The lower percentile used to determine the value to align with zero.



##### `inputs.preprocessing.i.kwargs.max_percentile`<sub> float</sub> ≝ `100.0`
The upper percentile used to determine the value to align with one.
Has to be bigger than `min_percentile`.
The range is 1 to 100 instead of 0 to 100 to avoid mistakenly
accepting percentiles specified in the range 0.0 to 1.0.



##### `inputs.preprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability.
`out = (tensor - v_lower) / (v_upper - v_lower + eps)`;
with `v_lower,v_upper` values at the respective percentiles.



##### `inputs.preprocessing.i.kwargs.reference_tensor`<sub> Optional[TensorId]</sub> ≝ `None`
Tensor ID to compute the percentiles from. Default: The tensor itself.
For any tensor in `inputs` only input tensor references are allowed.



</details>

**SigmoidDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[sigmoid]</sub>




**SoftmaxDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[softmax]</sub>




#### `inputs.preprocessing.i.kwargs`<sub> SoftmaxKwargs</sub> ≝ `axis='channel'`


<details><summary>SoftmaxKwargs

</summary>


**SoftmaxKwargs:**
##### `inputs.preprocessing.i.kwargs.axis`<sub> AxisId</sub> ≝ `channel`
The axis to apply the softmax function along.
Note:
    Defaults to 'channel' axis
    (which may not exist, in which case
    a different axis id has to be specified).
[*Example:*](#inputspreprocessingikwargsaxis) 'channel'



</details>

**ZeroMeanUnitVarianceDescr:**
#### `inputs.preprocessing.i.id`<sub> Literal[zero_mean_unit_variance]</sub>




#### `inputs.preprocessing.i.kwargs`<sub> ZeroMeanUnitVarianceKwargs</sub> ≝ `axes=None eps=1e-06`


<details><summary>ZeroMeanUnitVarianceKwargs

</summary>


**ZeroMeanUnitVarianceKwargs:**
##### `inputs.preprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to normalize jointly, i.e. axes to reduce to compute mean/std.
For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
To normalize each sample independently leave out the 'batch' axis.
Default: Scale all axes jointly.
[*Example:*](#inputspreprocessingikwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `inputs.preprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`
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

<details><summary>Sequence[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BatchAxis, bioimageio.spec.model.v0_5.ChannelAxis, bioimageio.spec.model.v0_5.IndexOutputAxis, typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7f88b5bd87c0>, custom_error_type=None, custom_error_message=None, custom_error_context=None)], typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7f88b5bd87c0>, custom_error_type=None, custom_error_message=None, custom_error_context=None)]], Discriminator(discriminator='type', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

</summary>

Sequence[typing.Annotated[typing.Union[bioimageio.spec.model.v0_5.BatchAxis, bioimageio.spec.model.v0_5.ChannelAxis, bioimageio.spec.model.v0_5.IndexOutputAxis, typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.TimeOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7f88b5bd87c0>, custom_error_type=None, custom_error_message=None, custom_error_context=None)], typing.Annotated[typing.Union[typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxis, Tag(tag='wo_halo')], typing.Annotated[bioimageio.spec.model.v0_5.SpaceOutputAxisWithHalo, Tag(tag='with_halo')]], Discriminator(discriminator=<function _get_halo_axis_discriminator_value at 0x7f88b5bd87c0>, custom_error_type=None, custom_error_message=None, custom_error_context=None)]], Discriminator(discriminator='type', custom_error_type=None, custom_error_message=None, custom_error_context=None)]]

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




#### `outputs.axes.channel_names`<sub> Sequence</sub>



Sequence[_internal.types.Identifier]

**IndexOutputAxis:**
#### `outputs.axes.id`<sub> AxisId</sub> ≝ `index`




#### `outputs.axes.description`<sub> str</sub> ≝ ``
A short description of this axis beyond its type and id.



#### `outputs.axes.type`<sub> Literal[index]</sub>




#### `outputs.axes.size`<sub> Union</sub>
The size/length of this axis can be specified as
- fixed integer
- reference to another axis with an optional offset (`SizeReference`)
- data dependent size using `DataDependentSize` (size is only known after model inference)
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




##### `outputs.axes.size.max`<sub> Optional[int]</sub> ≝ `None`




</details>

**TimeOutputAxis:**
#### `outputs.axes.size`<sub> Union</sub>
The size/length of this axis can be specified as
- fixed integer
- reference to another axis with an optional offset (see `SizeReference`)
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
reference to another axis with an optional offset (see `SizeReference`)
[*Examples:*](#outputsaxessize) [10, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

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
- reference to another axis with an optional offset (see `SizeReference`)
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
reference to another axis with an optional offset (see `SizeReference`)
[*Examples:*](#outputsaxessize) [10, {'tensor_id': 't', 'axis_id': 'a', 'offset': 5}]

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
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7f88b5e16ac0>, return_type=PydanticUndefined, when_used='unless-none'))]

**_internal.io.FileDescr:**
#### `outputs.test_tensor.source`<sub> Union</sub>
File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `outputs.test_tensor.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

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
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7f88b5e16ac0>, return_type=PydanticUndefined, when_used='unless-none'))]

**_internal.io.FileDescr:**
#### `outputs.sample_tensor.source`<sub> Union</sub>
File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `outputs.sample_tensor.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

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

#### `outputs.data.range`<sub> Sequence</sub> ≝ `(None, None)`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
`None` corresponds to min/max of what can be expressed by **type**.


Sequence[Optional[float], Optional[float]]

#### `outputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `outputs.data.scale`<sub> float</sub> ≝ `1.0`
Scale for data on an interval (or ratio) scale.



#### `outputs.data.offset`<sub> Optional[float]</sub> ≝ `None`
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

#### `outputs.data.range`<sub> Sequence</sub> ≝ `(None, None)`
Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor.
`None` corresponds to min/max of what can be expressed by **type**.


Sequence[Optional[float], Optional[float]]

#### `outputs.data.unit`<sub> Union</sub> ≝ `arbitrary unit`



Union[Literal[arbitrary unit], _internal.types.SiUnit]

#### `outputs.data.scale`<sub> float</sub> ≝ `1.0`
Scale for data on an interval (or ratio) scale.



#### `outputs.data.offset`<sub> Optional[float]</sub> ≝ `None`
Offset for data on a ratio scale.



</details>

### `outputs.postprocessing`<sub> Sequence</sub> ≝ `[]`
Description of how this output should be postprocessed.

note: `postprocessing` always ends with an 'ensure_dtype' operation.
      If not given this is added to cast to this tensor's `data.type`.

<details><summary>Sequence[Union[BinarizeDescr, ..., ZeroMeanUnitVarianceDescr]*]

</summary>

Sequence of Union of
- BinarizeDescr
- ClipDescr
- EnsureDtypeDescr
- FixedZeroMeanUnitVarianceDescr
- ScaleLinearDescr
- ScaleMeanVarianceDescr
- ScaleRangeDescr
- SigmoidDescr
- SoftmaxDescr
- ZeroMeanUnitVarianceDescr

(Discriminator(discriminator='id', custom_error_type=None, custom_error_message=None, custom_error_context=None))

**BinarizeDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[binarize]</sub>




#### `outputs.postprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[BinarizeKwargs, BinarizeAlongAxisKwargs]

</summary>


**BinarizeKwargs:**
##### `outputs.postprocessing.i.kwargs.threshold`<sub> float</sub>
The fixed threshold



**BinarizeAlongAxisKwargs:**
##### `outputs.postprocessing.i.kwargs.threshold`<sub> Sequence[float]</sub>
The fixed threshold values along `axis`



##### `outputs.postprocessing.i.kwargs.axis`<sub> AxisId</sub>
The `threshold` axis
[*Example:*](#outputspostprocessingikwargsaxis) 'channel'



</details>

**ClipDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[clip]</sub>




#### `outputs.postprocessing.i.kwargs`<sub> model.v0_4.ClipKwargs</sub>


<details><summary>model.v0_4.ClipKwargs

</summary>


**model.v0_4.ClipKwargs:**
##### `outputs.postprocessing.i.kwargs.min`<sub> float</sub>
minimum value for clipping



##### `outputs.postprocessing.i.kwargs.max`<sub> float</sub>
maximum value for clipping



</details>

**EnsureDtypeDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[ensure_dtype]</sub>




#### `outputs.postprocessing.i.kwargs`<sub> EnsureDtypeKwargs</sub>


<details><summary>EnsureDtypeKwargs

</summary>


**EnsureDtypeKwargs:**
##### `outputs.postprocessing.i.kwargs.dtype`<sub> Literal</sub>



Literal[float32, float64, uint8, int8, uint16, int16, uint32, int32, uint64, int64, bool]

</details>

**FixedZeroMeanUnitVarianceDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal</sub>



Literal[fixed_zero_mean_unit_variance]

#### `outputs.postprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[FixedZeroMeanUnitVarianceKwargs, FixedZeroMeanUnitVarianceAlongAxisKwargs]

</summary>


**FixedZeroMeanUnitVarianceKwargs:**
##### `outputs.postprocessing.i.kwargs.mean`<sub> float</sub>
The mean value to normalize with.



##### `outputs.postprocessing.i.kwargs.std`<sub> float</sub>
The standard deviation value to normalize with.



**FixedZeroMeanUnitVarianceAlongAxisKwargs:**
##### `outputs.postprocessing.i.kwargs.mean`<sub> Sequence[float]</sub>
The mean value(s) to normalize with.



##### `outputs.postprocessing.i.kwargs.std`<sub> Sequence[float (Ge(ge=1e-06))]</sub>
The standard deviation value(s) to normalize with.
Size must match `mean` values.



##### `outputs.postprocessing.i.kwargs.axis`<sub> AxisId</sub>
The axis of the mean/std values to normalize each entry along that dimension
separately.
[*Examples:*](#outputspostprocessingikwargsaxis) ['channel', 'index']



</details>

**ScaleLinearDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[scale_linear]</sub>




#### `outputs.postprocessing.i.kwargs`<sub> Union</sub>


<details><summary>Union[ScaleLinearKwargs, ScaleLinearAlongAxisKwargs]

</summary>


**ScaleLinearKwargs:**
##### `outputs.postprocessing.i.kwargs.gain`<sub> float</sub> ≝ `1.0`
multiplicative factor



##### `outputs.postprocessing.i.kwargs.offset`<sub> float</sub> ≝ `0.0`
additive term



**ScaleLinearAlongAxisKwargs:**
##### `outputs.postprocessing.i.kwargs.axis`<sub> AxisId</sub>
The axis of gain and offset values.
[*Example:*](#outputspostprocessingikwargsaxis) 'channel'



##### `outputs.postprocessing.i.kwargs.gain`<sub> Union</sub> ≝ `1.0`
multiplicative factor


Union[float, Sequence[float] (MinLen(min_length=1))]

##### `outputs.postprocessing.i.kwargs.offset`<sub> Union</sub> ≝ `0.0`
additive term


Union[float, Sequence[float] (MinLen(min_length=1))]

</details>

**ScaleMeanVarianceDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[scale_mean_variance]</sub>




#### `outputs.postprocessing.i.kwargs`<sub> ScaleMeanVarianceKwargs</sub>


<details><summary>ScaleMeanVarianceKwargs

</summary>


**ScaleMeanVarianceKwargs:**
##### `outputs.postprocessing.i.kwargs.reference_tensor`<sub> TensorId</sub>
Name of tensor to match.



##### `outputs.postprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to normalize jointly, i.e. axes to reduce to compute mean/std.
For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
To normalize samples independently, leave out the 'batch' axis.
Default: Scale all axes jointly.
[*Example:*](#outputspostprocessingikwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `outputs.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability:
`out  = (tensor - mean) / (std + eps) * (ref_std + eps) + ref_mean.`



</details>

**ScaleRangeDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[scale_range]</sub>




#### `outputs.postprocessing.i.kwargs`<sub> ScaleRangeKwargs</sub> ≝ `axes=None min_percentile=0.0 max_percentile=100.0 eps=1e-06 reference_tensor=None`


<details><summary>ScaleRangeKwargs

</summary>


**ScaleRangeKwargs:**
##### `outputs.postprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to normalize jointly, i.e. axes to reduce to compute the min/max percentile value.
For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
To normalize samples independently, leave out the "batch" axis.
Default: Scale all axes jointly.
[*Example:*](#outputspostprocessingikwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `outputs.postprocessing.i.kwargs.min_percentile`<sub> float</sub> ≝ `0.0`
The lower percentile used to determine the value to align with zero.



##### `outputs.postprocessing.i.kwargs.max_percentile`<sub> float</sub> ≝ `100.0`
The upper percentile used to determine the value to align with one.
Has to be bigger than `min_percentile`.
The range is 1 to 100 instead of 0 to 100 to avoid mistakenly
accepting percentiles specified in the range 0.0 to 1.0.



##### `outputs.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`
Epsilon for numeric stability.
`out = (tensor - v_lower) / (v_upper - v_lower + eps)`;
with `v_lower,v_upper` values at the respective percentiles.



##### `outputs.postprocessing.i.kwargs.reference_tensor`<sub> Optional[TensorId]</sub> ≝ `None`
Tensor ID to compute the percentiles from. Default: The tensor itself.
For any tensor in `inputs` only input tensor references are allowed.



</details>

**SigmoidDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[sigmoid]</sub>




**SoftmaxDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[softmax]</sub>




#### `outputs.postprocessing.i.kwargs`<sub> SoftmaxKwargs</sub> ≝ `axis='channel'`


<details><summary>SoftmaxKwargs

</summary>


**SoftmaxKwargs:**
##### `outputs.postprocessing.i.kwargs.axis`<sub> AxisId</sub> ≝ `channel`
The axis to apply the softmax function along.
Note:
    Defaults to 'channel' axis
    (which may not exist, in which case
    a different axis id has to be specified).
[*Example:*](#outputspostprocessingikwargsaxis) 'channel'



</details>

**ZeroMeanUnitVarianceDescr:**
#### `outputs.postprocessing.i.id`<sub> Literal[zero_mean_unit_variance]</sub>




#### `outputs.postprocessing.i.kwargs`<sub> ZeroMeanUnitVarianceKwargs</sub> ≝ `axes=None eps=1e-06`


<details><summary>ZeroMeanUnitVarianceKwargs

</summary>


**ZeroMeanUnitVarianceKwargs:**
##### `outputs.postprocessing.i.kwargs.axes`<sub> Optional</sub> ≝ `None`
The subset of axes to normalize jointly, i.e. axes to reduce to compute mean/std.
For example to normalize 'batch', 'x' and 'y' jointly in a tensor ('batch', 'channel', 'y', 'x')
resulting in a tensor of equal shape normalized per channel, specify `axes=('batch', 'x', 'y')`.
To normalize each sample independently leave out the 'batch' axis.
Default: Scale all axes jointly.
[*Example:*](#outputspostprocessingikwargsaxes) ('batch', 'x', 'y')


Optional[Sequence[bioimageio.spec.model.v0_5.AxisId]]

##### `outputs.postprocessing.i.kwargs.eps`<sub> float</sub> ≝ `1e-06`
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
### `weights.keras_hdf5`<sub> Optional[KerasHdf5WeightsDescr]</sub> ≝ `None`


<details><summary>Optional[KerasHdf5WeightsDescr]

</summary>


**KerasHdf5WeightsDescr:**
#### `weights.keras_hdf5.source`<sub> Union</sub>
Source of the weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.keras_hdf5.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

#### `weights.keras_hdf5.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
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

#### `weights.keras_hdf5.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightskeras_hdf5parent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.keras_hdf5.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.keras_hdf5.tensorflow_version`<sub> _internal.version_type.Version</sub>
TensorFlow version used to create these weights.



</details>

### `weights.onnx`<sub> Optional[OnnxWeightsDescr]</sub> ≝ `None`


<details><summary>Optional[OnnxWeightsDescr]

</summary>


**OnnxWeightsDescr:**
#### `weights.onnx.source`<sub> Union</sub>
Source of the weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.onnx.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

#### `weights.onnx.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
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

#### `weights.onnx.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightsonnxparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.onnx.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.onnx.opset_version`<sub> int</sub>
ONNX opset version



</details>

### `weights.pytorch_state_dict`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[PytorchStateDictWeightsDescr]

</summary>


**PytorchStateDictWeightsDescr:**
#### `weights.pytorch_state_dict.source`<sub> Union</sub>
Source of the weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.pytorch_state_dict.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

#### `weights.pytorch_state_dict.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
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

#### `weights.pytorch_state_dict.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightspytorch_state_dictparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.pytorch_state_dict.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.pytorch_state_dict.architecture`<sub> Union</sub>


<details><summary>Union[ArchitectureFromFileDescr, ArchitectureFromLibraryDescr]

</summary>


**ArchitectureFromFileDescr:**
##### `weights.pytorch_state_dict.architecture.source`<sub> Union</sub>
Architecture source file


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

##### `weights.pytorch_state_dict.architecture.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

##### `weights.pytorch_state_dict.architecture.callable`<sub> _internal.types.Identifier</sub>
Identifier of the callable that returns a torch.nn.Module instance.
[*Examples:*](#weightspytorch_state_dictarchitecturecallable) ['MyNetworkClass', 'get_my_model']



##### `weights.pytorch_state_dict.architecture.kwargs`<sub> Dict[str, YamlValue]</sub> ≝ `{}`
key word arguments for the `callable`



**ArchitectureFromLibraryDescr:**
##### `weights.pytorch_state_dict.architecture.callable`<sub> _internal.types.Identifier</sub>
Identifier of the callable that returns a torch.nn.Module instance.
[*Examples:*](#weightspytorch_state_dictarchitecturecallable) ['MyNetworkClass', 'get_my_model']



##### `weights.pytorch_state_dict.architecture.kwargs`<sub> Dict[str, YamlValue]</sub> ≝ `{}`
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
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7f88b5e16ac0>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix=('.yaml', '.yml'), case_sensitive=True); )]

**_internal.io.FileDescr:**
##### `weights.pytorch_state_dict.dependencies.source`<sub> Union</sub>
File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

##### `weights.pytorch_state_dict.dependencies.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

</details>

</details>

### `weights.tensorflow_js`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TensorflowJsWeightsDescr]

</summary>


**TensorflowJsWeightsDescr:**
#### `weights.tensorflow_js.source`<sub> Union</sub>
The multi-file weights.
All required files/folders should be a zip archive.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.tensorflow_js.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

#### `weights.tensorflow_js.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
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

#### `weights.tensorflow_js.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightstensorflow_jsparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.tensorflow_js.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.tensorflow_js.tensorflow_version`<sub> _internal.version_type.Version</sub>
Version of the TensorFlow library used.



</details>

### `weights.tensorflow_saved_model_bundle`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TensorflowSavedModelBundleWeightsDescr]

</summary>


**TensorflowSavedModelBundleWeightsDescr:**
#### `weights.tensorflow_saved_model_bundle.source`<sub> Union</sub>
The multi-file weights.
All required files/folders should be a zip archive.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.tensorflow_saved_model_bundle.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

#### `weights.tensorflow_saved_model_bundle.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
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

#### `weights.tensorflow_saved_model_bundle.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightstensorflow_saved_model_bundleparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

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
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7f88b5e16ac0>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix=('.yaml', '.yml'), case_sensitive=True); )]

**_internal.io.FileDescr:**
##### `weights.tensorflow_saved_model_bundle.dependencies.source`<sub> Union</sub>
File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

##### `weights.tensorflow_saved_model_bundle.dependencies.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

</details>

</details>

### `weights.torchscript`<sub> Optional</sub> ≝ `None`


<details><summary>Optional[TorchscriptWeightsDescr]

</summary>


**TorchscriptWeightsDescr:**
#### `weights.torchscript.source`<sub> Union</sub>
Source of the weights file.


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `weights.torchscript.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

#### `weights.torchscript.authors`<sub> Optional</sub> ≝ `None`
Authors
Either the person(s) that have trained this model resulting in the original weights file.
    (If this is the initial weights entry, i.e. it does not have a `parent`)
Or the person(s) who have converted the weights to this weights format.
    (If this is a child weight, i.e. it has a `parent` field)

<details><summary>Optional[Sequence[generic.v0_3.Author]]

</summary>


**generic.v0_3.Author:**
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

#### `weights.torchscript.parent`<sub> Optional</sub> ≝ `None`
The source weights these weights were converted from.
For example, if a model's weights were converted from the `pytorch_state_dict` format to `torchscript`,
The `pytorch_state_dict` weights entry has no `parent` and is the parent of the `torchscript` weights.
All weight entries except one (the initial set of weights resulting from training the model),
need to have this field.
[*Example:*](#weightstorchscriptparent) 'pytorch_state_dict'


Optional[Literal[keras_hdf5, onnx, pytorch_state_dict, tensorflow_js, tensorflow_saved_model_bundle, torchscript]]

#### `weights.torchscript.comment`<sub> str</sub> ≝ ``
A comment about this weights entry, for example how these weights were created.



#### `weights.torchscript.pytorch_version`<sub> _internal.version_type.Version</sub>
Version of the PyTorch library used.



</details>

</details>

## `attachments`<sub> Sequence</sub> ≝ `[]`
file attachments

<details><summary>Sequence[_internal.io.FileDescr*]

</summary>

Sequence of _internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7f88b5e16ac0>, return_type=PydanticUndefined, when_used='unless-none'))

**_internal.io.FileDescr:**
### `attachments.i.source`<sub> Union</sub>
File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `attachments.i.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

</details>

## `authors`<sub> Sequence[generic.v0_3.Author]</sub> ≝ `[]`
The authors are the creators of the model RDF and the primary points of contact.

<details><summary>Sequence[generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
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

## `cite`<sub> Sequence[generic.v0_3.CiteEntry]</sub> ≝ `[]`
citations

<details><summary>Sequence[generic.v0_3.CiteEntry]

</summary>


**generic.v0_3.CiteEntry:**
### `cite.i.text`<sub> str</sub>
free text description



### `cite.i.doi`<sub> Optional[_internal.types.Doi]</sub> ≝ `None`
A digital object identifier (DOI) is the prefered citation reference.
See https://www.doi.org/ for details.
Note:
    Either **doi** or **url** have to be specified.



### `cite.i.url`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`
URL to cite (preferably specify a **doi** instead/also).
Note:
    Either **doi** or **url** have to be specified.



</details>

## `config`<sub> Config</sub> ≝ `bioimageio=BioimageioConfig(reproducibility_tolerance=())`


<details><summary>Config

</summary>


**Config:**
### `config.bioimageio`<sub> BioimageioConfig</sub> ≝ `reproducibility_tolerance=()`


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



##### `config.bioimageio.reproducibility_tolerance.absolute_tolerance`<sub> float</sub> ≝ `0.0001`
Maximum absolute tolerance of reproduced test tensor.



##### `config.bioimageio.reproducibility_tolerance.mismatched_elements_per_million`<sub> int</sub> ≝ `100`
Maximum number of mismatched elements/pixels per million to tolerate.



##### `config.bioimageio.reproducibility_tolerance.output_ids`<sub> Sequence</sub> ≝ `()`
Limits the output tensor IDs these reproducibility details apply to.


Sequence[bioimageio.spec.model.v0_5.TensorId]

##### `config.bioimageio.reproducibility_tolerance.weights_formats`<sub> Sequence</sub> ≝ `()`
Limits the weights formats these details apply to.

<details><summary>Sequence[typing.Literal['keras_hdf5', 'onnx', 'pytorch_state_dict', 'tensorflow_js', 'tensorflow_saved_model_bundle', 'torchscript']]

</summary>

Sequence[typing.Literal['keras_hdf5', 'onnx', 'pytorch_state_dict', 'tensorflow_js', 'tensorflow_saved_model_bundle', 'torchscript']]

</details>

</details>

</details>

</details>

## `covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1 or 1:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')
[*Example:*](#covers) ['cover.png']

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package_serializer at 0x7f88b5e16b60>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False))

</details>

## `description`<sub> str</sub> ≝ ``
A string containing a brief description.



## `documentation`<sub> Optional</sub> ≝ `None`
URL or relative path to a markdown file with additional documentation.
The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
The documentation should include a '#[#] Validation' (sub)section
with details on how to quantitatively validate the model on unseen data.

<details><summary>Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package_serializer at 0x7f88b5e16b60>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix='.md', case_sensitive=True); )]

</details>

## `git_repo`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`
A URL to the Git repository where the resource is being developed.
[*Example:*](#git_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



## `icon`<sub> Union</sub> ≝ `None`
An icon for illustration, e.g. on bioimage.io

<details><summary>Union[str*, Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
  (union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package_serializer at 0x7f88b5e16b60>, return_type=PydanticUndefined, when_used='unless-none'))
- None


</details>

## `id`<sub> Optional[ModelId]</sub> ≝ `None`
bioimage.io-wide unique resource identifier
assigned by bioimage.io; version **un**specific.



## `id_emoji`<sub> Optional</sub> ≝ `None`
UTF-8 emoji for display alongside the `id`.


Optional[str (Len(min_length=1, max_length=2); )]

## `license`<sub> Union</sub> ≝ `None`
A [SPDX license identifier](https://spdx.org/licenses/).
We do not support custom license beyond the SPDX license list, if you need that please
[open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
to discuss your intentions with the community.
[*Examples:*](#license) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId, None]

## `links`<sub> Sequence[str]</sub> ≝ `[]`
IDs of other bioimage.io resources
[*Example:*](#links) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



## `maintainers`<sub> Sequence</sub> ≝ `[]`
Maintainers of this resource.
If not specified, `authors` are maintainers and at least some of them has to specify their `github_user` name

<details><summary>Sequence[generic.v0_3.Maintainer]

</summary>


**generic.v0_3.Maintainer:**
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



Optional[str (Predicate(_has_no_slash))]

### `maintainers.i.github_user`<sub> str</sub>




</details>

## `packaged_by`<sub> Sequence[generic.v0_3.Author]</sub> ≝ `[]`
The persons that have packaged and uploaded this model.
Only required if those persons differ from the `authors`.

<details><summary>Sequence[generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
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
### `parent.version`<sub> Optional</sub> ≝ `None`
The version of the linked resource following SemVer 2.0.


Optional[_internal.version_type.Version]

### `parent.id`<sub> ModelId</sub>
A valid model `id` from the bioimage.io collection.



</details>

## `run_mode`<sub> Optional[model.v0_4.RunMode]</sub> ≝ `None`
Custom run mode for this model: for more complex prediction procedures like test time
data augmentation that currently cannot be expressed in the specification.
No standard run modes are defined yet.

<details><summary>Optional[model.v0_4.RunMode]

</summary>


**model.v0_4.RunMode:**
### `run_mode.name`<sub> Union[Literal[deepimagej], str]</sub>
Run mode name



### `run_mode.kwargs`<sub> Dict[str, Any]</sub> ≝ `{}`
Run mode specific key word arguments



</details>

## `tags`<sub> Sequence[str]</sub> ≝ `[]`
Associated tags
[*Example:*](#tags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



## `timestamp`<sub> _internal.types.Datetime</sub> ≝ `root=datetime.datetime(2025, 8, 12, 13, 25, 14, 177909, tzinfo=datetime.timezone.utc)`
Timestamp in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format
with a few restrictions listed [here](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat).
(In Python a datetime object is valid, too).



## `training_data`<sub> Union</sub> ≝ `None`
The dataset used to train this model

<details><summary>Union[None, dataset.v0_3.LinkedDataset, dataset.v0_3.DatasetDescr, dataset.v0_2.DatasetDescr]

</summary>


**dataset.v0_3.LinkedDataset:**
### `training_data.version`<sub> Optional</sub> ≝ `None`
The version of the linked resource following SemVer 2.0.


Optional[_internal.version_type.Version]

### `training_data.id`<sub> dataset.v0_3.DatasetId</sub>
A valid dataset `id` from the bioimage.io collection.



**dataset.v0_3.DatasetDescr:**
### `training_data.name`<sub> str</sub>
A human-friendly name of the resource description.
May only contains letters, digits, underscore, minus, parentheses and spaces.



### `training_data.description`<sub> str</sub> ≝ ``
A string containing a brief description.



### `training_data.covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1 or 1:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')
[*Example:*](#training_datacovers) ['cover.png']

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package_serializer at 0x7f88b5e16b60>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False))

</details>

### `training_data.id_emoji`<sub> Optional</sub> ≝ `None`
UTF-8 emoji for display alongside the `id`.


Optional[str (Len(min_length=1, max_length=2); )]

### `training_data.authors`<sub> Sequence[generic.v0_3.Author]</sub> ≝ `[]`
The authors are the creators of this resource description and the primary points of contact.

<details><summary>Sequence[generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
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

### `training_data.attachments`<sub> Sequence</sub> ≝ `[]`
file attachments

<details><summary>Sequence[_internal.io.FileDescr*]

</summary>

Sequence of _internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7f88b5e16ac0>, return_type=PydanticUndefined, when_used='unless-none'))

**_internal.io.FileDescr:**
#### `training_data.attachments.i.source`<sub> Union</sub>
File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

#### `training_data.attachments.i.sha256`<sub> Optional</sub> ≝ `None`
SHA256 hash value of the **source** file.


Optional[_internal.io_basics.Sha256]

</details>

### `training_data.cite`<sub> Sequence[generic.v0_3.CiteEntry]</sub> ≝ `[]`
citations

<details><summary>Sequence[generic.v0_3.CiteEntry]

</summary>


**generic.v0_3.CiteEntry:**
#### `training_data.cite.i.text`<sub> str</sub>
free text description



#### `training_data.cite.i.doi`<sub> Optional[_internal.types.Doi]</sub> ≝ `None`
A digital object identifier (DOI) is the prefered citation reference.
See https://www.doi.org/ for details.
Note:
    Either **doi** or **url** have to be specified.



#### `training_data.cite.i.url`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`
URL to cite (preferably specify a **doi** instead/also).
Note:
    Either **doi** or **url** have to be specified.



</details>

### `training_data.license`<sub> Union</sub> ≝ `None`
A [SPDX license identifier](https://spdx.org/licenses/).
We do not support custom license beyond the SPDX license list, if you need that please
[open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
to discuss your intentions with the community.
[*Examples:*](#training_datalicense) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId, None]

### `training_data.git_repo`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`
A URL to the Git repository where the resource is being developed.
[*Example:*](#training_datagit_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



### `training_data.icon`<sub> Union</sub> ≝ `None`
An icon for illustration, e.g. on bioimage.io

<details><summary>Union[str*, Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
  (union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package_serializer at 0x7f88b5e16b60>, return_type=PydanticUndefined, when_used='unless-none'))
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
If not specified, `authors` are maintainers and at least some of them has to specify their `github_user` name

<details><summary>Sequence[generic.v0_3.Maintainer]

</summary>


**generic.v0_3.Maintainer:**
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



Optional[str (Predicate(_has_no_slash))]

#### `training_data.maintainers.i.github_user`<sub> str</sub>




</details>

### `training_data.tags`<sub> Sequence[str]</sub> ≝ `[]`
Associated tags
[*Example:*](#training_datatags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



### `training_data.version`<sub> Optional</sub> ≝ `None`
The version of the resource following SemVer 2.0.


Optional[_internal.version_type.Version]

### `training_data.version_comment`<sub> Optional</sub> ≝ `None`
A comment on the version of the resource.


Optional[str (MaxLen(max_length=512))]

### `training_data.format_version`<sub> Literal[0.3.0]</sub>
The **format** version of this resource specification



### `training_data.documentation`<sub> Optional</sub> ≝ `None`
URL or relative path to a markdown file encoded in UTF-8 with additional documentation.
The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.

<details><summary>Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Optional[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package_serializer at 0x7f88b5e16b60>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix='.md', case_sensitive=True); )]

</details>

### `training_data.badges`<sub> Sequence</sub> ≝ `[]`
badges associated with this resource

<details><summary>Sequence[generic.v0_2.BadgeDescr]

</summary>


**generic.v0_2.BadgeDescr:**
#### `training_data.badges.i.label`<sub> str</sub>
badge label to display on hover
[*Example:*](#training_databadgesilabel) 'Open in Colab'



#### `training_data.badges.i.icon`<sub> Union</sub> ≝ `None`
badge icon (included in bioimage.io package if not a URL)
[*Example:*](#training_databadgesiicon) 'https://colab.research.google.com/assets/colab-badge.svg'

<details><summary>Union[Union[Path*, _internal.io.RelativeFilePath]*, _internal.url.HttpUrl, pydantic.networks.HttpUrl, None]

</summary>

Union of
- Union[Path (PathType(path_type='file'); ), _internal.io.RelativeFilePath]
  (AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package_serializer at 0x7f88b5e16b60>, return_type=PydanticUndefined, when_used='unless-none'))
- _internal.url.HttpUrl
- pydantic.networks.HttpUrl
- None


</details>

#### `training_data.badges.i.url`<sub> _internal.url.HttpUrl</sub>
target URL
[*Example:*](#training_databadgesiurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



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




### `training_data.id`<sub> Optional[dataset.v0_3.DatasetId]</sub> ≝ `None`
bioimage.io-wide unique resource identifier
assigned by bioimage.io; version **un**specific.



### `training_data.parent`<sub> Optional[dataset.v0_3.DatasetId]</sub> ≝ `None`
The description from which this one is derived



### `training_data.source`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`
"URL to the source of the dataset.



**dataset.v0_2.DatasetDescr:**
### `training_data.name`<sub> str</sub>
A human-friendly name of the resource description



### `training_data.description`<sub> str</sub>




### `training_data.covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff')
[*Example:*](#training_datacovers) ['cover.png']

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package_serializer at 0x7f88b5e16b60>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False))

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
File attachments

<details><summary>Sequence[Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*]

</summary>

Sequence of Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package_serializer at 0x7f88b5e16b60>, return_type=PydanticUndefined, when_used='unless-none'))

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
  (union_mode='left_to_right')
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



### `training_data.format_version`<sub> Literal[0.2.4]</sub>
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
badge icon (included in bioimage.io package if not a URL)
[*Example:*](#training_databadgesiicon) 'https://colab.research.google.com/assets/colab-badge.svg'

<details><summary>Union[Union[Path*, _internal.io.RelativeFilePath]*, _internal.url.HttpUrl, pydantic.networks.HttpUrl, None]

</summary>

Union of
- Union[Path (PathType(path_type='file'); ), _internal.io.RelativeFilePath]
  (AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package_serializer at 0x7f88b5e16b60>, return_type=PydanticUndefined, when_used='unless-none'))
- _internal.url.HttpUrl
- pydantic.networks.HttpUrl
- None


</details>

#### `training_data.badges.i.url`<sub> _internal.url.HttpUrl</sub>
target URL
[*Example:*](#training_databadgesiurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



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

### `training_data.license`<sub> Union</sub> ≝ `None`
A [SPDX license identifier](https://spdx.org/licenses/).
We do not support custom license beyond the SPDX license list, if you need that please
[open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose
) to discuss your intentions with the community.
[*Examples:*](#training_datalicense) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId, str, None]

### `training_data.type`<sub> Literal[dataset]</sub>




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

### `inputs.preprocessing.i.kwargs.axis`
channel
### `inputs.preprocessing.i.kwargs.axis`
- channel
- index

### `inputs.preprocessing.i.kwargs.axis`
channel
### `inputs.preprocessing.i.kwargs.axes`
('batch', 'x', 'y')
### `inputs.preprocessing.i.kwargs.axis`
channel
### `inputs.preprocessing.i.kwargs.axes`
('batch', 'x', 'y')
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
- channel
- index

### `outputs.postprocessing.i.kwargs.axis`
channel
### `outputs.postprocessing.i.kwargs.axes`
('batch', 'x', 'y')
### `outputs.postprocessing.i.kwargs.axes`
('batch', 'x', 'y')
### `outputs.postprocessing.i.kwargs.axis`
channel
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

### `weights.tensorflow_js.authors.i.orcid`
0000-0001-2345-6789
### `weights.tensorflow_js.parent`
pytorch_state_dict
### `weights.tensorflow_saved_model_bundle.authors.i.orcid`
0000-0001-2345-6789
### `weights.tensorflow_saved_model_bundle.parent`
pytorch_state_dict
### `weights.torchscript.authors.i.orcid`
0000-0001-2345-6789
### `weights.torchscript.parent`
pytorch_state_dict
### `authors.i.orcid`
0000-0001-2345-6789
### `covers`
['cover.png']
### `git_repo`
https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad
### `license`
- CC0-1.0
- MIT
- BSD-2-Clause

### `links`
('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')
### `maintainers.i.orcid`
0000-0001-2345-6789
### `packaged_by.i.orcid`
0000-0001-2345-6789
### `tags`
('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')
### `training_data.covers`
['cover.png']
### `training_data.authors.i.orcid`
0000-0001-2345-6789
### `training_data.license`
- CC0-1.0
- MIT
- BSD-2-Clause

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
### `training_data.covers`
['cover.png']
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

