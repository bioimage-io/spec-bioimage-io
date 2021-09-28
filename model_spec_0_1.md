
* `cite` _CiteEntry_   is a Dict with the following keys:
  * `text` _String_ 
  * `doi` _optional String_ 
  * `url` _optional String_ 
* `description` _String_ 
* `documentation` _RelativeLocalPath→Path_ 
* `format_version` _String_ 
* `inputs` _List\[InputArray\]_   is a Dict with the following keys:
  * `data_type` _String_ 
  * `name` _String_ 
  * `shape` _Union\[ExplicitShape→List\[Integer\] | ParametrizedInputShape\]_ 
    1. _optional ExplicitShape→List\[Integer\]_ 
    1. _ParametrizedInputShape_   is a Dict with the following keys:
      * `min` _List\[Integer\]_ The minimum input shape with same length as `axes`
      * `step` _List\[Integer\]_ The minimum shape change with same length as `axes`
  * `axes` _optional Axes→String_ 
  * `data_range` _optional Tuple_ 
* `language` _String_ 
* `license` _String_ 
* `name` _String_ 
* `outputs` _List\[OutputArray\]_   is a Dict with the following keys:
  * `data_type` _String_ 
  * `name` _String_ 
  * `shape` _Union\[ExplicitShape→List\[Integer\] | ImplicitOutputShape\]_ 
    1. _optional ExplicitShape→List\[Integer\]_ 
    1. _ImplicitOutputShape_   is a Dict with the following keys:
      * `offset` _List\[Integer\]_ Position of origin wrt to input.
      * `reference_tensor` _String_ Name of the reference input tensor.
      * `scale` _List\[Float\]_ 'output_pix/input_pix' for each dimension.
  * `axes` _optional Axes→String_ 
  * `data_range` _optional Tuple_ 
  * `halo` _optional List\[Integer\]_ 
* `prediction` _Prediction_   is a Dict with the following keys:
  * `dependencies` _optional Dependencies→String_ 
  * `postprocess` _List\[Transformation\]_   is a Dict with the following keys:
    * `spec` _URI→String_ 
    * `kwargs` _optional Dict\[Any, Any\]_ 
  * `preprocess` _List\[Transformation\]_   is a Dict with the following keys:
    * `spec` _URI→String_ 
    * `kwargs` _optional Dict\[Any, Any\]_ 
  * `weights` _Weights_   is a Dict with the following keys:
    * `source` _URI→String_ 
    * `hash` _optional Dict\[Any, Any\]_ 
* `source` _String_ 
* `tags` _List\[String\]_ 
* `authors` _optional List\[String\]_ 
* `config` _optional Dict\[Any, Any\]_ 
* `covers` _optional List\[RelativeLocalPath→Path\]_ 
* `framework` _optional String_ 
* `optional_kwargs` _optional Dict\[String, Any\]_ 
* `required_kwargs` _optional List\[String\]_ 
* `test_input` _optional RelativeLocalPath→Path_ 
* `test_output` _optional RelativeLocalPath→Path_ 
* `training` _optional Dict\[Any, Any\]_ 
