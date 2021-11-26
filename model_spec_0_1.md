
* <a id="cite"></a>`cite` _CiteEntry_   is a Dict with the following keys:
  * <a id="cite:text"></a>`text` _String_ 
  * <a id="cite:doi"></a>`doi` _optional String_ 
  * <a id="cite:url"></a>`url` _optional String_ 
* <a id="description"></a>`description` _String_ 
* <a id="documentation"></a>`documentation` _RelativeLocalPath→Path_ 
* <a id="format_version"></a>`format_version` _String_ 
* <a id="inputs"></a>`inputs` _List\[InputArray\]_   is a Dict with the following keys:
  * <a id="inputs:data_type"></a>`data_type` _String_ 
  * <a id="inputs:name"></a>`name` _String_ 
  * <a id="inputs:shape"></a>`shape` _Union\[ExplicitShape→List\[Integer\] | ParametrizedInputShape\]_ 
    1. _optional ExplicitShape→List\[Integer\]_ 
    1. _ParametrizedInputShape_   is a Dict with the following keys:
    * <a id="inputs:shape:min"></a>`min` _List\[Integer\]_ The minimum input shape with same length as `axes`
    * <a id="inputs:shape:step"></a>`step` _List\[Integer\]_ The minimum shape change with same length as `axes`
  * <a id="inputs:axes"></a>`axes` _optional Axes→String_ 
  * <a id="inputs:data_range"></a>`data_range` _optional Tuple_ 
* <a id="language"></a>`language` _String_ 
* <a id="license"></a>`license` _String_ 
* <a id="name"></a>`name` _String_ 
* <a id="outputs"></a>`outputs` _List\[OutputArray\]_   is a Dict with the following keys:
  * <a id="outputs:data_type"></a>`data_type` _String_ 
  * <a id="outputs:name"></a>`name` _String_ 
  * <a id="outputs:shape"></a>`shape` _Union\[ExplicitShape→List\[Integer\] | ImplicitOutputShape\]_ 
    1. _optional ExplicitShape→List\[Integer\]_ 
    1. _ImplicitOutputShape_   is a Dict with the following keys:
    * <a id="outputs:shape:offset"></a>`offset` _List\[Float\]_ Position of origin wrt to input. Multiple of 0.5.
    * <a id="outputs:shape:reference_tensor"></a>`reference_tensor` _String_ Name of the reference input tensor.
    * <a id="outputs:shape:scale"></a>`scale` _List\[Float\]_ 'output_pix/input_pix' for each dimension.
  * <a id="outputs:axes"></a>`axes` _optional Axes→String_ 
  * <a id="outputs:data_range"></a>`data_range` _optional Tuple_ 
  * <a id="outputs:halo"></a>`halo` _optional List\[Integer\]_ 
* <a id="prediction"></a>`prediction` _Prediction_   is a Dict with the following keys:
  * <a id="prediction:dependencies"></a>`dependencies` _optional Dependencies→String_ 
  * <a id="prediction:postprocess"></a>`postprocess` _List\[Transformation\]_   is a Dict with the following keys:
    * <a id="prediction:postprocess:spec"></a>`spec` _URI→String_ 
    * <a id="prediction:postprocess:kwargs"></a>`kwargs` _optional Dict\[Any, Any\]_ 
  * <a id="prediction:preprocess"></a>`preprocess` _List\[Transformation\]_   is a Dict with the following keys:
    * <a id="prediction:preprocess:spec"></a>`spec` _URI→String_ 
    * <a id="prediction:preprocess:kwargs"></a>`kwargs` _optional Dict\[Any, Any\]_ 
  * <a id="prediction:weights"></a>`weights` _Weights_   is a Dict with the following keys:
    * <a id="prediction:weights:source"></a>`source` _URI→String_ 
    * <a id="prediction:weights:hash"></a>`hash` _optional Dict\[Any, Any\]_ 
* <a id="source"></a>`source` _String_ 
* <a id="tags"></a>`tags` _List\[String\]_ 
* <a id="authors"></a>`authors` _optional List\[String\]_ 
* <a id="config"></a>`config` _optional Dict\[Any, Any\]_ 
* <a id="covers"></a>`covers` _optional List\[RelativeLocalPath→Path\]_ 
* <a id="framework"></a>`framework` _optional String_ 
* <a id="optional_kwargs"></a>`optional_kwargs` _optional Dict\[String, Any\]_ 
* <a id="required_kwargs"></a>`required_kwargs` _optional List\[String\]_ 
* <a id="test_input"></a>`test_input` _optional RelativeLocalPath→Path_ 
* <a id="test_output"></a>`test_output` _optional RelativeLocalPath→Path_ 
* <a id="training"></a>`training` _optional Dict\[Any, Any\]_ 
