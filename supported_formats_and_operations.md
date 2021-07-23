# Weight Formats

The supported weight formats are listed below. In addition to `source` and `sha256` which will be required for all formats, some format may contain additional fields.

- `keras_hdf5`: A hdf5 file containing weights for Keras.
- `pytorch_script`: A torchscript file.
- `pytorch_state_dict`: A file containg the state dict of a pytorch model.
- `tensorflow_js`: A text JSON file named model.json, which carries the topology and reference to the weights files, used by tensorflow.js.
- `tensorflow_saved_model_bundle`: A zip file containing a `pb` file and `variables` folder. Additional fields are
  - `tag`
  - `tensorflow_version`
- `onnx`: A Open Neural Network Exchange file
  - `opset_version`

## Consumers

Which consumer software supports which format?

| `weight_format`       | ilastik | deepImageJ | Fiji |
| --------------------- | ------- | ---------- | ---- |
|  `keras_hdf5`         | No      | No         | ?    | 
|  `pytorch_script`     | No      | Yes        | No   |
|  `pytorch_state_dict` | Yes     | No         | No   |
|  `tensorflow_js`      | No      | Yes        | No   |
|  `tensorflow_saved_model_bundle` | No | Yes | Yes |
|  `onnx` | ? | ? | ? |


# Pre- and postprocessing

The supported operations that are valid in pre- or postprocessing. IMPORTANT: these operations should always return float32 tensors, so that their output can be consumed by the models.

- `binarize` binarize the tensor with a fixed threshold, values above the threshold will be set to one, values below the threshold to zero
  - `kwargs`
    - `threshold` the fixed threshold
  - `reference_implemation`
- `clip` clip the tensor
  - `kwargs`
    - `min` minimum value for clipping
    - `max` maximum value for clipping
  - `reference_implementation`
- `scale_linear` scale the tensor with a fixed multiplicative and additive factor
  - `kwargs`
    - `gain` multiplicative factor
    - `offset` additive factor
    - `axes` the subset of axes to scale jointly. For example `xy` to scale the two image axes for 2d data jointly. The batch axis (`b`) is not valid here.
  - `reference_implementation`
- `sigmoid` apply a sigmoid to the tensor.
  - `kwargs` None
  - `reference_implementation`
- `zero_mean_unit_variance` normalize the tensor to have zero mean and unit variance
  - `kwargs`
    - `mode` can be one of `fixed` (fixed values for mean and variance), `per_sample` (mean and variance are computed for each sample individually), `per_dataset` (mean and variance are computed for the entire dataset)
    - `axes` the subset of axes to normalize jointly. For example `xy` to normalize the two image axes for 2d data jointly. The batch axis (`b`) is not valid here.
    - `mean` the mean value(s) to use for `mode == fixed`. For example `[1.1, 2.2, 3.3]` in the case of a 3 channel image where the channels are not normalized jointly.
    - `std` the standard deviation values to use for `mode == fixed`. Analogous to `mean`.
    - `[eps]` epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`. Default value: 10^-7.
  - `reference_implementation`
  
## Consumers

Which consumer supports which pre-/postprocessing operation?

| pre-/postprocesing         | ilastik | deepImageJ | Fiji |
| -------------------------- | ------- | ---------- | ---- |
|  `binarize`                | no      | ?          | ?    |
|  `clip`                    | ?       | ?          | ?    | 
|  `scale_linear`            | ?       | ?          | ?    |
|  `sigmoid`                 | yes     | ?          | ?    |
|  `zero_mean_unit_variance` | yes     | ?          | ?    |


## Preprocessing

Additional preprocessing operations. IMPORTANT: these operations should always return float32 tensors, so that their output can be consumed by the models.

- `scale_range` normalize the tensor with percentile normalization
  - `kwargs`
    - `mode` can be one of `per_sample` (percentiles are computed for each sample individually), `per_dataset` (percentiles are computed for the entire dataset). For a fixed scaling use `scale linear`.
    - `axes` the subset of axes to normalize jointly. For example `xy` to normalize the two image axes for 2d data jointly. The batch axis (`b`) is not valid here.
    - `min_percentile` the lower percentile used for normalization, in range 0 to 100. Default value: 0.
    - `max_percentile` the upper percentile used for normalization, in range 1 to 100. Has to be bigger than `min_percentile`. Default value: 100. The range is 1 to 100 instead of 0 to 100 to avoid mistakenly accepting percentiles specified in the range 0.0 to 1.0
  - `reference_implementaion`


### Consumers

Which consumer supports which preprocessing operation?

| preprocesing               | ilastik | deepImageJ | Fiji |
| -------------------------- | ------- | ---------- | ---- |
|  `scale_range`             | ?       | ?          | ?    |


## Postprocessing

Additional postprocessing operations.

- `scale_range` normalize the tensor with percentile normalization
  - `kwargs`
    - same as preprocessing
    - `reference_tensor` tensor name to compute the percentiles from. Default: The tensor itself. If `mode`==`per_dataset` this needs to be the name of an input tensor.
  - `reference_implementation`
- `scale_mean_variance` scale the tensor s.t. its mean and variance match a reference tensor 
  - `kwargs`
    - `mode` one of `per_dataset` or `per_sample` (for fixed mean and variance use `scale_linear`)
    - `reference_tensor` name of tensor to match
  - `reference_implementation`


### Consumers

Which consumer supports which postprocessing operation?

| postprocesing          | ilastik | deepImageJ | Fiji |
| --------------------- | ------- | ---------- | ---- |
| `scale_mean_variance` | ?       | ?          | ?    |
| `scale_range`         | ?       | ?          | ?    |


# Run Modes

Custom run modes to enable more complex prediction procedures.


## Consumers
