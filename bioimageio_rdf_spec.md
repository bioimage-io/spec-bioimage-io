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
