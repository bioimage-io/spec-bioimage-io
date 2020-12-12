# Weight Formats

The supported weight formats and their additional fields:

- `keras_hdf5`: A hdf5 file containing weights for Keras.
- `pytorch_script`: A torchscript file.
- `pytorch_state_dict`: A file containg the state dict of a pytorch model.
- `tensorflow_js`: A text JSON file named model.json, which carries the topology and reference to the weights files, used by tensorflow.js.
- `tensorflow_saved_model_bundle`: A zip file containing a `pb` file and `variables` folder. Additional fields are
  - `tag`
  - `tensorflow_version`

## Consumers

Which consumer software supports which format?

| `weight_format`       | ilastik | deepImageJ | Fiji |
| --------------------- | ------- | ---------- | ---- |
|  `keras_hdf5`         | No      | No         | ?    | 
|  `pytorch_script`     | No      | Yes        | No   |
|  `pytorch_state_dict` | Yes     | No         | No   |
|  `tensorflow_js`      | No      | Yes        | No   |
|  `tensorflow_saved_model_bundle` | No | Yes | Yes |


# Preprocessing

The supported preprocessing operations.

- `clip` clip the tensor
  - `kwargs`
    - `min` minimum value for clipping
    - `max` maximum value for clipping
  - `reference_implementation`
- `min_max` normalize the tensor to range 0, 1
  - `kwargs`
    - `axes` the subset of axes to normalize jointly. For example `xy` to normalize the two image axes for 2d data jointly. The batch axis (`b`) is not valid here.
  - `reference_implementation`
- `percentile` normalize the tensor with percentile normalization
  - `kwargs`
    - `mode` can be one of `per_sample` (percentiles are computed for each sample individually), `per_dataset` (percentiles are computed for the entire dataset)
    - `axes` the subset of axes to normalize jointly. For example `xy` to normalize the two image axes for 2d data jointly. The batch axis (`b`) is not valid here.
    - `min_percentile` the lower percentile used for normalization, in range 0 to 100.
    - `max_percentile` the upper percentile used for normalization, in range 0 to 100. Has to be bigger than `upper_percentile`.
  - `reference_implementaion`
- `scale_linear` scale the tensor with a fixed multiplicative and additive factor
  - `kwargs`
    - `gain` multiplicative factor
    - `offset` additive factor
    - `axes` the subset of axes to scale jointly. For example `xy` to scale the two image axes for 2d data jointly. The batch axis (`b`) is not valid here.
  - `reference_implementation`
- `zero_mean_unit_variance` normalize the tensor to have zero mean and unit variance
  - `kwargs`
    - `mode` can be one of `fixed` (fixed values for mean and variance), `per_sample` (mean and variance are computed for each sample individually), `per_dataset` (mean and variance are computed for the entire dataset)
    - `axes` the subset of axes to normalize jointly. For example `xy` to normalize the two image axes for 2d data jointly. The batch axis (`b`) is not valid here.
    - `mean` the mean value(s) to use for `mode == fixed`. For example `[1.1, 2.2, 3.3]` in the case of a 3 channel image where the channels are not normalized jointly.
    - `std` the standard deviation values to use for `mode == fixed`. Analogous to `mean`.
    - `[eps]` epsilon for numeric stability: `out = (tensor - mean) / (std + eps)`.
  - `reference_implementation`

## Consumers

Which consumer supports which preprocessing operation?

| preprocesing               | ilastik | deepImageJ | Fiji |
| -------------------------- | ------- | ---------- | ---- |
|  `clip`                    | ?       | ?          | ?    | 
|  `min_max`                 | ?       | ?          | ?    |
|  `percentile`              | ?       | ?          | ?    |
| `scale_linear`             | ?       | ?          | ?    |
|  `zero_mean_unit_variance` | yes     | ?          | ?    |


# Postprocessing

The supported postprocessing operations.

- `binarize` binarize the tensor with a fixed threshold, values above the threshold will be set to one, values below the threshold to zero
  - `kwargs`
    - `threshold` the fixed threshold
  - `reference_implemation`
- `clip` clip the tensor, same as in [preprocessing](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#preprocessing).
- `sigmoid` apply a sigmoid to the tensor.
  - `kwargs` None
  - `reference_implementation`
- `scale_mean_variance` scale the tensor s.t. its mean and variance match a reference input 
  - `kwargs`
    - `mode` one of `per_dataset` or `per_sample` (for fixed mean and variance use `scale_linear`)
    - `reference_input` name of the input tensor to use as reference
  - `reference_implementation`
- `scale_min_max` scale the tensor s.t. its min and max match a reference tensor
  - `kwargs`
    - `mode` can be one of `fixed`, `per_sample` or `per_dataset`
    - `min_percentile` (if `mode != fixed`) the percentile used to compute the reference min value (default: 0)
    - `max_percentile` (if `mode != fixed`) the percentile used to compute the reference max value (default: 100)
    - `min` (if `mode == fixed`) the fixed min value
    - `max` (if `mode == fixed`) the fixed max value
    - `reference_input` name of the input tensor to use as reference
  - `reference_implementation`
- `scale_linear` scale the tensor with a fixed multiplicative and additive factor, sae as in [preprocessing](https://github.com/bioimage-io/configuration/blob/master/supported_formats_and_operations.md#preprocessing).

## Consumers

Which consumer supports which postprocessing operation?

| preprocesing          | ilastik | deepImageJ | Fiji |
| --------------------- | ------- | ---------- | ---- |
|  `clip`               | no      | ?          | yes  |
|  `binarize`           | no      | ?          | ?    |
|  `sigmoid`            | yes     | ?          | ?    | 
|  `scale_mean_variance`| no      | ?          | yes  |
|  `scale_min_max`      | no      | ?          | yes  |
|  `scale_linear`       | no      | ?          | ?    |


# Run Modes

Custom run modes to enable more complex prediction procedures.


## Consumers
