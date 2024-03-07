import datetime
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

import pooch
import pytest

from bioimageio.spec._description import DISCOVER, LATEST
from bioimageio.spec._internal.types import FormatVersionPlaceholder
from tests.utils import ParameterSet, check_bioimageio_yaml

BASE_URL = "https://bioimage-io.github.io/collection-bioimage-io/"
RDF_BASE_URL = BASE_URL + "rdfs/"
WEEK = f"{datetime.datetime.now().year}week{datetime.datetime.now().isocalendar()[1]}"
CACHE_PATH = Path(__file__).parent / "cache" / WEEK


KNOWN_INVALID = {
    "10.5281/zenodo.5749843/5888237/rdf.yaml",
    "10.5281/zenodo.5910163/5942853/rdf.yaml",
    "10.5281/zenodo.5910854/6539073/rdf.yaml",
    "10.5281/zenodo.5914248/6514622/rdf.yaml",
    "10.5281/zenodo.6559929/6559930/rdf.yaml",
    "10.5281/zenodo.7614645/7642674/rdf.yaml",
    "biapy/biapy/latest/rdf.yaml",
    "biapy/notebook_classification_2d/latest/rdf.yaml",
    "biapy/Notebook_semantic_segmentation_3d/latest/rdf.yaml",
    "deepimagej/deepimagej/latest/rdf.yaml",
    "deepimagej/DeepSTORMZeroCostDL4Mic/latest/rdf.yaml",
    "deepimagej/Mt3VirtualStaining/latest/rdf.yaml",
    "deepimagej/MU-Lux_CTC_PhC-C2DL-PSC/latest/rdf.yaml",
    "deepimagej/SkinLesionClassification/latest/rdf.yaml",
    "deepimagej/SMLMDensityMapEstimationDEFCoN/latest/rdf.yaml",
    "deepimagej/UNet2DGlioblastomaSegmentation/latest/rdf.yaml",
    "deepimagej/WidefieldDapiSuperResolution/latest/rdf.yaml",
    "deepimagej/WidefieldFitcSuperResolution/latest/rdf.yaml",
    "deepimagej/WidefieldTxredSuperResolution/latest/rdf.yaml",
    "fiji/N2VSEMDemo/latest/rdf.yaml",
    "ilastik/mitoem_segmentation_challenge/latest/rdf.yaml",
    "imjoy/LuCa-7color/latest/rdf.yaml",
    "zero/Dataset_CARE_2D_coli_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_fnet_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_Noise2Void_2D_subtilis_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_SplineDist_2D_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_StarDist_2D_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_U-Net_2D_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_U-Net_2D_multilabel_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_YOLOv2_antibiotic_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_YOLOv2_coli_DeepBacs/latest/rdf.yaml",
    "zero/Notebook_CycleGAN_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_DecoNoising_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_Detectron2_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_DRMIME_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_EmbedSeg_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_MaskRCNN_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_pix2pix_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_RetinaNet_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_StarDist_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_U-Net_2D_multilabel_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_U-Net_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_U-Net_3D_ZeroCostDL4Mic/latest/rdf.yaml",
}
KNOWN_INVALID_AS_LATEST = {
    "10.5281/zenodo.5749843/5888237/rdf.yaml",
    "10.5281/zenodo.5874841/6630266/rdf.yaml",
    "10.5281/zenodo.5910163/5942853/rdf.yaml",
    "10.5281/zenodo.5914248/6514622/rdf.yaml",
    "10.5281/zenodo.5914248/8186255/rdf.yaml",
    "10.5281/zenodo.6383429/7774505/rdf.yaml",
    "10.5281/zenodo.6406803/6406804/rdf.yaml",
    "10.5281/zenodo.6559474/6559475/rdf.yaml",
    "10.5281/zenodo.6559929/6559930/rdf.yaml",
    "10.5281/zenodo.6811491/6811492/rdf.yaml",
    "10.5281/zenodo.6865412/6919253/rdf.yaml",
    "10.5281/zenodo.7380171/7405349/rdf.yaml",
    "10.5281/zenodo.7614645/7642674/rdf.yaml",
    "10.5281/zenodo.8401064/8429203/rdf.yaml",
    "10.5281/zenodo.8421755/8432366/rdf.yaml",
    "biapy/biapy/latest/rdf.yaml",
    "biapy/notebook_classification_2d/latest/rdf.yaml",
    "biapy/notebook_classification_3d/latest/rdf.yaml",
    "biapy/notebook_denoising_2d/latest/rdf.yaml",
    "biapy/notebook_denoising_3d/latest/rdf.yaml",
    "biapy/notebook_detection_2d/latest/rdf.yaml",
    "biapy/notebook_detection_3d/latest/rdf.yaml",
    "biapy/notebook_instance_segmentation_2d/latest/rdf.yaml",
    "biapy/notebook_instance_segmentation_3d/latest/rdf.yaml",
    "biapy/notebook_self_supervision_2d/latest/rdf.yaml",
    "biapy/notebook_self_supervision_3d/latest/rdf.yaml",
    "biapy/notebook_semantic_segmentation_2d/latest/rdf.yaml",
    "biapy/Notebook_semantic_segmentation_3d/latest/rdf.yaml",
    "biapy/notebook_super_resolution_2d/latest/rdf.yaml",
    "biapy/notebook_super_resolution_3d/latest/rdf.yaml",
    "bioimageio/stardist/latest/rdf.yaml",
    "deepimagej/deepimagej-web/latest/rdf.yaml",
    "deepimagej/deepimagej/latest/rdf.yaml",
    "deepimagej/DeepSTORMZeroCostDL4Mic/latest/rdf.yaml",
    "deepimagej/DeepSTORMZeroCostDL4Mic/latest/rdf.yaml",
    "deepimagej/DeepSTORMZeroCostDL4Mic/latest/rdf.yaml",
    "deepimagej/DeepSTORMZeroCostDL4Mic/latest/rdf.yaml",
    "deepimagej/EVsTEMsegmentationFRUNet/latest/rdf.yaml",
    "deepimagej/MoNuSeg_digital_pathology_miccai2018/latest/rdf.yaml",
    "deepimagej/Mt3VirtualStaining/latest/rdf.yaml",
    "deepimagej/MU-Lux_CTC_PhC-C2DL-PSC/latest/rdf.yaml",
    "deepimagej/SkinLesionClassification/latest/rdf.yaml",
    "deepimagej/smlm-deepimagej/latest/rdf.yaml",
    "deepimagej/SMLMDensityMapEstimationDEFCoN/latest/rdf.yaml",
    "deepimagej/unet-pancreaticcellsegmentation/latest/rdf.yaml",
    "deepimagej/UNet2DGlioblastomaSegmentation/latest/rdf.yaml",
    "deepimagej/WidefieldDapiSuperResolution/latest/rdf.yaml",
    "deepimagej/WidefieldFitcSuperResolution/latest/rdf.yaml",
    "deepimagej/WidefieldTxredSuperResolution/latest/rdf.yaml",
    "dl4miceverywhere/DL4MicEverywhere/latest/rdf.yaml",
    "dl4miceverywhere/Notebook_bioimageio_pytorch/latest/rdf.yaml",
    "dl4miceverywhere/Notebook_bioimageio_tensorflow/latest/rdf.yaml",
    "fiji/Fiji/latest/rdf.yaml",
    "hpa/HPA-Classification/latest/rdf.yaml",
    "hpa/hpa-kaggle-2021-dataset/latest/rdf.yaml",
    "icy/icy/latest/rdf.yaml",
    "ilastik/arabidopsis_tissue_atlas/latest/rdf.yaml",
    "ilastik/cremi_training_data/latest/rdf.yaml",
    "ilastik/ilastik/latest/rdf.yaml",
    "ilastik/isbi2012_neuron_segmentation_challenge/latest/rdf.yaml",
    "ilastik/mitoem_segmentation_challenge/latest/rdf.yaml",
    "ilastik/mws-segmentation/latest/rdf.yaml",
    "imjoy/BioImageIO-Packager/latest/rdf.yaml",
    "imjoy/GenericBioEngineApp/latest/rdf.yaml",
    "imjoy/HPA-Single-Cell/latest/rdf.yaml",
    "imjoy/ImageJ.JS/latest/rdf.yaml",
    "imjoy/ImJoy/latest/rdf.yaml",
    "imjoy/LuCa-7color/latest/rdf.yaml",
    "imjoy/vizarr/latest/rdf.yaml",
    "qupath/QuPath/latest/rdf.yaml",
    "stardist/stardist/latest/rdf.yaml",
    "zero/Dataset_CARE_2D_coli_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_CARE_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_CARE_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_CycleGAN_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_Deep-STORM_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_fnet_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_fnet_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_Noise2Void_2D_subtilis_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_Noise2Void_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_Noise2Void_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_Noisy_Nuclei_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_pix2pix_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_SplineDist_2D_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_StarDist_2D_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_StarDist_2D_ZeroCostDL4Mic_2D/latest/rdf.yaml",
    "zero/Dataset_StarDist_brightfield_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_StarDist_brightfield2_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_StarDist_Fluo_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_StarDist_fluo2_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Dataset_U-Net_2D_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_U-Net_2D_multilabel_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_YOLOv2_antibiotic_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_YOLOv2_coli_DeepBacs/latest/rdf.yaml",
    "zero/Dataset_YOLOv2_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook Preview/latest/rdf.yaml",
    "zero/Notebook_Augmentor_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_CARE_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_CARE_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_Cellpose_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_CycleGAN_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_CycleGAN_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_DecoNoising_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_DecoNoising_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_Deep-STORM_2D_ZeroCostDL4Mic_DeepImageJ/latest/rdf.yaml",
    "zero/Notebook_Deep-STORM_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_DenoiSeg_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_Detectron2_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_Detectron2_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_DFCAN_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_DRMIME_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_DRMIME_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_EmbedSeg_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_EmbedSeg_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_fnet_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_fnet_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_Interactive_Segmentation_Kaibu_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_MaskRCNN_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_MaskRCNN_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_Noise2Void_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_Noise2Void_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_pix2pix_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_pix2pix_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/notebook_preview/latest/rdf.yaml-latest",
    "zero/notebook_preview/latest/rdf.yaml",
    "zero/Notebook_Quality_Control_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_RCAN_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_RetinaNet_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_RetinaNet_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_SplineDist_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_StarDist_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_StarDist_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_StarDist_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_U-Net_2D_multilabel_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_U-Net_2D_multilabel_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_U-Net_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_U-Net_2D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_U-Net_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_U-Net_3D_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/Notebook_YOLOv2_ZeroCostDL4Mic/latest/rdf.yaml",
    "zero/WGAN_ZeroCostDL4Mic.ipynb/latest/rdf.yaml",
}
EXCLUDE_FIELDS_FROM_ROUNDTRIP = {
    "10.5281/zenodo.6348728/6348729/rdf.yaml": {"cite"},  # doi prefixed
    "10.5281/zenodo.6406803/6406804/rdf.yaml": {"cite"},  # doi prefixed
    "10.5281/zenodo.6338614/6338615/rdf.yaml": {"cite"},  # doi prefixed
    "10.5281/zenodo.5914248/8186255/rdf.yaml": {"cite"},  # doi prefixed
    "10.5281/zenodo.7274275/8123818/rdf.yaml": {"inputs", "parent"},
    "10.5281/zenodo.7315440/7315441/rdf.yaml": {
        "cite",
        "maintainers",
        "weights",
    },  # weights.onnx: missing sh256, cite[0].doi: prefix
    "10.5281/zenodo.7772662/7781091/rdf.yaml": {
        "weights"
    },  # upper to lower case sha256
    "10.5281/zenodo.6028097/6028098/rdf.yaml": {
        "authors",  # gh username "Constantin Pape" -> contantinpape
        "maintainers",
    },
    "zero/Notebook Preview/latest/rdf.yaml": {"rdf_source"},  # ' ' -> %20
}


def yield_bioimageio_yaml_urls() -> Iterable[ParameterSet]:
    collection_path: Any = pooch.retrieve(BASE_URL + "collection.json", None)
    with Path(collection_path).open(encoding="utf-8") as f:
        collection_data = json.load(f)["collection"]

    collection_registry: Dict[str, None] = {
        entry["rdf_source"].replace(RDF_BASE_URL, ""): None for entry in collection_data
    }

    for rdf in collection_registry:
        descr_url = RDF_BASE_URL + rdf
        key = rdf
        yield pytest.param(descr_url, key, id=key)


@pytest.mark.parametrize("format_version", [DISCOVER, LATEST])
@pytest.mark.parametrize("descr_url,key", list(yield_bioimageio_yaml_urls()))
def test_rdf(
    descr_url: Path,
    key: str,
    format_version: FormatVersionPlaceholder,
    bioimageio_json_schema: Mapping[Any, Any],
):
    if (
        format_version == DISCOVER
        and key in KNOWN_INVALID
        or format_version == LATEST
        and key in KNOWN_INVALID_AS_LATEST
    ):
        pytest.skip("known failure")

    check_bioimageio_yaml(
        descr_url,
        as_latest=format_version == LATEST,
        exclude_fields_from_roundtrip=EXCLUDE_FIELDS_FROM_ROUNDTRIP.get(key, set()),
        bioimageio_json_schema=bioimageio_json_schema,
        perform_io_checks=False,
    )
