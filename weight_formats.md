# Supported weight formats

The supported weight formats and which consumer softwares support them.

| `weight_format` | Description | ilastik | deepImageJ | Fiji |
| --------------- | ----------- | ------- | ---------- | ---- |
| `tensorflow_saved_model_bundle` | A zip file containing `pb` file and `variables` folder  | No | Yes | Yes | 
| `keras_hdf5` |  | No | | |
| `tensorflow_js` | A zip file containing a json file and a binary weights file. | No | |
| `pytorch_state_dict` | A file containg the state dict of a pytorch model | Yes | No | No |
| `pytorch_script` | A torchscrpt file | No | | No |
