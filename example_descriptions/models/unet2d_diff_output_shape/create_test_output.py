"""Recreate the test output with NumPy and PyTorch."""

from pathlib import Path

import numpy as np
import torch
from resize_unet import ResizeUNet

model_dir = Path(__file__).resolve().parent
test_input = np.load(model_dir / "test_input.npy").astype(np.float32)
test_input = (test_input - test_input.mean()) / (test_input.std() + 1e-6)

model = ResizeUNet(in_channels=1, out_channels=1, depth=3, initial_features=16)
_ = model.load_state_dict(
    torch.load(model_dir / "weights.pt", map_location="cpu", weights_only=True)
)
model = model.eval()
with torch.inference_mode():
    test_output = model(torch.from_numpy(test_input)).numpy().astype(np.float32)

np.save(model_dir / "test_output.npy", test_output)
