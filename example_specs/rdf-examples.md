# Examples for describing the

### Describing applications
The RDF can be used to describe applications. To do so set the `type` field to `application`.\
For regular software package with a downloadable file, you can set `download_url` to the downloadable file, for example, you can upload the executable files as Github release, deposit it on Zenodo, or even generate a sharable url from Dropbox/Google Drive.\
For web application, set `source` to the url of the web application. Users can then click and redirect to your web application. However, simple integration will not support features such as opening dataset or models with your application.

It is recommended to build BioEngine Apps such that users can directly try and use them in bioimage.io. See [here](https://github.com/bioimage-io/bioimage.io/blob/main/docs/bioengine_apps/build-bioengine-apps.md) for more details.\
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
badges:
 - icon: https://imjoy.io/static/badge/launch-imjoy-badge.svg
   label: Launch ImJoy
   url: https://imjoy.io/#/app?plugin=https://kaibu.org/#/app
```
For more application examples, see the [manifest for ImJoy](https://github.com/imjoy-team/bioimage-io-models/blob/master/manifest.bioimage.io.yaml).

### Describing notebooks and scripts

Jupyter notebooks, Google Colab or other types of executable notebooks or scripts are considered as applications, therefore, you should use `type=application` and add additional tags. For example:
```
  - type: application
    id: Notebook_fnet_3D_ZeroCostDL4Mic
    name: Label-free Prediction - fnet - (3D) ZeroCostDL4Mic
    description: Paired image-to-image translation of 3D images. Label-free Prediction (fnet) is a neural network used to infer the features of cellular structures from brightfield or EM images without coloured labels. The network is trained using paired training images from the same field of view, imaged in a label-free (e.g. brightfield) and labelled condition (e.g. fluorescent protein). When trained, this allows the user to identify certain structures from brightfield images alone. The performance of fnet may depend significantly on the structure at hand. Note - visit the ZeroCostDL4Mic wiki to check the original publications this network is based on and make sure you cite these.
    cite:
      - text: "von Chamier, L., Laine, R.F., Jukkala, J. et al. Democratising deep learning for microscopy with ZeroCostDL4Mic. Nat Commun 12, 2276 (2021). https://doi.org/10.1038/s41467-021-22518-0"
        doi: https://doi.org/10.1038/s41467-021-22518-0

      - text: "Ounkomol, C., Seshamani, S., Maleckar, M.M. et al. Label-free prediction of three-dimensional fluorescence images from transmitted-light microscopy. Nat Methods 15, 917–920 (2018). https://doi.org/10.1038/s41592-018-0111-2"
        doi: https://doi.org/10.1038/s41592-018-0111-2

    authors:
      - Lucas von Chamier and the ZeroCostDL4Mic Team
    covers:
      - https://raw.githubusercontent.com/HenriquesLab/ZeroCostDL4Mic/master/BioimageModelZoo/Images/fnet_notebook.png

    badges:
      - label: Open in Colab
        icon: https://colab.research.google.com/assets/colab-badge.svg
        url: https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/fnet_3D_ZeroCostDL4Mic.ipynb
    documentation: https://raw.githubusercontent.com/HenriquesLab/ZeroCostDL4Mic/master/BioimageModelZoo/README.md
    tags: [colab, notebook, fnet, labelling, ZeroCostDL4Mic, 3D]
    download_url: https://raw.githubusercontent.com/HenriquesLab/ZeroCostDL4Mic/master/Colab_notebooks/fnet_3D_ZeroCostDL4Mic.ipynb
    git_repo: https://github.com/HenriquesLab/ZeroCostDL4Mic
    links:
      - Notebook Preview
      - Dataset_fnet_3D_ZeroCostDL4Mic
```


### Describing datasets and other types
The RDF allows for the description of datasets (type=`dataset`) and other potential resources, you can use set `source` and/or `download_url` to point to the resource, or use `attachments` to specify a list of associated files.

For examples, see entries `dataset`/`notebook` in the [ZeroCostDL4Mic](https://github.com/HenriquesLab/ZeroCostDL4Mic/blob/master/manifest.bioimage.io.yaml) collection.


### Describing models with the unspecific RDF(not recommended, use the Model RDF instead)
In general, it is discouraged to use the general RDF to describe AI models and we recommend to follow the [model RDF spec](#model-resource-description-file-specification) instead. However, in some cases, it is not possible to provide detailed fields defined in the [model RDF spec](#model-resource-description-file-specification), the general RDF can be used for discribing AI models.
To do that, you need to first set the `type` field to `model`.\
A basic integration would be simply provide a `download_url` to a zip file (for example, with the model weights, source code or executable binary file) hosted on Github releases, Dropbox, Google Drive etc. For example:
```yaml
download_url: https://zenodo.org/record/3446812/files/unet2d_weights.torch?download=1
```

If the model is available as a github repo, then provide the `git_repo` field:
```yaml
git_repo: https://github.com/my/model...
```

Here an example of a general RDF describing a model (not recommended):
https://github.com/CellProfiling/HPA-model-zoo/blob/2f668d87defddc6c7cd156259a8be4146b665e72/manifest.bioimage.io.yaml#L33-L59

