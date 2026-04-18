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

Two styles are supported — pick whichever feels natural:

**Style 1 — callable class** (recommended for ops with configuration):

```python
# my_op.py
import numpy as np

class my_op:
    def __init__(self, threshold=0.5):
        self.threshold = threshold          # kwargs land here

    def __call__(self, *arrays):
        # arrays = model output tensors in rdf.yaml declaration order
        return (arrays[0] > self.threshold).astype(np.uint8)
```

**Style 2 — factory function** (closure over kwargs):

```python
# my_op.py
import numpy as np

def my_op(threshold=0.5):
    """Called once with kwargs; returns the per-image function."""
    def run(*arrays):
        # arrays = model output tensors in rdf.yaml declaration order
        return (arrays[0] > threshold).astype(np.uint8)
    return run
```

Both are used identically in `rdf.yaml` — the runtime handles either.

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
