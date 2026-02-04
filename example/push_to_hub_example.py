"""Example script I used to create https://huggingface.co/thefynnbe/ambitious-sloth"""

from loguru import logger

from bioimageio.spec import load_model_description
from bioimageio.spec._hf import push_to_hub

logger.enable("bioimageio")

# loading from bioimage.io
my_model = load_model_description(
    "ambitious-sloth", format_version="latest", perform_io_checks=False
)
print("loaded", my_model.id)


# add huggingface used in the huggingface model card
my_model.config.bioimageio.architecture_type = "HyLFM-Net"
my_model.config.bioimageio.architecture_description = (
    "A convolutional neural network for light-field microscopy volume reconstruction."
)
my_model.config.bioimageio.modality = "fluorescence microscopy"
my_model.config.bioimageio.target_structure = ["medaka larvae heart"]
my_model.config.bioimageio.task = "volume reconstruction"
my_model.config.bioimageio.environmental_impact.hardware_type = "GTX 2080 Ti"
my_model.config.bioimageio.environmental_impact.hours_used = 10
my_model.config.bioimageio.environmental_impact.compute_region = "Germany"
my_model.config.bioimageio.environmental_impact.co2_emitted = 0.54
my_model.config.bioimageio.environmental_impact.cloud_provider = "EMBL Heidelberg"

# set version to None to upload a draft
# my_model.version = None

push_to_hub(my_model, "thefynnbe")
