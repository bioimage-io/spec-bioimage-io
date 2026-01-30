import collections.abc
import warnings
from functools import partial
from pathlib import PurePosixPath
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np
from imageio.v3 import imwrite  # pyright: ignore[reportUnknownVariableType]
from loguru import logger
from numpy.typing import NDArray
from typing_extensions import assert_never

from bioimageio.spec._internal.validation_context import get_validation_context
from bioimageio.spec.model.v0_5 import (
    IntervalOrRatioDataDescr,
    KerasHdf5WeightsDescr,
    NominalOrOrdinalDataDescr,
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
    markdown_string = ""
    images: dict[str, bytes] = {}

    def format_data_descr(
        d: Union[
            NominalOrOrdinalDataDescr,
            IntervalOrRatioDataDescr,
            Sequence[Union[NominalOrOrdinalDataDescr, IntervalOrRatioDataDescr]],
        ],
    ) -> str:
        ret = ""
        if isinstance(d, NominalOrOrdinalDataDescr):
            ret += f"        - Values: {d.values}\n"
        elif isinstance(d, IntervalOrRatioDataDescr):
            ret += f"        - Values: {d.scale} {d.unit} with offset: {d.offset} in range {d.range}\n"
        elif isinstance(d, collections.abc.Sequence):
            for dd in d:
                ret += format_data_descr(dd)
        else:
            assert_never(d)

        return ret

    # Input descriptions
    if model.inputs:
        markdown_string += "\n    - **Input specifications:**\n"

        for inp in model.inputs:
            axes_str = ", ".join(str(a.id) for a in inp.axes)
            shape_str = " × ".join(
                str(a.size) if isinstance(a.size, int) else str(a.size)
                for a in inp.axes
            )

            markdown_string += (
                f"      `{inp.id}`: {inp.description or 'No description provided'}\n"
            )
            markdown_string += f"        - Axes: `{axes_str}`\n"
            markdown_string += f"        - Shape: `{shape_str}`\n"
            markdown_string += f"        - Data type: `{inp.dtype}`\n"
            markdown_string += format_data_descr(inp.data)

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
                markdown_string += (
                    f"        - example\n          ![{inp.id} sample]({filename})\n"
                )

    # Output descriptions
    if model.outputs:
        markdown_string += "\n    - **Output specifications:**\n"
        for out in model.outputs:
            axes_str = ", ".join(str(a.id) for a in out.axes)
            shape_str = " × ".join(
                str(a.size) if isinstance(a.size, int) else str(a.size)
                for a in out.axes
            )

            markdown_string += (
                f"      **{out.id}**: {out.description or 'No description provided'}\n"
            )
            markdown_string += f"      - Axes: `{axes_str}`\n"
            markdown_string += f"      - Shape: `{shape_str}`\n"
            markdown_string += f"      - Data type: `{out.dtype}`\n"
            markdown_string += format_data_descr(out.data)

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
                markdown_string += (
                    f"      - example\n        ![{out.id} sample]({filename})\n"
                )

    return markdown_string, images


def create_huggingface_model_card(model: ModelDescr) -> Tuple[str, Dict[str, bytes]]:
    """Create a Hugging Face model card for a BioImage.IO model.

    Returns:
        A tuple of (markdown_string, images_dict) where images_dict maps
        filenames to PNG bytes that should be saved alongside the markdown.
    """
    if model.version is None:
        model_version = ""
    else:
        model_version = f"\n- **model version:** {model.version}"

    if model.documentation is None:
        additional_model_doc = ""
    else:
        doc_reader = get_reader(model.documentation)
        local_doc_path = f"package/{doc_reader.original_file_name}"
        model = model.model_copy()
        with get_validation_context().replace(perform_io_checks=False):
            model.documentation = RelativeFilePath(PurePosixPath(local_doc_path))

        doc_local_link = f"[{doc_reader.original_file_name}]({local_doc_path})"
        additional_model_doc = (
            f"\n- **Additional model documentation:** {doc_local_link}"
        )

    if model.cite:
        developed_by = "\n- **Developed by:** " + (
            "".join(
                (
                    f"\n    - {c.text}: "
                    + (f"https://www.doi.org/{c.doi}" if c.doi else str(c.url))
                )
                for c in model.cite
            )
        )
    else:
        developed_by = ""

    if model.config.bioimageio.funded_by:
        funded_by = f"\n- **Funded by:** {model.config.bioimageio.funded_by}"
    else:
        funded_by = ""

    if model.authors:
        shared_by = "\n- **Shared by:** " + (
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
        )
    else:
        shared_by = ""

    if model.config.bioimageio.architecture_type:
        model_type = f"\n- **Model type:** {model.config.bioimageio.architecture_type}"
    else:
        model_type = ""

    if model.config.bioimageio.modality:
        model_modality = f"\n- **Modality:** {model.config.bioimageio.modality}"
    else:
        model_modality = ""

    if model.config.bioimageio.target_structure:
        target_structures = f"\n- **Target structures:** " + ", ".join(
            model.config.bioimageio.target_structure
        )
    else:
        target_structures = ""

    if model.config.bioimageio.task:
        task_type = f"\n- **Task type:** {model.config.bioimageio.task}"
    else:
        task_type = ""

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

    if model.parent:
        finetuned_from = f"\n- **Finetuned from model:** {model.parent.id}"
    else:
        finetuned_from = ""

    repository = (
        f"[{model.git_repo}]({model.git_repo})" if model.git_repo else "missing"
    )

    dl_frameworks: List[str] = []
    training_frameworks: List[str] = []
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

        if weights.parent is None:
            training_frameworks.append(weights.weights_format_name)

        dl_frameworks.append(f"{weights.weights_format_name}: {dl_framework_version}")

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

    if len(training_frameworks) > 1:
        warnings.warn(
            "Multiple training frameworks detected. (Some weight formats are probably missing a `parent` reference.)"
        )

    if (
        model.weights.pytorch_state_dict is not None
        and model.weights.pytorch_state_dict.dependencies is not None
    ):
        env_reader = model.weights.pytorch_state_dict.dependencies.get_reader()
        dependencies = f"Dependencies for Pytorch State dict weights are listed in [{env_reader.original_file_name}](package/{env_reader.original_file_name})."
    else:
        dependencies = "None beyond the respective framework library."

    out_of_scope_use = (
        model.config.bioimageio.out_of_scope_use
        if model.config.bioimageio.out_of_scope_use
        else """missing; therefore these limitations should be considered:

- *Likely not suitable for diagnostic purposes.*
- *Likely not validated for different imaging modalities than present in the training data.*
- *Should not be used without proper validation on user's specific datasets.*

"""
    )

    evaluation_parts: List[str] = []
    n_evals = 0
    for e in model.config.bioimageio.evaluations:
        if e.dataset_role == "independent":
            continue  # treated separately below

        n_evals += 1
        if n_evals == 1:
            n_evals_str = ""
        else:
            n_evals_str = f" {n_evals}"

        evaluation_parts.append(f"# Evaluation{n_evals_str}\n")
        evaluation_parts.append(e.format_md())

    if not evaluation_parts:
        evaluation_parts.append("# Evaluation\n")
        evaluation_parts.append("missing")

    evaluation_parts.append("### Validation on External Data\n")

    n_evals = 0
    for e in model.config.bioimageio.evaluations:
        if e.dataset_role != "independent":
            continue  # treated separately above

        n_evals += 1
        if n_evals == 1:
            n_evals_str = ""
        else:
            n_evals_str = f" {n_evals}"

        evaluation_parts.append(f"### Validation on External Data{n_evals_str}\n")
        evaluation_parts.append(e.format_md())

    if n_evals == 0:
        evaluation_parts.append("missing")

    evaluation = "\n".join(evaluation_parts)

    training_details = ""
    if model.config.bioimageio.training.training_preprocessing:
        training_details += f"### Preprocessing\n\n{model.config.bioimageio.training.training_preprocessing}\n\n"

    training_details += "### Training Hyperparameters\n\n"
    training_details += f"    # - **Framework:** {' / '.join(training_frameworks)}"
    if model.config.bioimageio.training.training_epochs is not None:
        training_details += (
            f"    - **Epochs:** {model.config.bioimageio.training.training_epochs}\n"
        )

    if model.config.bioimageio.training.training_batch_size is not None:
        training_details += f"    - **Batch size:** {model.config.bioimageio.training.training_batch_size}\n"

    if model.config.bioimageio.training.initial_learning_rate is not None:
        training_details += f"    - **Initial learning rate:** {model.config.bioimageio.training.initial_learning_rate}\n"

    if model.config.bioimageio.training.learning_rate_schedule is not None:
        training_details += f"    - **Learning rate schedule:** {model.config.bioimageio.training.learning_rate_schedule}\n"

    if model.config.bioimageio.training.loss_function is not None:
        training_details += (
            f"    - **Loss function:** {model.config.bioimageio.training.loss_function}"
        )
        if model.config.bioimageio.training.loss_function_kwargs:
            training_details += (
                f" with {model.config.bioimageio.training.loss_function_kwargs}"
            )
        training_details += "\n"

    if model.config.bioimageio.training.optimizer is not None:
        training_details += (
            f"    - **Optimizer:** {model.config.bioimageio.training.optimizer}"
        )
        if model.config.bioimageio.training.optimizer_kwargs:
            training_details += (
                f" with {model.config.bioimageio.training.optimizer_kwargs}"
            )
        training_details += "\n"

    if model.config.bioimageio.training.regularization is not None:
        training_details += f"    - **Regularization:** {model.config.bioimageio.training.regularization}\n"

    speeds_sizes_times = "### Speeds, Sizes, Times\n\n"
    if model.config.bioimageio.training.training_duration is not None:
        speeds_sizes_times += f"    - **Training time:** {'{:.2f}'.format(model.config.bioimageio.training.training_duration)}\n"

    speeds_sizes_times += f"    - **Model size:** {model_size}\n"
    if model.config.bioimageio.inference_time:
        speeds_sizes_times += (
            f"    - **Inference time:** {model.config.bioimageio.inference_time}\n"
        )

    if model.config.bioimageio.memory_requirements_inference:
        speeds_sizes_times += f"    - **Memory requirements:** {model.config.bioimageio.memory_requirements_inference}\n"

    model_arch_and_objective = "## Model Architecture and Objective\n\n"
    if (
        model.config.bioimageio.architecture_type
        or model.config.bioimageio.architecture_description
    ):
        model_arch_and_objective += (
            f"    - **Architecture:** {model.config.bioimageio.architecture_type or ''}"
            + (
                " --- "
                if model.config.bioimageio.architecture_type
                and model.config.bioimageio.architecture_description
                else ""
            )
            + (
                model.config.bioimageio.architecture_description
                if model.config.bioimageio.architecture_description is not None
                else ""
            )
            + "\n"
        )

    io_desc, referenced_files = _get_io_description(model)
    model_arch_and_objective += io_desc

    hardware_requirements = "\n### Hardware Requirements\n"
    if model.config.bioimageio.memory_requirements_training is not None:
        hardware_requirements += f"    - **Training:** GPU memory: {model.config.bioimageio.memory_requirements_training}\n"

    if model.config.bioimageio.memory_requirements_inference is not None:
        hardware_requirements += f"    - **Inference:** GPU memory: {model.config.bioimageio.memory_requirements_inference}\n"

    hardware_requirements += f"    - **Storage:** Model size: {model_size}\n"

    markdown = f"""# {model.name}

{model.description or ""}


# Table of Contents

- [Model Details](#model-details)
- [Uses](#uses)
- [Bias, Risks, and Limitations](#bias-risks-and-limitations)
- [How to Get Started with the Model](#how-to-get-started-with-the-model)
- [Training Details](#training-details)
- [Evaluation](#evaluation)
- [Environmental Impact](#environmental-impact)
- [Technical Specifications](#technical-specifications)


# Model Details

## Model Description
{model_version}{additional_model_doc}{developed_by}{funded_by}{shared_by}{model_type}{
        model_modality
    }{target_structures}{task_type}
- **License:** {license}{finetuned_from}

## Model Sources

- **Repository:** {repository}
- **Paper:** see [**Developed by**](#model-description)

# Uses

## Direct Use

This model is compatible with the bioimageio.spec Python package (version >= {
        VERSION
    }) and the bioimageio.core Python package supporting model inference in Python code or via the `bioimageio` CLI.



## Downstream Use

Specific bioimage.io partner tool compatibilities may be reported at [Compatibility Reports](https://bioimage-io.github.io/collection/latest/compatibility/#compatibility-by-resource).
{
        "Training (and fine-tuning) code may be available at " + model.git_repo + "."
        if model.git_repo
        else ""
    }

## Out-of-Scope Use

{out_of_scope_use}


{model.config.bioimageio.bias_risks_limitations.format_md()}

# How to Get Started with the Model

`pip install bioimageio.core[dev]`

Get started using the test sample provided by the model:
```python
from bioimageio.core import load_model_description, predict
from bioimageio.core.digest_spec import get_test_input_sample

model_descr = load_model_description("<model.yaml or model.zip path or URL>")
input_sample = get_test_input_sample(model_descr)
output_sample = predict(model=model_descr, inputs=input_sample)
```

Deploy on your own data:
```python
from bioimageio.core.digest_spec import create_sample_for_model

input_sample = create_sample_for_model(
    model_descr,
    inputs={{"raw": "<path to your input image>"}}
)
output_sample = predict(model=model_descr, inputs=input_sample)
```

Alternatively, use the `bioimageio` CLI provided by the `bioimageio.core` package:

```console
bioimageio predict --help
```

# Training Details

## Training Data

{
        "This model was trained on `" + str(model.training_data.id) + "`."
        if model.training_data is not None
        else "missing"
    }

## Training Procedure

{training_details}

{speeds_sizes_times}

{evaluation}

{model.config.bioimageio.environmental_impact.format_md()}

# Technical Specifications

{model_arch_and_objective}

## Compute Infrastructure

{hardware_requirements}

### Software

- **Framework:** {" or ".join(dl_frameworks)}
- **Libraries:** {dependencies}
- **BioImage.IO partner compatibility:** [Compatibility Reports](https://bioimage-io.github.io/collection/latest/compatibility/#compatibility-by-resource)

---

*This model card was created using the template of the bioimageio.spec Python Package, which intern is based on the BioImage Model Zoo template, incorporating best practices from the Hugging Face Model Card Template. For more information on contributing models, visit [bioimage.io](https://bioimage.io).*

---

**References:**

- [Hugging Face Model Card Template](https://huggingface.co/docs/hub/en/model-card-annotated)
- [Hugging Face modelcard_template.md](https://github.com/huggingface/huggingface_hub/blob/b9decfdf9b9a162012bc52f260fd64fc37db660e/src/huggingface_hub/templates/modelcard_template.md)
- [BioImage Model Zoo Documentation](https://bioimage.io/docs/)
- [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993)
- [bioimageio.spec Python Package](https://bioimage-io.github.io/spec-bioimage-io)
"""

    return markdown, referenced_files
