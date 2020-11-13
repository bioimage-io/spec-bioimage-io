# Weight Formats

The supported weight formats:

- `keras_hdf5`: 
- `pytorch_script`: A torchscript file.
- `pytorch_state_dict`: A file containg the state dict of a pytorch model.
- `tensorflow_js`: A zip file containing a json file and a binary weights file.
- `tensorflow_saved_model_bundle`: A zip file containing a `pb` file and `variables` folder.

## Consumers

Which consumer software supports which format?

| `weight_format`       | ilastik | deepImageJ | Fiji |
| --------------------- | ------- | ---------- | ---- |
|  `keras_hdf5`         | No      | ?          | ?    | 
|  `pytorch_script`     | No      | ?          | No   |
|  `pytorch_state_dict` | Yes     | No         | No   |
|  `tensorflow_js`      | No      | Yes        | No   |
|  `tensorflow_saved_model_bundle` | No | Yes | Yes |


# Preprocessing

The supported preprocessing operations.

- `zero_mean_unit_variance`
  - `kwargs`
    - `mode`
  - `reference_implementation`

## Consumers

Which consumer supports which preprocessing operation?

TODO


# Postprocessing

The supported postprocessing operations.

- `sigmoid`

## Consumers

Which consumer supports which postprocessing operation?

TODO
