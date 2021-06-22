## Describing AI models

In general, it is discouraged to use the generic RDF to describe AI models and we recommend to follow the [model RDF spec](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/bioimageio_model_spec.md) instead. However, in some cases, it is not possible to provide detailed fields defined in the [model RDF spec](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/bioimageio_model_spec.md), the generic RDF can be used for discribing AI models.

To do that, you need to first set the `type` filed to `model`.

A basic integration would be simply provide a `download_url` to a zip file (for example, with the model weights, source code or executable binary file) hosted on Github releases, Dropbox, Google Drive etc. For example: 
```yaml
download_url: https://zenodo.org/record/3446812/files/unet2d_weights.torch?download=1
```

If the model is available as a github repo, then provide the `git_repo` field:
```yaml
git_repo: https://github.com/my/model...
```

See an example here:
```yaml
id: HPA-bestfitting
name: HPA-bestfitting
tags:
  - classification
  - densenet-121
  - inception-v3
  - resnet-34
  - resnet-50
framework: pytorch
authors:
  - Shubin Dai
license: MIT
cite: null
git_repo: >-
  https://github.com/CellProfiling/HPA-competition-solutions/tree/master/bestfitting
description: >-
  A CNN model using focal loss and image augmentation, optimized with Adam
  optimizer.
documentation: >-
  https://raw.githubusercontent.com/CellProfiling/HPA-competition-solutions/master/bestfitting/README.md
badges:
  - label: HPA Competition
    ext: 1st
    url: https://www.kaggle.com/c/human-protein-atlas-image-classification/leaderboard
covers:
  - https://raw.githubusercontent.com/CellProfiling/HPA-model-zoo/master/hpa_challenge_header.png
  - https://raw.githubusercontent.com/CellProfiling/HPA-competition-solutions/master/bestfitting/src/bestfitting-densenet-diagram.png
```

## Describing applications
You need to first set the `type` filed to `application`.

For regular software package with a downloadable file, you can set `download_url` to the downloadable file, for example, you can upload the executable files as Github release, deposit it on Zenodo, or even generate a sharable url from Dropbox/Google Drive.

For web application, set `source` to the url of the web application. Users can then click and redirect to your web application. However, simple integration will not support features such as opening dataset or models with your application.

It is recommended to build BioEngine Apps such that users can directly try and use them in BioImage.IO. See [here](https://github.com/bioimage-io/bioimage.io/blob/master/docs/build-bioengine-apps.md) for more details.


Below is an example for [Kaibu](https://kaibu.org), which is a BioEngine/ImJoy compatible web application:
```yaml
id: kaibu
name: Kaibu
description: Kaibu--a web application for visualizing and annotating multi-dimensional images
covers:
 # use the `raw` url if you store the image on github
 - https://raw.githubusercontent.com/imjoy-team/kaibu/master/public/static/img/kaibu-screenshot-1.png

# source url to kaibu.org
source: https://kaibu.org
# add custom badge
badge:
 - icon: https://imjoy.io/static/badge/launch-imjoy-badge.svg
   label: Launch ImJoy
   url: https://imjoy.io/#/app?plugin=https://kaibu.org/#/app
```

For more examples, see the [manifest for ImJoy](https://github.com/imjoy-team/bioimage-io-models/blob/master/manifest.bioimage.io.yaml).

## Describing datasets, notebooks and other types
Similarily, for datasets (type=`dataset`), notebooks (type=`notebook`) and other potential resources, you can use set `source` and/or `download_url` to point to the resource, or use `attachments` to specify a list of associated files.

For example, this is a RDF for notebooks:
```yaml
id: unet-2d
name: U-net (2D)
description: U-Net for segmentation
cite:
  text: "Falk, T., Mai, D., Bensch, R. et al. U-Net: deep learning for cell counting, detection, and morphometry. Nat Methods 16, 67–70 (2019)."
  doi: https://doi.org/10.1038/s41592-018-0261-2
authors:
  - ZeroCostDL4Mic Team
covers:
  - https://raw.githubusercontent.com/oeway/ZeroCostDL4Mic/master/Wiki_files/wiki%20unet.png
badges:
  - label: Open in Colab
    icon: https://colab.research.google.com/assets/colab-badge.svg
    url: https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb
documentation: null
tags: [UNet, segmentation, ZeroCostDL4Mic]
source: https://github.com/HenriquesLab/ZeroCostDL4Mic/raw/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb
```

For more examples, see the [ZeroCostDL4Mic](https://github.com/HenriquesLab/ZeroCostDL4Mic/blob/master/manifest.bioimage.io.yaml) repo.

## Link between resource items

You can use `links` which is a list of `id` to other resource items, for example, if you want to associate an applicaiton with a model, you can set the links field of the models like the following:
```yaml
application:
  - id: HPA-Classification
    source: https://raw.githubusercontent.com/bioimage-io/tfjs-bioimage-io/master/apps/HPA-Classification.imjoy.html

model:
  - id: HPAShuffleNetV2
    source: https://raw.githubusercontent.com/bioimage-io/tfjs-bioimage-io/master/models/HPAShuffleNetV2/HPAShuffleNetV2.model.yaml
    links:
      - HPA-Classification
```

## Add custom badges
You can add custom badges to each item to support, e.g.: "Launch Binder", "Open in Colab", "Launch ImJoy" etc.

Here is an example:
```yaml
    badges:
      - label: Open in Colab
        icon: https://colab.research.google.com/assets/colab-badge.svg
        url: https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb
```

## Hosting the file
It is recommended to host the resource description file on one of the public git repository website, including Github, Gitlab, Bitbucket, or Gist. A link can be submitted to BioImage.IO so we can keep track of the changes later.
