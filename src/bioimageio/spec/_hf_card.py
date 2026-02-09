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
    TensorId,
    TorchscriptWeightsDescr,
)

from ._internal.io import RelativeFilePath, get_reader
from ._internal.io_utils import load_array
from ._version import VERSION
from .model import ModelDescr
from .utils import get_spdx_licenses, load_image

HF_KNOWN_LICENSES = (
    "apache-2.0",
    "mit",
    "openrail",
    "bigscience-openrail-m",
    "creativeml-openrail-m",
    "bigscience-bloom-rail-1.0",
    "bigcode-openrail-m",
    "afl-3.0",
    "artistic-2.0",
    "bsl-1.0",
    "bsd",
    "bsd-2-clause",
    "bsd-3-clause",
    "bsd-3-clause-clear",
    "c-uda",
    "cc",
    "cc0-1.0",
    "cc-by-2.0",
    "cc-by-2.5",
    "cc-by-3.0",
    "cc-by-4.0",
    "cc-by-sa-3.0",
    "cc-by-sa-4.0",
    "cc-by-nc-2.0",
    "cc-by-nc-3.0",
    "cc-by-nc-4.0",
    "cc-by-nd-4.0",
    "cc-by-nc-nd-3.0",
    "cc-by-nc-nd-4.0",
    "cc-by-nc-sa-2.0",
    "cc-by-nc-sa-3.0",
    "cc-by-nc-sa-4.0",
    "cdla-sharing-1.0",
    "cdla-permissive-1.0",
    "cdla-permissive-2.0",
    "wtfpl",
    "ecl-2.0",
    "epl-1.0",
    "epl-2.0",
    "etalab-2.0",
    "eupl-1.1",
    "eupl-1.2",
    "agpl-3.0",
    "gfdl",
    "gpl",
    "gpl-2.0",
    "gpl-3.0",
    "lgpl",
    "lgpl-2.1",
    "lgpl-3.0",
    "isc",
    "h-research",
    "intel-research",
    "lppl-1.3c",
    "ms-pl",
    "apple-ascl",
    "apple-amlr",
    "mpl-2.0",
    "odc-by",
    "odbl",
    "openmdw-1.0",
    "openrail++",
    "osl-3.0",
    "postgresql",
    "ofl-1.1",
    "ncsa",
    "unlicense",
    "zlib",
    "pddl",
    "lgpl-lr",
    "deepfloyd-if-license",
    "fair-noncommercial-research-license",
    "llama2",
    "llama3",
    "llama3.1",
    "llama3.2",
    "llama3.3",
    "llama4",
    "grok2-community",
    "gemma",
)


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


def _get_io_description(
    model: ModelDescr,
) -> Tuple[str, Dict[str, bytes], List[TensorId], List[TensorId]]:
    """Generate a description of model inputs and outputs with sample images.

    Returns:
        A tuple of (markdown_string, referenced_files_dict, input_ids, output_ids) where referenced_files_dict maps
        filenames to file bytes.
    """
    markdown_string = ""
    referenced_files: dict[str, bytes] = {}
    input_ids: List[TensorId] = []
    output_ids: List[TensorId] = []

    def format_data_descr(
        d: Union[
            NominalOrOrdinalDataDescr,
            IntervalOrRatioDataDescr,
            Sequence[Union[NominalOrOrdinalDataDescr, IntervalOrRatioDataDescr]],
        ],
    ) -> str:
        ret = ""
        if isinstance(d, NominalOrOrdinalDataDescr):
            ret += f"  - Values: {d.values}\n"
        elif isinstance(d, IntervalOrRatioDataDescr):
            ret += f"  - Value unit: {d.unit}\n"
            ret += f"  - Value scale factor: {d.scale}\n"
            if d.offset is not None:
                ret += f"  - Value offset: {d.offset}\n"
            elif d.range[0] is not None:
                ret += f"  - Value minimum: {d.range[0]}\n"
            elif d.range[1] is not None:
                ret += f"  - Value maximum: {d.range[1]}\n"
        elif isinstance(d, collections.abc.Sequence):
            for dd in d:
                ret += format_data_descr(dd)
        else:
            assert_never(d)

        return ret

    # Input descriptions
    if model.inputs:
        markdown_string += "\n- **Input specifications:**\n"

        for inp in model.inputs:
            input_ids.append(inp.id)
            axes_str = ", ".join(str(a.id) for a in inp.axes)
            shape_str = " × ".join(
                str(a.size) if isinstance(a.size, int) else str(a.size)
                for a in inp.axes
            )

            markdown_string += f"  `{inp.id}`: {inp.description or ''}\n\n"
            markdown_string += f"  - Axes: `{axes_str}`\n"
            markdown_string += f"  - Shape: `{shape_str}`\n"
            markdown_string += f"  - Data type: `{inp.dtype}`\n"
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
                filename = f"images/input_{inp.id}_sample.png"
                referenced_files[filename] = img_bytes
                markdown_string += f"  - example\n    ![{inp.id} sample]({filename})\n"

    # Output descriptions
    if model.outputs:
        markdown_string += "\n- **Output specifications:**\n"
        for out in model.outputs:
            output_ids.append(out.id)
            axes_str = ", ".join(str(a.id) for a in out.axes)
            shape_str = " × ".join(
                str(a.size) if isinstance(a.size, int) else str(a.size)
                for a in out.axes
            )

            markdown_string += f"  `{out.id}`: {out.description or ''}\n"
            markdown_string += f"  - Axes: `{axes_str}`\n"
            markdown_string += f"  - Shape: `{shape_str}`\n"
            markdown_string += f"  - Data type: `{out.dtype}`\n"
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
                filename = f"images/output_{out.id}_sample.png"
                referenced_files[filename] = img_bytes
                markdown_string += f"  - example\n    {out.id} sample]({filename})\n"

    return markdown_string, referenced_files, input_ids, output_ids


def create_huggingface_model_card(
    model: ModelDescr, *, repo_id: str
) -> Tuple[str, Dict[str, bytes]]:
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

        additional_model_doc = f"\n- **Additional model documentation:** [{local_doc_path}]({local_doc_path})"

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
        target_structures = "\n- **Target structures:** " + ", ".join(
            model.config.bioimageio.target_structure
        )
    else:
        target_structures = ""

    if model.config.bioimageio.task:
        task_type = f"\n- **Task type:** {model.config.bioimageio.task}"
    else:
        task_type = ""

    if model.parent:
        finetuned_from = f"\n- **Finetuned from model:** {model.parent.id}"
    else:
        finetuned_from = ""

    repository = (
        f"[{model.git_repo}]({model.git_repo})" if model.git_repo else "missing"
    )

    dl_framework_parts: List[str] = []
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

        dl_framework_parts.append(
            f"\n    - {weights.weights_format_name}: {dl_framework_version}"
        )

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

    dl_frameworks = "".join(dl_framework_parts)
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
        else """missing; therefore these typical limitations should be considered:

- *Likely not suitable for diagnostic purposes.*
- *Likely not validated for different imaging modalities than present in the training data.*
- *Should not be used without proper validation on user's specific datasets.*

"""
    )

    environmental_impact = model.config.bioimageio.environmental_impact.format_md()
    if environmental_impact:
        environmental_impact_toc_entry = (
            "\n- [Environmental Impact](#environmental-impact)"
        )
    else:
        environmental_impact_toc_entry = ""

    evaluation_parts: List[str] = []
    n_evals = 0
    for e in model.config.bioimageio.evaluations:
        if e.dataset_role == "independent":
            continue  # treated separately below

        n_evals += 1
        n_evals_str = "" if n_evals == 1 else f" {n_evals}"
        evaluation_parts.append(f"\n# Evaluation{n_evals_str}\n")
        evaluation_parts.append(e.format_md())

    n_evals = 0
    for e in model.config.bioimageio.evaluations:
        if e.dataset_role != "independent":
            continue  # treated separately above

        n_evals += 1
        n_evals_str = "" if n_evals == 1 else f" {n_evals}"

        evaluation_parts.append(f"### Validation on External Data{n_evals_str}\n")
        evaluation_parts.append(e.format_md())

    if evaluation_parts:
        evaluation = "\n".join(evaluation_parts)
        evaluation_toc_entry = "\n- [Evaluation](#evaluation)"
    else:
        evaluation = ""
        evaluation_toc_entry = ""

    training_details = ""
    if model.config.bioimageio.training.training_preprocessing:
        training_details += f"### Preprocessing\n\n{model.config.bioimageio.training.training_preprocessing}\n\n"

    training_details += "### Training Hyperparameters\n\n"
    training_details += f"- **Framework:** {' / '.join(training_frameworks)}"
    if model.config.bioimageio.training.training_epochs is not None:
        training_details += (
            f"- **Epochs:** {model.config.bioimageio.training.training_epochs}\n"
        )

    if model.config.bioimageio.training.training_batch_size is not None:
        training_details += f"- **Batch size:** {model.config.bioimageio.training.training_batch_size}\n"

    if model.config.bioimageio.training.initial_learning_rate is not None:
        training_details += f"- **Initial learning rate:** {model.config.bioimageio.training.initial_learning_rate}\n"

    if model.config.bioimageio.training.learning_rate_schedule is not None:
        training_details += f"- **Learning rate schedule:** {model.config.bioimageio.training.learning_rate_schedule}\n"

    if model.config.bioimageio.training.loss_function is not None:
        training_details += (
            f"- **Loss function:** {model.config.bioimageio.training.loss_function}"
        )
        if model.config.bioimageio.training.loss_function_kwargs:
            training_details += (
                f" with {model.config.bioimageio.training.loss_function_kwargs}"
            )
        training_details += "\n"

    if model.config.bioimageio.training.optimizer is not None:
        training_details += (
            f"- **Optimizer:** {model.config.bioimageio.training.optimizer}"
        )
        if model.config.bioimageio.training.optimizer_kwargs:
            training_details += (
                f" with {model.config.bioimageio.training.optimizer_kwargs}"
            )
        training_details += "\n"

    if model.config.bioimageio.training.regularization is not None:
        training_details += (
            f"- **Regularization:** {model.config.bioimageio.training.regularization}\n"
        )

    speeds_sizes_times = "### Speeds, Sizes, Times\n\n"
    if model.config.bioimageio.training.training_duration is not None:
        speeds_sizes_times += f"- **Training time:** {'{:.2f}'.format(model.config.bioimageio.training.training_duration)}\n"

    speeds_sizes_times += f"- **Model size:** {model_size}\n"
    if model.config.bioimageio.inference_time:
        speeds_sizes_times += (
            f"- **Inference time:** {model.config.bioimageio.inference_time}\n"
        )

    if model.config.bioimageio.memory_requirements_inference:
        speeds_sizes_times += f"- **Memory requirements:** {model.config.bioimageio.memory_requirements_inference}\n"

    model_arch_and_objective = "## Model Architecture and Objective\n\n"
    if (
        model.config.bioimageio.architecture_type
        or model.config.bioimageio.architecture_description
    ):
        model_arch_and_objective += (
            f"- **Architecture:** {model.config.bioimageio.architecture_type or ''}"
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

    io_desc, referenced_files, input_ids, output_ids = _get_io_description(model)
    predict_snippet_inputs = str(
        {input_id: "<path or tensor>" for input_id in input_ids}
    )
    model_arch_and_objective += io_desc

    hardware_requirements = "\n### Hardware Requirements\n"
    if model.config.bioimageio.memory_requirements_training is not None:
        hardware_requirements += f"- **Training:** GPU memory: {model.config.bioimageio.memory_requirements_training}\n"

    if model.config.bioimageio.memory_requirements_inference is not None:
        hardware_requirements += f"- **Inference:** GPU memory: {model.config.bioimageio.memory_requirements_inference}\n"

    hardware_requirements += f"- **Storage:** Model size: {model_size}\n"

    if model.license is None:
        license = "unknown"
        license_meta = "unknown"
    else:
        spdx_licenses = get_spdx_licenses()
        matches = [
            (entry["name"], entry["reference"])
            for entry in spdx_licenses["licenses"]
            if entry["licenseId"].lower() == model.license.lower()
        ]
        if matches:
            if len(matches) > 1:
                logger.warning(
                    "Multiple SPDX license matches found for '{}', using the first one.",
                    model.license,
                )
            name, reference = matches[0]
            license = f"[{name}]({reference})"
            license_meta = f"other\nlicense_name: {model.license.lower()}\nlicense_link: {reference}"
        else:
            if model.license.lower() in HF_KNOWN_LICENSES:
                license_meta = model.license.lower()
            else:
                license_meta = "other"

            license = model.license.lower()

    base_model = (
        f"\nbase_model: {model.parent.id[len('huggingface/') :]}"
        if model.parent is not None and model.parent.id.startswith("huggingface/")
        else ""
    )
    dataset_meta = (
        f"\ndataset: {model.training_data.id[len('huggingface/') :]}"
        if model.training_data is not None
        and model.training_data.id is not None
        and model.training_data.id.startswith("huggingface/")
        else ""
    )
    # TODO: add pipeline_tag to metadata
    readme = f"""---
license: {license_meta}
tags: {list({"biology"}.union(set(model.tags)))}
language: [en]
library_name: bioimageio{base_model}{dataset_meta}
---
# {model.name}

{model.description or ""}


# Table of Contents

- [Model Details](#model-details)
- [Uses](#uses)
- [Bias, Risks, and Limitations](#bias-risks-and-limitations)
- [How to Get Started with the Model](#how-to-get-started-with-the-model)
- [Training Details](#training-details){evaluation_toc_entry}{
        environmental_impact_toc_entry
    }
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

```python
from bioimageio.core import predict

output_sample = predict(
    "huggingface/{repo_id}/{model.version or "draft"}",
    inputs={predict_snippet_inputs},
)

output_tensor = output_sample.members["{
        output_ids[0] if output_ids else "<output_id>"
    }"]
xarray_dataarray = output_tensor.data
numpy_ndarray = output_tensor.data.to_numpy()
```

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

You can use "huggingface/{repo_id}/{
        model.version or "draft"
    }" as the resource identifier to load this model directly from the Hugging Face Hub using bioimageio.spec or bioimageio.core.

See [bioimageio.core documentation: Get started](https://bioimage-io.github.io/core-bioimage-io-python/latest/get-started) for instructions on how to load and run this model using the `bioimageio.core` Python package or the bioimageio CLI.

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
{environmental_impact}

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

    return readme, referenced_files
