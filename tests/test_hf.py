from pathlib import Path

import pytest

from bioimageio.spec import load_model_description
from bioimageio.spec.model.v0_5 import Evaluation, ModelId


@pytest.mark.parametrize("fill_meta", (True, False))
def test_hf(unet2d_path: Path, fill_meta: bool):
    from bioimageio.spec._hf import push_to_hub

    my_model = load_model_description(unet2d_path, format_version="latest")
    my_model.id = ModelId("unet2d_nuclei_broad")

    if fill_meta:
        my_model.config.bioimageio.architecture_type = "Unet"
        my_model.config.bioimageio.architecture_description = "A 2D Unet"
        my_model.config.bioimageio.modality = "fluorescence microscopy"
        my_model.config.bioimageio.target_structure = ["nuclei"]
        my_model.config.bioimageio.task = "segmentation"
        my_model.config.bioimageio.environmental_impact.hardware_type = "GTX 2080 Ti"
        my_model.config.bioimageio.environmental_impact.hours_used = 10
        my_model.config.bioimageio.environmental_impact.compute_region = "Germany"
        my_model.config.bioimageio.environmental_impact.co2_emitted = 0.54
        my_model.config.bioimageio.environmental_impact.cloud_provider = (
            "EMBL Heidelberg"
        )
        my_model.config.bioimageio.funded_by = "EMBL"
        my_model.config.bioimageio.new_version = (
            "huggingface/bioimageio/not_a_real_model"
        )
        my_model.config.bioimageio.out_of_scope_use = (
            "for testing only. do not use this model for real applications."
        )
        my_model.config.bioimageio.model_parameter_count = 123456
        my_model.config.bioimageio.training.training_epochs = 100
        my_model.config.bioimageio.training.training_batch_size = 10
        my_model.config.bioimageio.training.initial_learning_rate = 1e-4
        my_model.config.bioimageio.training.learning_rate_schedule = "ausgefuxt"
        my_model.config.bioimageio.training.loss_function = "dice_loss"
        my_model.config.bioimageio.training.loss_function_kwargs = {"smooth": 1e-5}
        my_model.config.bioimageio.training.optimizer = "Adam"
        my_model.config.bioimageio.training.optimizer_kwargs = {"weight_decay": 1e-5}
        my_model.config.bioimageio.training.regularization = "drop-out"
        my_model.config.bioimageio.training.training_duration = 1
        my_model.config.bioimageio.inference_time = "super fast"
        my_model.config.bioimageio.memory_requirements_inference = "not much"
        my_model.config.bioimageio.memory_requirements_training = "also not much"
        my_model.config.bioimageio.evaluations.append(
            Evaluation(
                dataset_id="my_test_set",
                dataset_source="https://example.com",
                dataset_role="test",
                sample_count=3,
                evaluation_factors=["nuclei", "membrane"],
                evaluation_factors_long=["cell nuclei", "cell membrane"],
                metrics=["DICE", "IoU"],
                metrics_long=["dice score", "IoU score"],
                results=[[1, 2], [3, 4]],
                results_summary="dummy summary",
            )
        )

    push_to_hub(my_model, "thefynnbe", prep_only_no_upload=True)
