"""Recreate the test outputs with NumPy and PyTorch 2.0 or newer.

After running this script, update the output SHA-256 values in bioimageio.yaml.
"""

from pathlib import Path

import numpy as np
import torch
from multi_tensor_unet import MultiTensorUNet

model_dir = Path(__file__).resolve().parent
inputs = []
for i in range(2):
    test_input = np.load(model_dir / f"test_input_{i}.npy").astype(np.float32)
    test_input = (test_input - test_input.mean()) / (test_input.std() + 1e-6)
    inputs.append(torch.from_numpy(test_input))

model = MultiTensorUNet(in_channels=2, out_channels=2, depth=3, initial_features=16)
_ = model.load_state_dict(
    torch.load(model_dir / "weights.pt", map_location="cpu", weights_only=True)
)
model = model.eval()
with torch.inference_mode():
    output0, output1 = model(*inputs)

np.save(model_dir / "test_output_0.npy", output0.numpy().astype(np.float32))
np.save(model_dir / "test_output_1.npy", output1.numpy().astype(np.float32))
