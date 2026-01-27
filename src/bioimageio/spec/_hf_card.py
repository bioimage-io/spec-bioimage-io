from functools import partial
from pathlib import PurePosixPath
from typing import Any, Dict, Optional, Tuple

import numpy as np
from imageio.v3 import imread, imwrite  # pyright: ignore[reportUnknownVariableType]
from loguru import logger
from numpy.typing import NDArray
from typing_extensions import assert_never

from bioimageio.spec._internal.validation_context import get_validation_context
from bioimageio.spec.model.v0_5 import (
    KerasHdf5WeightsDescr,
    OnnxWeightsDescr,
    PytorchStateDictWeightsDescr,
    TensorflowJsWeightsDescr,
    TensorflowSavedModelBundleWeightsDescr,
    TorchscriptWeightsDescr,
)

from ._internal.io import RelativeFilePath, get_reader
from ._internal.io_utils import load_array
from ._version import VERSION
from .model import ModelDescr
from .utils import get_spdx_licenses, load_image


def _generate_png_from_tensor(tensor: NDArray[np.generic]) -> Optional[bytes]:
    """Generate PNG bytes from a sample tensor.

    Prefers 2D slices from multi-dimensional arrays.
    Returns PNG bytes or None if generation fails.
    """
    try:
        # Squeeze out singleton dimensions
        arr = np.squeeze(tensor)

        # Handle different dimensionalities
        if arr.ndim == 2:
            img_data = arr
        elif arr.ndim == 3:
            # Could be (H, W, C) or (Z, H, W)
            if arr.shape[-1] in [1, 3, 4]:  # Likely channels last
                img_data = arr
            else:  # Take middle slice
                img_data = arr[arr.shape[0] // 2]
        elif arr.ndim == 4:
            # Take middle slices (e.g., batch, z, y, x)
            img_data = (
                arr[0, arr.shape[1] // 2]
                if arr.shape[0] == 1
                else arr[arr.shape[0] // 2, arr.shape[1] // 2]
            )
        elif arr.ndim > 4:
            # Take middle slices of all extra dimensions
            slices = tuple(s // 2 for s in arr.shape[:-2])
            img_data = arr[slices]
        else:
            return None

        # Normalize to 0-255 uint8
        img_data = np.squeeze(img_data)
        if img_data.dtype != np.uint8:
            img_min, img_max = img_data.min(), img_data.max()
            if img_max > img_min:
                img_data: NDArray[Any] = (img_data - img_min) / (img_max - img_min)
            else:
                img_data = np.zeros_like(img_data)
            img_data = (img_data * 255).astype(np.uint8)
        return imwrite("<bytes>", img_data, extension=".png")
    except Exception:
        return None


def _get_io_description(model: ModelDescr) -> Tuple[str, Dict[str, bytes]]:
    """Generate a description of model inputs and outputs with sample images.

    Returns:
        A tuple of (markdown_string, referenced_files_dict) where referenced_files_dict maps
        filenames to file bytes.
    """
    sections = []
    images: dict[str, bytes] = {}

    # Input descriptions
    if model.inputs:
        sections.append("### Model Inputs\n")
        for inp in model.inputs:
            axes_str = ", ".join(str(a.id) for a in inp.axes)
            shape_str = " × ".join(
                str(a.size) if isinstance(a.size, int) else str(a.size)
                for a in inp.axes
            )

            inp_desc = f"`{inp.id}`: {inp.description or 'No description provided'}\n"
            inp_desc += f"- Axes: `{axes_str}`\n"
            inp_desc += f"- Shape: `{shape_str}`\n"
            inp_desc += f"- Data type: `{inp.dtype}`\n"

            # Try to load and display sample_tensor (preferred) or test_tensor
            img_bytes = None
            if inp.sample_tensor is not None:
                try:
                    arr = load_image(inp.sample_tensor)
                    img_bytes = _generate_png_from_tensor(arr)
                except Exception as e:
                    logger.error("failed to generate input sample image: {}", e)

            if img_bytes is None and inp.test_tensor is not None:
                try:
                    arr = load_array(inp.test_tensor)
                    img_bytes = _generate_png_from_tensor(arr)
                except Exception as e:
                    logger.error(
                        "failed to generate input sample image from test data: {}", e
                    )

            if img_bytes:
                filename = f"input_{inp.id}_sample.png"
                images[filename] = img_bytes
                inp_desc += f"\n![{inp.id} sample]({filename})\n"

            sections.append(inp_desc)

    # Output descriptions
    if model.outputs:
        sections.append("\n### Model Outputs\n")
        for out in model.outputs:
            axes_str = ", ".join(str(a.id) for a in out.axes)
            shape_str = " × ".join(
                str(a.size) if isinstance(a.size, int) else str(a.size)
                for a in out.axes
            )

            out_desc = f"**{out.id}**: {out.description or 'No description provided'}\n"
            out_desc += f"- Axes: `{axes_str}`\n"
            out_desc += f"- Shape: `{shape_str}`\n"
            out_desc += f"- Data type: `{out.dtype}`\n"

            # Try to load and display sample_tensor (preferred) or test_tensor
            img_bytes = None
            if out.sample_tensor is not None:
                try:
                    arr = load_image(out.sample_tensor)
                    img_bytes = _generate_png_from_tensor(arr)
                except Exception as e:
                    logger.error("failed to generate output sample image: {}", e)

            if img_bytes is None and out.test_tensor is not None:
                try:
                    arr = load_array(out.test_tensor)
                    img_bytes = _generate_png_from_tensor(arr)
                except Exception as e:
                    logger.error(
                        "failed to generate output sample image from test data: {}", e
                    )

            if img_bytes:
                filename = f"output_{out.id}_sample.png"
                images[filename] = img_bytes
                out_desc += f"\n![{out.id} sample]({filename})\n"

            sections.append(out_desc)

    return "\n".join(sections), images


def create_hf_model_card(model: ModelDescr) -> Tuple[ModelDescr, str, Dict[str, bytes]]:
    """Create a Hugging Face model card for a BioImage.IO model.

    Returns:
        A tuple of (markdown_string, images_dict) where images_dict maps
        filenames to PNG bytes that should be saved alongside the markdown.
    """
    referenced_files: Dict[str, bytes] = {}
    if model.documentation is None:
        doc_local_link = ""
    else:
        doc_reader = get_reader(model.documentation)
        local_doc_path = f"package/{doc_reader.original_file_name}"
        model = model.model_copy()
        with get_validation_context().replace(perform_io_checks=False):
            model.documentation = RelativeFilePath(PurePosixPath(local_doc_path))

        doc_local_link = f"[{doc_reader.original_file_name}]({local_doc_path})"
        referenced_files[doc_reader.original_file_name] = doc_reader.read()

    shared_by = (
        "".join(
            (
                f"\n    - {a.name}"
                + (f", {a.affiliation}" if a.affiliation else "")
                + (
                    f", [https://orcid.org/{a.orcid}](https://orcid.org/{a.orcid})"
                    if a.orcid
                    else ""
                )
                + (
                    f", [https://github.com/{a.github_user}](https://github.com/{a.github_user})"
                    if a.github_user
                    else ""
                )
                for a in model.authors
            )
        )
        if model.authors
        else "missing"
    )

    developed_by = (
        "".join(
            (
                f"\n    - {c.text}: "
                + (f"https://www.doi.org/{c.doi}" if c.doi else str(c.url))
            )
            for c in model.cite
        )
        if model.cite
        else " missing"
    )
    if model.license is None:
        license = "missing"
    else:
        matches = [
            (entry["name"], entry["reference"])
            for entry in get_spdx_licenses()["licenses"]
            if entry["licenseId"] == model.license
        ]
        if matches:
            if len(matches) > 1:
                logger.warning(
                    "Multiple SPDX license matches found for '{}', using the first one.",
                    model.license,
                )
            name, reference = matches[0]
            license = f"[{name}]({reference})"
        else:
            license = model.license

    repository = (
        f"[{model.git_repo}]({model.git_repo})" if model.git_repo else "missing"
    )

    # Get input/output descriptions with images
    io_desc, images = _get_io_description(model)
    assert not any(k in referenced_files for k in images.keys()), (
        "filename collision in referenced files"
    )
    referenced_files.update(images)

    dl_framework = []
    model_size: Optional[str] = None
    for weights in model.weights.available_formats.values():
        if isinstance(weights, (PytorchStateDictWeightsDescr, TorchscriptWeightsDescr)):
            dl_framework_version = weights.pytorch_version
        elif isinstance(
            weights,
            (
                TensorflowSavedModelBundleWeightsDescr,
                TensorflowJsWeightsDescr,
                KerasHdf5WeightsDescr,
            ),
        ):
            dl_framework_version = weights.tensorflow_version
        elif isinstance(weights, OnnxWeightsDescr):
            dl_framework_version = f"opset version: {weights.opset_version}"
        else:
            assert_never(weights)

        dl_framework.append(f"{weights.weights_format_name}: {dl_framework_version}")

        if model_size is None:
            s = 0
            r = weights.get_reader()
            for chunk in iter(partial(r.read, 128 * 1024), b""):
                s += len(chunk)

            if model.config.bioimageio.model_parameter_count is not None:
                if model.config.bioimageio.model_parameter_count < 1e9:
                    model_size = f"{model.config.bioimageio.model_parameter_count / 1e6:.2f} million parameters, "
                else:
                    model_size = f"{model.config.bioimageio.model_parameter_count / 1e9:.2f} billion parameters, "
            else:
                model_size = ""

            if s < 1e9:
                model_size += f"{s / 1e6:.2f} MB"
            else:
                model_size += f"{s / 1e9:.2f} GB"

    if (
        model.weights.pytorch_state_dict is not None
        and model.weights.pytorch_state_dict.dependencies is not None
    ):
        referenced_files["environment.yaml"] = (
            model.weights.pytorch_state_dict.dependencies.get_reader().read()
        )
        dependencies = "Depdencies for pytorch state dicht weights listed in [environment.yaml](environment.yaml)."
    else:
        dependencies = "none beyond the respective framework"

    out_of_scope_use = (
        model.config.bioimageio.out_of_scope_use
        if model.config.bioimageio.out_of_scope_use
        else """missing; therefore these limitations should be considered:

- *Likely not suitable for diagnostic purposes.*
- *Likely not validated for different imaging modalities than present in the training data.*
- *Should not be used without proper validation on user's specific datasets.*

"""
    )

    evaluation = (
        "".join(
            e.format_md()
            for e in model.config.bioimageio.evaluations
            if e.dataset_role != "independent"
        )
        or "missing"
    )

    evaluation += "\n### Validation on External Data\n"
    evaluation += (
        "".join(
            e.format_md()
            for e in model.config.bioimageio.evaluations
            if e.dataset_role == "independent"
        )
        or "missing"
    )

    markdown = f"""# {model.name}

{model.description or ""}


# Table of Contents

- [Model Details](#model-details)
- [Uses](#uses)
- [Task Details](#task-details)
- [Bias, Risks, and Limitations](#bias-risks-and-limitations)
- [Training Details](#training-details)
- [Evaluation](#evaluation)
- [Environmental Impact](#environmental-impact)
- [Technical Specifications](#technical-specifications)
- [How to Get Started with the Model](#how-to-get-started-with-the-model)


# Model Details

## Model Description

- **model version:** {model.version or "missing"}
- **Additional model documentation:** {doc_local_link or "missing"}
- **Developed by:**{developed_by}
- **Funded by:** {
        model.config.bioimageio.funded_by
        if model.config.bioimageio.funded_by
        else "missing"
    }
- **Shared by:** {shared_by}
- **Model type:** {
        model.config.bioimageio.model_type
        if model.config.bioimageio.model_type
        else "missing"
    }
- **Modality:** {
        model.config.bioimageio.modality
        if model.config.bioimageio.modality
        else "missing"
    }
- **License:** {license}
- **Finetuned from model:** {"N/A" if model.parent is None else model.parent.id}

## Model Sources

- **Repository:** {repository}
- **Paper:** see **Developed by**

# Uses

## Direct Use

{io_desc}

## Downstream Use

This model is compatible with the bioimageio.spec Python package (version >= {
        VERSION
    }) and other bioimage.io tools like the bioimageio.core Python package supporting model inference in Python code or via the `bioimageio` CLI.
Specific bioimage.io partner tool compatibilities may be reported at [Compatibility Reports](https://bioimage-io.github.io/collection/latest/compatibility/#compatibility-by-resource).
{
        "Training (and fine-tuning) code may be available at " + model.git_repo + "."
        if model.git_repo
        else ""
    }

## Out-of-Scope Use

{out_of_scope_use}

# Task Details

*Bioimage-specific task information*

- **Task type:** *[segmentation, classification, detection, denoising, etc.]*
- **Input modality:** *[2D/3D fluorescence, brightfield, EM, etc.]*
- **Target structures:** *[nuclei, cells, organelles, etc.]*
- **Imaging technique:** *[confocal, widefield, super-resolution, etc.]*
- **Spatial resolution:** *[pixel/voxel size requirements]*
- **Temporal resolution:** *[if applicable]*

# Bias, Risks, and Limitations

## Known Biases

{
        model.config.bioimageio.known_biases
        if model.config.bioimageio.known_biases
        else "missing"
    }

## Risks

{model.config.bioimageio.risks if model.config.bioimageio.risks else "missing"}

## Limitations

{
        model.config.bioimageio.limitations
        if model.config.bioimageio.limitations
        else "missing"
    }

## Recommendations

{
        model.config.bioimageio.recommendations
        if model.config.bioimageio.recommendations
        else "missing"
    }

# Training Details

## Training Data

{
        "This model was trained on `" + str(model.training_data.id) + "`."
        if model.training_data is not None
        else "missing"
    }

## Training Procedure

### Preprocessing

{model.config.bioimageio.training_preprocessing or "missing"}

### Training Hyperparameters

- **Architecture:** {model.config.bioimageio.architecture or "missing"}
- **Framework:** {dl_framework.join(", ")}
- **Epochs:** {model.config.bioimageio.training_epochs or "missing"}
- **Batch size:** {model.config.bioimageio.training_batch_size or "missing"}
- **Learning rate:** {model.config.bioimageio.initial_learning_rate or "missing"} {
        model.config.bioimageio.learning_rate_schedule or ""
    }
- **Loss function:** {model.config.bioimageio.loss_function or "missing"} {
        "with " + str(model.config.bioimageio.loss_function_kwargs)
        if model.config.bioimageio.loss_function_kwargs
        else ""
    }
- **Optimizer:** {model.config.bioimageio.optimizer or "missing"} {
        "with " + str(model.config.bioimageio.optimizer_kwargs)
        if model.config.bioimageio.optimizer_kwargs
        else ""
    }
- **Regularization:** {model.config.bioimageio.regularization or "missing"}

### Speeds, Sizes, Times

- **Training time:** {
        "{:.2f}".format(model.config.bioimageio.training_duration)
        if model.config.bioimageio.training_duration is not None
        else "missing"
    }
- **Model size:** {model_size}
- **Inference time:** {model.config.bioimageio.inference_time or "missing"}
- **Memory requirements:** {
        model.config.bioimageio.memory_requirements_inference or "missing"
    }

# Evaluation

{evaluation}

## Societal Impact Assessment

{model.config.bioimageio.societal_impact_assessment or "missing"}

# Environmental Impact

{model.config.bioimageio.environmental_impact.format_md()}

# Technical Specifications

## Model Architecture and Objective

*Detailed technical specifications:*

- **Architecture:** *[Detailed network architecture]*
- **Input specifications:** *[Tensor shapes, data types, preprocessing]*
- **Output specifications:** *[Output format and interpretation]*
- **Objective function:** *[Loss function and optimization details]*

## Compute Infrastructure

### Hardware Requirements

- **Training:** GPU memory: {
        model.config.bioimageio.memory_requirements_training or "missing"
    },
- **Inference:** GPU memory: {
        model.config.bioimageio.memory_requirements_inference or "missing"
    }
- **Storage:** Model size: {model_size}

### Software Dependencies

*Software requirements:*

- **Framework:** {dl_framework.join(", ")}
- **Libraries:** {dependencies}
- **BioImage.IO partner compatibility:** [Compatibility Reports](https://bioimage-io.github.io/collection/latest/compatibility/#compatibility-by-resource)

# How to Get Started with the Model

{io_desc}

## Usage Instructions

*Provide step-by-step instructions for using the model with the above inputs/outputs:*

---

## Glossary

*Define domain-specific terms:*

- **CLI**: *Command Line Interface*
- **IoU (Intersection over Union):** *Metric for evaluating segmentation quality*
- **Dice coefficient:** *Similarity metric for binary segmentation*
- **Voxel:** *3D pixel representing volume element*
- **Z-projection:** *2D representation of 3D data*

---

*This model card was created using the template of the bioimageio.spec Python Package, which intern is based on the BioImage Model Zoo template, incorporating best practices from the Hugging Face Model Card Template. For more information on contributing models, visit [bioimage.io](https://bioimage.io).*

---

**References:**

- [Hugging Face Model Card Template](https://huggingface.co/docs/hub/en/model-card-annotated)
- [BioImage Model Zoo Documentation](https://bioimage.io/docs/)
- [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993)
- [bioimageio.spec Python Package](https://bioimage-io.github.io/spec-bioimage-io)
"""

    return markdown, images
