# Custom Ops Library

Pre-built postprocessing and preprocessing factory functions for the BioImage Model Zoo.

## How to use a built-in op

In your `rdf.yaml`, set `id: custom` and name the op in `callable` — no `source` needed:

```yaml
postprocessing:
  - id: custom
    callable: cellpose_flow_dynamics
    kwargs:
      cellprob_threshold: 0.0
      flow_threshold: 0.4
```

`bioimageio.core` will look up `callable` in this folder automatically.

## How to write your own op

1. Write a Python file with a single factory function:

```python
# my_op.py
import numpy as np

def my_op(threshold=0.5):
    """
    Factory function — called once with kwargs.
    Returns the function that processes tensors.
    """
    def run(*arrays):
        # arrays = model output tensors in rdf.yaml declaration order
        # each is a numpy.ndarray
        return (arrays[0] > threshold).astype(np.uint8)
    return run
```

2. Point to it from `rdf.yaml`:

```yaml
postprocessing:
  - id: custom
    callable: my_op
    source: my_op.py
    sha256: <sha256 of my_op.py>
    kwargs:
      threshold: 0.5
```

3. To share it as a built-in: open a PR adding your file to this folder.

## Rules for contributed ops

- One file per op, filename = callable name (e.g. `cellpose_flow_dynamics.py`)
- Only import from: `numpy`, `scipy`, `scikit-image`, `torch`, `tensorflow`,
  `onnxruntime`, `bioimageio.core` — no custom packages
- Factory signature: `def op_name(**kwargs) -> Callable[..., np.ndarray]`
- Inner function signature: `def run(*arrays: np.ndarray) -> np.ndarray`
- Include a docstring explaining what the op does and what tensors it expects

## Available ops

| File | Callable | Description |
|------|----------|-------------|
| `cellpose_flow_dynamics.py` | `cellpose_flow_dynamics` | Decode Cellpose flow fields into instance labels |
