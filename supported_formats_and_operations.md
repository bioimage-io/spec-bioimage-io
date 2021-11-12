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
