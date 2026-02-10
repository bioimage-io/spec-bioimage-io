from pathlib import Path

import pytest

from bioimageio.spec import load_model_description
from bioimageio.spec.model.v0_5 import (
    DatasetId,
    Evaluation,
    HttpUrl,
    LinkedModel,
    ModelId,
    OnnxWeightsDescr,
    Version,
    WeightsDescr,
)


@pytest.mark.parametrize("fill_meta", (True, False))
def test_hf(unet2d_path: Path, fill_meta: bool, tmp_path: Path):
    from bioimageio.spec._hf import push_to_hub

    model = load_model_description(unet2d_path, format_version="latest")
    model.id = ModelId("unet2d_nuclei_broad")

    if fill_meta:
        model.license = "AAL"
        model.parent = LinkedModel(
            id=ModelId("unet2d_nuclei_broad_v0.1"),
            version=Version("0.1"),
        )
        model.config.bioimageio.architecture_type = "Unet"
        model.config.bioimageio.architecture_description = "A 2D Unet"
        model.config.bioimageio.modality = "fluorescence microscopy"
        model.config.bioimageio.target_structure = ["nuclei"]
        model.config.bioimageio.task = "segmentation"
        model.config.bioimageio.environmental_impact.hardware_type = "GTX 2080 Ti"
        model.config.bioimageio.environmental_impact.hours_used = 10
        model.config.bioimageio.environmental_impact.compute_region = "Germany"
        model.config.bioimageio.environmental_impact.co2_emitted = 0.54
        model.config.bioimageio.environmental_impact.cloud_provider = "EMBL Heidelberg"
        model.config.bioimageio.funded_by = "EMBL"
        model.config.bioimageio.new_version = ModelId(
            "huggingface/bioimageio/not_a_real_model"
        )
        model.config.bioimageio.out_of_scope_use = (
            "for testing only. do not use this model for real applications."
        )
        model.config.bioimageio.model_parameter_count = 123456
        model.config.bioimageio.training.training_epochs = 100
        model.config.bioimageio.training.training_batch_size = 10
        model.config.bioimageio.training.initial_learning_rate = 1e-4
        model.config.bioimageio.training.learning_rate_schedule = "ausgefuxt"
        model.config.bioimageio.training.loss_function = "dice_loss"
        model.config.bioimageio.training.loss_function_kwargs = {"smooth": 1e-5}
        model.config.bioimageio.training.optimizer = "Adam"
        model.config.bioimageio.training.optimizer_kwargs = {"weight_decay": 1e-5}
        model.config.bioimageio.training.regularization = "drop-out"
        model.config.bioimageio.training.training_duration = 1
        model.config.bioimageio.training.training_preprocessing = (
            "some preprocessing description"
        )
        model.config.bioimageio.inference_time = "super fast"
        model.config.bioimageio.memory_requirements_inference = "not much"
        model.config.bioimageio.memory_requirements_training = "also not much"
        model.config.bioimageio.evaluations.append(
            Evaluation(
                dataset_id=DatasetId("my_test_set"),
                dataset_source=HttpUrl("https://example.com"),
                dataset_role="test",
                sample_count=3,
                evaluation_factors=["nuclei", "membrane"],
                evaluation_factors_long=["cell nuclei", "cell membrane"],
                metrics=["DICE", "IoU"],
                metrics_long=["dice score", "IoU score"],
                results=[[1, 2], [3, 4]],
                results_summary="dummy summary",
            ),
        )
        model.config.bioimageio.evaluations.append(
            Evaluation(
                model_id=model.id,
                dataset_id=DatasetId("my_test_set"),
                dataset_source=HttpUrl("https://example.com"),
                dataset_role="independent",
                sample_count=3,
                evaluation_factors=["nuclei", "membrane"],
                evaluation_factors_long=["cell nuclei", "cell membrane"],
                metrics=["DICE", "IoU"],
                metrics_long=["dice score", "IoU score"],
                results=[[1, 2], [3, 4]],
                results_summary="dummy summary",
            ),
        )
    else:
        model.authors = []
        model.cite = []
        model.license = None
        model.weights = WeightsDescr(
            onnx=OnnxWeightsDescr(
                source=HttpUrl("https://example.com"),
                opset_version=11,
                comment="fake example weights",
            )
        )  # create invalid empty weights descr

    push_to_hub(model, "thefynnbe", prep_only_no_upload=True, prep_dir=tmp_path)

    if not fill_meta:
        with pytest.raises(ValueError):  # non-empty output dir
            push_to_hub(model, "thefynnbe", prep_only_no_upload=True, prep_dir=tmp_path)

        model.id = None
        with pytest.raises(ValueError):
            push_to_hub(model, "thefynnbe", prep_only_no_upload=True)
