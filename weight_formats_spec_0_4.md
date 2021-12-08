# Weight formats in model spec 0.4
## Common \[optional\] key word arguments for all weight formats

- `source` URI or path to the weights file. Preferably a url.
- `[attachments]` Dictionary of text keys and list values (that may contain any valid yaml) to additional, relevant files that are specific to the current weight format. A list of URIs can be listed under the `files` key to included additional files for generating the model package.
- `[authors]` A list of authors. If this is the root weight (it does not have a `parent` field): the person(s) that have trained this model. If this is a child weight (it has a `parent` field): the person(s) who have converted the weights to this format.
- `[parent]` The source weights used as input for converting the weights to this format. For example, if the weights were converted from the format `pytorch_state_dict` to `pytorch_script`, the parent is `pytorch_state_dict`. All weight entries except one (the initial set of weights resulting from training the model), need to have this field.
- `[sha256]` SHA256 checksum of the source file specified. You can drag and drop your file to this [online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate it in your browser. Or you can generate the SHA256 code for your model and weights by using for example, `hashlib` in Python. 
    Code snippet to compute SHA256 checksum
    
    ```python
    import hashlib
    
    filename = "your filename here"
    with open(filename, "rb") as f:
      bytes = f.read() # read entire file as bytes
      readable_hash = hashlib.sha256(bytes).hexdigest()
      print(readable_hash)
      ```



## Weight formats and their additional \[optional\] key word arguments
- `keras_hdf5` Keras HDF5 weights format
  - key word arguments:
    - `[tensorflow_version]` 
- `onnx` ONNX weights format
  - key word arguments:
    - `[opset_version]` 
- `pytorch_state_dict` PyTorch state dictionary weights format
  - key word arguments:
    - `[architecture]` Source code of the model architecture that either points to a local implementation: `<relative path to file>:<identifier of implementation within the file>` or the implementation in an available dependency: `<root-dependency>.<sub-dependency>.<identifier>`.
For example: `my_function.py:MyImplementation` or `bioimageio.core.some_module.some_class_or_function`.
    - `[architecture_sha256]` SHA256 checksum of the model source code file.You can drag and drop your file to this [online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate it in your browser. Or you can generate the SHA256 code for your model and weights by using for example, `hashlib` in Python. 
    Code snippet to compute SHA256 checksum
    
    ```python
    import hashlib
    
    filename = "your filename here"
    with open(filename, "rb") as f:
      bytes = f.read() # read entire file as bytes
      readable_hash = hashlib.sha256(bytes).hexdigest()
      print(readable_hash)
      ```

 This field is only required if the architecture points to a source file.
    - `[kwargs]` Keyword arguments for the implementation specified by `architecture`.
- `tensorflow_js` Tensorflow Javascript weights format
  - key word arguments:
    - `[tensorflow_version]` 
- `tensorflow_saved_model_bundle` Tensorflow Saved Model Bundle weights format
  - key word arguments:
    - `[tensorflow_version]` 
- `torchscript` Torchscript weights format
