# Custom Ops Library

Pre-built postprocessing (and preprocessing) factory functions for the BioImage Model Zoo.

Contributors ship their op **inline** with the model package during development, then
promote it here as a built-in once it is ready to be shared — **without changing anything
else in `rdf.yaml`**.

---

## Workflow: inline → built-in

### Step 1 — Develop inline (source shipped with model package)

Write a Python file and put it alongside your weights.
Reference it in `rdf.yaml`:

```yaml
postprocessing:
  - id: custom
    callable: my_postprocess        # class or function name
    source: my_postprocess.py       # packaged with the model
    sha256: <sha256 of the file>    # required — see below
    kwargs:                         # all optional
      threshold: 0.5
```

Compute the sha256:
```bash
python -c "import hashlib; print(hashlib.sha256(open('my_postprocess.py','rb').read()).hexdigest())"
```

### Step 2 — Promote to built-in (optional, for sharing)

1. Open a PR adding `my_postprocess.py` to this folder
2. Once merged, drop `source` and `sha256` from `rdf.yaml` — everything else stays the same:

```yaml
postprocessing:
  - id: custom
    callable: my_postprocess        # now resolved from custom_ops/
    kwargs:
      threshold: 0.5
```

`callable` name, `kwargs`, and runtime behaviour are **identical** in both stages.

---

## Writing an op — two supported styles

### Style 1 — Callable class (recommended for ops with configuration)

```python
# my_postprocess.py
import numpy as np

class my_postprocess:
    def __init__(self, threshold=0.5):
        """kwargs from rdf.yaml arrive here."""
        self.threshold = threshold

    def __call__(self, *arrays):
        """
        Model output tensors arrive here in rdf.yaml declaration order.
        Each array is a numpy.ndarray.
        Must return a single numpy.ndarray.
        """
        return (arrays[0] > self.threshold).astype(np.uint8)
```

### Style 2 — Factory function (closure over kwargs)

```python
# my_postprocess.py
import numpy as np

def my_postprocess(threshold=0.5):
    """kwargs from rdf.yaml arrive here. Return the per-image function."""
    def run(*arrays):
        """
        Model output tensors in rdf.yaml declaration order.
        Return a single numpy.ndarray.
        """
        return (arrays[0] > threshold).astype(np.uint8)
    return run
```

Both styles work identically. The runtime does:
```python
op = callable(**kwargs)   # __init__ or factory called once
result = op(*tensors)     # __call__ or inner function called per image
```

---

## Rules for contributed ops

- **One file per op**, filename = callable name (e.g. `cellpose_flow_dynamics.py`)
- **Imports**: only `numpy`, `scipy`, `scikit-image`, `torch`, `torchvision`,
  `tensorflow`, `onnxruntime`, `bioimageio.core` — no custom packages
- **Signature**: `callable(**kwargs)` returns something that accepts `*arrays` and returns `np.ndarray`
- **Docstring**: explain what the op does, expected tensor order, and what it returns
- **No side effects**: the op must be stateless across images (state held in `self` or closure is fine)

---

## Available built-in ops

| File | Callable | Description |
|------|----------|-------------|
| [`cellpose_flow_dynamics.py`](cellpose_flow_dynamics.py) | `cellpose_flow_dynamics` | Decode Cellpose/Cellpose-SAM flow fields into instance labels |
