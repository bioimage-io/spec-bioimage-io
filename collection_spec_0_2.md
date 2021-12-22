# BioImage.IO Collection Resource Description File Specification 0.2.1
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing collections of other resources.
These fields are typically stored in YAML files which we call Collection Resource Description Files or `collection RDF`.

The collection RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.

* <a id="format_version"></a>`format_version` _String_ Version of the BioImage.IO Resource Description File Specification used.The current general format version described here is 0.2.1. Note: The general RDF format is not to be confused with specialized RDF format like the Model RDF format.
* <a id="authors"></a>`authors` _List\[Author\]_ A list of authors. The authors are the creators of the specifications and the primary points of contact.
  1. _Author_   is a Dict with the following keys:
  * <a id="authors:affiliation"></a>`affiliation` _optional String_ Affiliation.
  * <a id="authors:email"></a>`email` _optional Email_ 
  * <a id="authors:github_user"></a>`github_user` _optional String_ GitHub user name.
  * <a id="authors:name"></a>`name` _optional String_ Full name.
  * <a id="authors:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
* <a id="cite"></a>`cite` _List\[CiteEntry\]_ A list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used.
  1. _CiteEntry_   is a Dict with the following keys:
  * <a id="cite:text"></a>`text` _String_ 
  * <a id="cite:doi"></a>`doi` _optional* String_ 
  * <a id="cite:url"></a>`url` _optional* String_ 
* <a id="description"></a>`description` _String_ A string containing a brief description.
* <a id="documentation"></a>`documentation` _Union\[URL→URI | RelativeLocalPath→Path\]_ URL or relative path to markdown file with additional documentation. For markdown files the recommended documentation file name is `README.md`.
  1. _optional URL→URI_ 
  1. _optional RelativeLocalPath→Path_ 
* <a id="name"></a>`name` _String_ name of the resource, a human-friendly name
* <a id="tags"></a>`tags` _List\[String\]_ A list of tags.
* <a id="type"></a>`type` _String_ 
* <a id="application"></a>`application` _optional List\[Union\[CollectionEntry | RDF\]\]_ 
  1. _optional Union\[CollectionEntry | RDF\]_ 
  1. _CollectionEntry_   is a Dict with the following keys:
  * <a id="application:id_"></a>`id_` _String_ 
  * <a id="application:source"></a>`source` _URL→URI_ 
  1. _RDF_ # BioImage.IO Resource Description File Specification 0.2.1
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks. 
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by 
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be 
specified.
 RDF is a Dict with the following keys:# BioImage.IO Resource Description File Specification 0.2.1
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks. 
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by 
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be 
specified.

  * <a id="application:format_version"></a>`format_version` _String_ Version of the BioImage.IO Resource Description File Specification used.The current general format version described here is 0.2.1. Note: The general RDF format is not to be confused with specialized RDF format like the Model RDF format.
  * <a id="application:authors"></a>`authors` _List\[Author\]_ A list of authors. The authors are the creators of the specifications and the primary points of contact.
    1. _Author_   is a Dict with the following keys:
    * <a id="application:authors:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="application:authors:email"></a>`email` _optional Email_ 
    * <a id="application:authors:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="application:authors:name"></a>`name` _optional String_ Full name.
    * <a id="application:authors:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="application:cite"></a>`cite` _List\[CiteEntry\]_ A list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used.
    1. _CiteEntry_   is a Dict with the following keys:
    * <a id="application:cite:text"></a>`text` _String_ 
    * <a id="application:cite:doi"></a>`doi` _optional* String_ 
    * <a id="application:cite:url"></a>`url` _optional* String_ 
  * <a id="application:description"></a>`description` _String_ A string containing a brief description.
  * <a id="application:documentation"></a>`documentation` _Union\[URL→URI | RelativeLocalPath→Path\]_ URL or relative path to markdown file with additional documentation. For markdown files the recommended documentation file name is `README.md`.
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="application:name"></a>`name` _String_ name of the resource, a human-friendly name
  * <a id="application:tags"></a>`tags` _List\[String\]_ A list of tags.
  * <a id="application:type"></a>`type` _String_ 
  * <a id="application:attachments"></a>`attachments` _Attachments_ Attachments. Additional, unknown keys are allowed. Attachments is a Dict with the following keys:
    * <a id="application:attachments:files"></a>`files` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ File attachments; included when packaging the resource.
      1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
      1. _optional URI→String_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="application:badges"></a>`badges` _optional List\[Badge\]_ a list of badges
    1. _Badge_ Custom badge Badge is a Dict with the following keys:Custom badge
    * <a id="application:badges:label"></a>`label` _String_ e.g. 'Open in Colab'
    * <a id="application:badges:icon"></a>`icon` _optional String_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
    * <a id="application:badges:url"></a>`url` _optional Union\[URL→URI | RelativeLocalPath→Path\]_ e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'
      1. _optional URL→URI_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="application:config"></a>`config` _optional YamlDict→Dict\[Any, Any\]_ 
  * <a id="application:covers"></a>`covers` _optional List\[Union\[URL→URI | RelativeLocalPath→Path\]\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
    1. _optional Union\[URL→URI | RelativeLocalPath→Path\]_ 
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="application:download_url"></a>`download_url` _optional URL→URI_ recommended url to the zipped file if applicable
  * <a id="application:git_repo"></a>`git_repo` _optional URL→URI_ A url to the git repository, e.g. to Github or Gitlab.
  * <a id="application:icon"></a>`icon` _optional String_ an icon for the resource
  * <a id="application:license"></a>`license` _optional String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
  * <a id="application:links"></a>`links` _optional List\[String\]_ links to other bioimage.io resources
  * <a id="application:maintainers"></a>`maintainers` _optional List\[Maintainer\]_ Maintainers of this resource.
    1. _Maintainer_   is a Dict with the following keys:
    * <a id="application:maintainers:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="application:maintainers:email"></a>`email` _optional Email_ 
    * <a id="application:maintainers:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="application:maintainers:name"></a>`name` _optional String_ Full name.
    * <a id="application:maintainers:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="application:source"></a>`source` _optional Union\[URI→String | RelativeLocalPath→Path\]_ url or local relative path to the source of the resource
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="application:version"></a>`version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
* <a id="attachments"></a>`attachments` _Attachments_ Attachments. Additional, unknown keys are allowed. Attachments is a Dict with the following keys:
  * <a id="attachments:files"></a>`files` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ File attachments; included when packaging the resource.
    1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
* <a id="badges"></a>`badges` _optional List\[Badge\]_ a list of badges
  1. _Badge_ Custom badge Badge is a Dict with the following keys:Custom badge
  * <a id="badges:label"></a>`label` _String_ e.g. 'Open in Colab'
  * <a id="badges:icon"></a>`icon` _optional String_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
  * <a id="badges:url"></a>`url` _optional Union\[URL→URI | RelativeLocalPath→Path\]_ e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
* <a id="config"></a>`config` _optional YamlDict→Dict\[Any, Any\]_ 
* <a id="covers"></a>`covers` _optional List\[Union\[URL→URI | RelativeLocalPath→Path\]\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
  1. _optional Union\[URL→URI | RelativeLocalPath→Path\]_ 
  1. _optional URL→URI_ 
  1. _optional RelativeLocalPath→Path_ 
* <a id="dataset"></a>`dataset` _optional List\[Union\[CollectionEntry | RDF\]\]_ 
  1. _optional Union\[CollectionEntry | RDF\]_ 
  1. _CollectionEntry_   is a Dict with the following keys:
  * <a id="dataset:id_"></a>`id_` _String_ 
  * <a id="dataset:source"></a>`source` _URL→URI_ 
  1. _RDF_ # BioImage.IO Resource Description File Specification 0.2.1
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks. 
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by 
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be 
specified.
 RDF is a Dict with the following keys:# BioImage.IO Resource Description File Specification 0.2.1
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks. 
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by 
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be 
specified.

  * <a id="dataset:format_version"></a>`format_version` _String_ Version of the BioImage.IO Resource Description File Specification used.The current general format version described here is 0.2.1. Note: The general RDF format is not to be confused with specialized RDF format like the Model RDF format.
  * <a id="dataset:authors"></a>`authors` _List\[Author\]_ A list of authors. The authors are the creators of the specifications and the primary points of contact.
    1. _Author_   is a Dict with the following keys:
    * <a id="dataset:authors:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="dataset:authors:email"></a>`email` _optional Email_ 
    * <a id="dataset:authors:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="dataset:authors:name"></a>`name` _optional String_ Full name.
    * <a id="dataset:authors:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="dataset:cite"></a>`cite` _List\[CiteEntry\]_ A list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used.
    1. _CiteEntry_   is a Dict with the following keys:
    * <a id="dataset:cite:text"></a>`text` _String_ 
    * <a id="dataset:cite:doi"></a>`doi` _optional* String_ 
    * <a id="dataset:cite:url"></a>`url` _optional* String_ 
  * <a id="dataset:description"></a>`description` _String_ A string containing a brief description.
  * <a id="dataset:documentation"></a>`documentation` _Union\[URL→URI | RelativeLocalPath→Path\]_ URL or relative path to markdown file with additional documentation. For markdown files the recommended documentation file name is `README.md`.
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="dataset:name"></a>`name` _String_ name of the resource, a human-friendly name
  * <a id="dataset:tags"></a>`tags` _List\[String\]_ A list of tags.
  * <a id="dataset:type"></a>`type` _String_ 
  * <a id="dataset:attachments"></a>`attachments` _Attachments_ Attachments. Additional, unknown keys are allowed. Attachments is a Dict with the following keys:
    * <a id="dataset:attachments:files"></a>`files` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ File attachments; included when packaging the resource.
      1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
      1. _optional URI→String_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="dataset:badges"></a>`badges` _optional List\[Badge\]_ a list of badges
    1. _Badge_ Custom badge Badge is a Dict with the following keys:Custom badge
    * <a id="dataset:badges:label"></a>`label` _String_ e.g. 'Open in Colab'
    * <a id="dataset:badges:icon"></a>`icon` _optional String_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
    * <a id="dataset:badges:url"></a>`url` _optional Union\[URL→URI | RelativeLocalPath→Path\]_ e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'
      1. _optional URL→URI_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="dataset:config"></a>`config` _optional YamlDict→Dict\[Any, Any\]_ 
  * <a id="dataset:covers"></a>`covers` _optional List\[Union\[URL→URI | RelativeLocalPath→Path\]\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
    1. _optional Union\[URL→URI | RelativeLocalPath→Path\]_ 
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="dataset:download_url"></a>`download_url` _optional URL→URI_ recommended url to the zipped file if applicable
  * <a id="dataset:git_repo"></a>`git_repo` _optional URL→URI_ A url to the git repository, e.g. to Github or Gitlab.
  * <a id="dataset:icon"></a>`icon` _optional String_ an icon for the resource
  * <a id="dataset:license"></a>`license` _optional String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
  * <a id="dataset:links"></a>`links` _optional List\[String\]_ links to other bioimage.io resources
  * <a id="dataset:maintainers"></a>`maintainers` _optional List\[Maintainer\]_ Maintainers of this resource.
    1. _Maintainer_   is a Dict with the following keys:
    * <a id="dataset:maintainers:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="dataset:maintainers:email"></a>`email` _optional Email_ 
    * <a id="dataset:maintainers:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="dataset:maintainers:name"></a>`name` _optional String_ Full name.
    * <a id="dataset:maintainers:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="dataset:source"></a>`source` _optional Union\[URI→String | RelativeLocalPath→Path\]_ url or local relative path to the source of the resource
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="dataset:version"></a>`version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
* <a id="download_url"></a>`download_url` _optional URL→URI_ recommended url to the zipped file if applicable
* <a id="git_repo"></a>`git_repo` _optional URL→URI_ A url to the git repository, e.g. to Github or Gitlab.
* <a id="icon"></a>`icon` _optional String_ an icon for the resource
* <a id="license"></a>`license` _optional String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
* <a id="links"></a>`links` _optional List\[String\]_ links to other bioimage.io resources
* <a id="maintainers"></a>`maintainers` _optional List\[Maintainer\]_ Maintainers of this resource.
  1. _Maintainer_   is a Dict with the following keys:
  * <a id="maintainers:affiliation"></a>`affiliation` _optional String_ Affiliation.
  * <a id="maintainers:email"></a>`email` _optional Email_ 
  * <a id="maintainers:github_user"></a>`github_user` _optional String_ GitHub user name.
  * <a id="maintainers:name"></a>`name` _optional String_ Full name.
  * <a id="maintainers:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
* <a id="model"></a>`model` _optional List\[Union\[CollectionEntry | Model | Model\]\]_ 
  1. _optional Union\[CollectionEntry | Model | Model\]_ 
  1. _CollectionEntry_   is a Dict with the following keys:
  * <a id="model:id_"></a>`id_` _String_ 
  * <a id="model:source"></a>`source` _URL→URI_ 
  1. _Model_ # BioImage.IO Model Resource Description File Specification 0.4.1
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing AI models with pretrained weights.
These fields are typically stored in YAML files which we call Model Resource Description Files or `model RDF`.
The model RDFs can be downloaded or uploaded to the bioimage.io website, produced or consumed by BioImage.IO-compatible consumers(e.g. image analysis software or other website).

The model RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.
 Model is a Dict with the following keys:# BioImage.IO Model Resource Description File Specification 0.4.1
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing AI models with pretrained weights.
These fields are typically stored in YAML files which we call Model Resource Description Files or `model RDF`.
The model RDFs can be downloaded or uploaded to the bioimage.io website, produced or consumed by BioImage.IO-compatible consumers(e.g. image analysis software or other website).

The model RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.

  * <a id="model:format_version"></a>`format_version` _String_ Version of the BioImage.IO Model Resource Description File Specification used.
This is mandatory, and important for the consumer software to verify before parsing the fields.
The recommended behavior for the implementation is to keep backward compatibility and throw an error if the model yaml
is in an unsupported format version. The current format version described here is
0.4.1
  * <a id="model:authors"></a>`authors` _List\[Author\]_ A list of authors. The authors are the creators of the specifications and the primary points of contact.
    1. _Author_   is a Dict with the following keys:
    * <a id="model:authors:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="model:authors:email"></a>`email` _optional Email_ 
    * <a id="model:authors:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="model:authors:name"></a>`name` _optional String_ Full name.
    * <a id="model:authors:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="model:cite"></a>`cite` _List\[CiteEntry\]_ A list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used.
    1. _CiteEntry_   is a Dict with the following keys:
    * <a id="model:cite:text"></a>`text` _String_ 
    * <a id="model:cite:doi"></a>`doi` _optional* String_ 
    * <a id="model:cite:url"></a>`url` _optional* String_ 
  * <a id="model:description"></a>`description` _String_ A string containing a brief description.
  * <a id="model:documentation"></a>`documentation` _Union\[URL→URI | RelativeLocalPath→Path\]_ Relative path to file with additional documentation in markdown. This means: 1) only relative file path is allowed 2) the file must be in markdown format with `.md` file name extension 3) URL is not allowed. It is recommended to use `README.md` as the documentation name.
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:inputs"></a>`inputs` _List\[InputTensor\]_ Describes the input tensors expected by this model.
    1. _InputTensor_   is a Dict with the following keys:
    * <a id="model:inputs:axes"></a>`axes` _Axes→String_ Axes identifying characters from: bitczyx. Same length and order as the axes in `shape`.

    | character | description |
    | --- | --- |
    |  b  |  batch (groups multiple samples) |
    |  i  |  instance/index/element |
    |  t  |  time |
    |  c  |  channel |
    |  z  |  spatial dimension z |
    |  y  |  spatial dimension y |
    |  x  |  spatial dimension x |
    * <a id="model:inputs:data_type"></a>`data_type` _String_ The data type of this tensor. For inputs, only `float32` is allowed and the consumer software needs to ensure that the correct data type is passed here. For outputs can be any of `float32, float64, (u)int8, (u)int16, (u)int32, (u)int64`. The data flow in bioimage.io models is explained [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).
    * <a id="model:inputs:name"></a>`name` _String_ Tensor name. No duplicates are allowed.
    * <a id="model:inputs:shape"></a>`shape` _Union\[ExplicitShape→List\[Integer\] | ParametrizedInputShape\]_ Specification of input tensor shape.
      1. _optional ExplicitShape→List\[Integer\]_ Exact shape with same length as `axes`, e.g. `shape: [1, 512, 512, 1]`
      1. _ParametrizedInputShape_ A sequence of valid shapes given by `shape = min + k * step for k in {0, 1, ...}`. ParametrizedInputShape is a Dict with the following keys:
      * <a id="model:inputs:shape:min"></a>`min` _List\[Integer\]_ The minimum input shape with same length as `axes`
      * <a id="model:inputs:shape:step"></a>`step` _List\[Integer\]_ The minimum shape change with same length as `axes`
    * <a id="model:inputs:data_range"></a>`data_range` _optional Tuple_ Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor. If not specified, the full data range that can be expressed in `data_type` is allowed.
    * <a id="model:inputs:description"></a>`description` _optional String_ 
    * <a id="model:inputs:preprocessing"></a>`preprocessing` _optional List\[Preprocessing\]_ Description of how this input should be preprocessed.
      1. _Preprocessing_   is a Dict with the following keys:
      * <a id="model:inputs:preprocessing:name"></a>`name` _String_ Name of preprocessing. One of: binarize, clip, scale_linear, sigmoid, zero_mean_unit_variance, scale_range.
      * <a id="model:inputs:preprocessing:kwargs"></a>`kwargs` _optional Kwargs→Dict\[String, Any\]_ Key word arguments as described in [preprocessing spec](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/preprocessing_spec_0_3.md).
  * <a id="model:license"></a>`license` _String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
  * <a id="model:name"></a>`name` _String_ Name of this model. It should be human-readable and only contain letters, numbers, `_`, `-` or spaces and not be longer than 64 characters.
  * <a id="model:tags"></a>`tags` _List\[String\]_ A list of tags.
  * <a id="model:test_inputs"></a>`test_inputs` _List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ List of URIs or local relative paths to test inputs as described in inputs for **a single test case**. This means if your model has more than one input, you should provide one URI for each input.Each test input should be a file with a ndarray in [numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).The extension must be '.npy'.
    1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:test_outputs"></a>`test_outputs` _List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ Analog to to test_inputs.
    1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:timestamp"></a>`timestamp` _DateTime_ Timestamp of the initial creation of this model in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format.
  * <a id="model:type"></a>`type` _String_ 
  * <a id="model:weights"></a>`weights` _Dict\[String, Union\[KerasHdf5WeightsEntry | OnnxWeightsEntry | PytorchStateDictWeightsEntry | TensorflowJsWeightsEntry | TensorflowSavedModelBundleWeightsEntry | TorchscriptWeightsEntry\]\]_ The weights for this model. Weights can be given for different formats, but should otherwise be equivalent. The available weight formats determine which consumers can use this model.
    1. _String_ Format of this set of weights. Weight formats can define additional (optional or required) fields. See [weight_formats_spec_0_4.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/weight_formats_spec_0_4.md). One of: pytorch_state_dict, torchscript, keras_hdf5, tensorflow_js, tensorflow_saved_model_bundle, onnx
  * <a id="model:attachments"></a>`attachments` _Attachments_ Attachments. Additional, unknown keys are allowed. Attachments is a Dict with the following keys:
    * <a id="model:attachments:files"></a>`files` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ File attachments; included when packaging the resource.
      1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
      1. _optional URI→String_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="model:badges"></a>`badges` _optional List\[Badge\]_ a list of badges
    1. _Badge_ Custom badge Badge is a Dict with the following keys:Custom badge
    * <a id="model:badges:label"></a>`label` _String_ e.g. 'Open in Colab'
    * <a id="model:badges:icon"></a>`icon` _optional String_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
    * <a id="model:badges:url"></a>`url` _optional Union\[URL→URI | RelativeLocalPath→Path\]_ e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'
      1. _optional URL→URI_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="model:config"></a>`config` _optional YamlDict→Dict\[Any, Any\]_ A custom configuration field that can contain any keys not present in the RDF spec. This means you should not store, for example, github repo URL in `config` since we already have the `git_repo` key defined in the spec.
Keys in `config` may be very specific to a tool or consumer software. To avoid conflicted definitions, it is recommended to wrap configuration into a sub-field named with the specific domain or tool name, for example:
    ```yaml
       config:
          bioimage_io:  # here is the domain name
            my_custom_key: 3837283
            another_key:
               nested: value
          imagej:
            macro_dir: /path/to/macro/file
    ```
    If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.

    For example:
    ```yaml
    config:
      # custom config for DeepImageJ, see https://github.com/bioimage-io/configuration/issues/23
      deepimagej:
        model_keys:
          # In principle the tag "SERVING" is used in almost every tf model
          model_tag: tf.saved_model.tag_constants.SERVING
          # Signature definition to call the model. Again "SERVING" is the most general
          signature_definition: tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY
        test_information:
          input_size: [2048x2048] # Size of the input images
          output_size: [1264x1264 ]# Size of all the outputs
          device: cpu # Device used. In principle either cpu or GPU
          memory_peak: 257.7 Mb # Maximum memory consumed by the model in the device
          runtime: 78.8s # Time it took to run the model
          pixel_size: [9.658E-4µmx9.658E-4µm] # Size of the pixels of the input
    ```

  * <a id="model:covers"></a>`covers` _optional List\[Union\[URL→URI | RelativeLocalPath→Path\]\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
    1. _optional Union\[URL→URI | RelativeLocalPath→Path\]_ 
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:download_url"></a>`download_url` _optional URL→URI_ recommended url to the zipped file if applicable
  * <a id="model:git_repo"></a>`git_repo` _optional URL→URI_ A url to the git repository, e.g. to Github or Gitlab.If the model is contained in a subfolder of a git repository, then a url to the exact folder(which contains the configuration yaml file) should be used.
  * <a id="model:icon"></a>`icon` _optional String_ an icon for the resource
  * <a id="model:links"></a>`links` _optional List\[String\]_ links to other bioimage.io resources
  * <a id="model:maintainers"></a>`maintainers` _optional List\[Maintainer\]_ Maintainers of this resource.
    1. _Maintainer_   is a Dict with the following keys:
    * <a id="model:maintainers:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="model:maintainers:email"></a>`email` _optional Email_ 
    * <a id="model:maintainers:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="model:maintainers:name"></a>`name` _optional String_ Full name.
    * <a id="model:maintainers:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="model:outputs"></a>`outputs` _optional List\[OutputTensor\]_ Describes the output tensors from this model.
    1. _OutputTensor_   is a Dict with the following keys:
    * <a id="model:outputs:axes"></a>`axes` _Axes→String_ Axes identifying characters from: bitczyx. Same length and order as the axes in `shape`.

    | character | description |
    | --- | --- |
    |  b  |  batch (groups multiple samples) |
    |  i  |  instance/index/element |
    |  t  |  time |
    |  c  |  channel |
    |  z  |  spatial dimension z |
    |  y  |  spatial dimension y |
    |  x  |  spatial dimension x |
    * <a id="model:outputs:data_type"></a>`data_type` _String_ The data type of this tensor. For inputs, only `float32` is allowed and the consumer software needs to ensure that the correct data type is passed here. For outputs can be any of `float32, float64, (u)int8, (u)int16, (u)int32, (u)int64`. The data flow in bioimage.io models is explained [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).
    * <a id="model:outputs:name"></a>`name` _String_ Tensor name. No duplicates are allowed.
    * <a id="model:outputs:shape"></a>`shape` _Union\[ExplicitShape→List\[Integer\] | ImplicitOutputShape\]_ Specification of output tensor shape.
      1. _optional ExplicitShape→List\[Integer\]_ 
      1. _ImplicitOutputShape_ In reference to the shape of an input tensor, the shape of the output tensor is `shape = shape(input_tensor) * scale + 2 * offset`. ImplicitOutputShape is a Dict with the following keys:
      * <a id="model:outputs:shape:offset"></a>`offset` _List\[Float\]_ Position of origin wrt to input. Multiple of 0.5.
      * <a id="model:outputs:shape:reference_tensor"></a>`reference_tensor` _String_ Name of the reference tensor.
      * <a id="model:outputs:shape:scale"></a>`scale` _List\[Float\]_ 'output_pix/input_pix' for each dimension.
    * <a id="model:outputs:data_range"></a>`data_range` _optional Tuple_ Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor. If not specified, the full data range that can be expressed in `data_type` is allowed.
    * <a id="model:outputs:description"></a>`description` _optional String_ 
    * <a id="model:outputs:halo"></a>`halo` _optional List\[Integer\]_ The halo to crop from the output tensor (for example to crop away boundary effects or for tiling). The halo should be cropped from both sides, i.e. `shape_after_crop = shape - 2 * halo`. The `halo` is not cropped by the bioimage.io model, but is left to be cropped by the consumer software. Use `shape:offset` if the model output itself is cropped and input and output shapes not fixed.
    * <a id="model:outputs:postprocessing"></a>`postprocessing` _optional List\[Postprocessing\]_ Description of how this output should be postprocessed.
      1. _Postprocessing_   is a Dict with the following keys:
      * <a id="model:outputs:postprocessing:name"></a>`name` _String_ Name of postprocessing. One of: binarize, clip, scale_linear, sigmoid, zero_mean_unit_variance, scale_range, scale_mean_variance.
      * <a id="model:outputs:postprocessing:kwargs"></a>`kwargs` _optional Kwargs→Dict\[String, Any\]_ Key word arguments as described in [postprocessing spec](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/postprocessing_spec_0_3.md).
  * <a id="model:packaged_by"></a>`packaged_by` _optional List\[Author\]_ The persons that have packaged and uploaded this model. Only needs to be specified if different from `authors` in root or any entry in `weights`.
    1. _Author_   is a Dict with the following keys:
    * <a id="model:packaged_by:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="model:packaged_by:email"></a>`email` _optional Email_ 
    * <a id="model:packaged_by:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="model:packaged_by:name"></a>`name` _optional String_ Full name.
    * <a id="model:packaged_by:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="model:parent"></a>`parent` _ModelParent_ Parent model from which the trained weights of this model have been derived, e.g. by finetuning the weights of this model on a different dataset. For format changes of the same trained model checkpoint, see `weights`. ModelParent is a Dict with the following keys:
    * <a id="model:parent:sha256"></a>`sha256` _optional SHA256→String_ Hash of the parent model RDF.
    * <a id="model:parent:uri"></a>`uri` _optional Union\[URI→String | RelativeLocalPath→Path\]_ Url of another model available on bioimage.io or path to a local model in the bioimage.io specification. If it is a url, it needs to be a github url linking to the page containing the model (NOT the raw file).
      1. _optional URI→String_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="model:run_mode"></a>`run_mode` _RunMode_ Custom run mode for this model: for more complex prediction procedures like test time data augmentation that currently cannot be expressed in the specification. No standard run modes are defined yet. RunMode is a Dict with the following keys:
    * <a id="model:run_mode:name"></a>`name` _String_ The name of the `run_mode`
    * <a id="model:run_mode:kwargs"></a>`kwargs` _optional Kwargs→Dict\[String, Any\]_ Key word arguments.
  * <a id="model:sample_inputs"></a>`sample_inputs` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ List of URIs/local relative paths to sample inputs to illustrate possible inputs for the model, for example stored as png or tif images. The model is not tested with these sample files that serve to inform a human user about an example use case.
    1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:sample_outputs"></a>`sample_outputs` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ List of URIs/local relative paths to sample outputs corresponding to the `sample_inputs`.
    1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:source"></a>`source` _optional Union\[URI→String | RelativeLocalPath→Path\]_ url or local relative path to the source of the resource
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:version"></a>`version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
  1. _Model_ # BioImage.IO Model Resource Description File Specification 0.3.5
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing AI models with pretrained weights.
These fields are typically stored in YAML files which we called Model Resource Description Files or `model RDF`.
The model RDFs can be downloaded or uploaded to the bioimage.io website, produced or consumed by BioImage.IO-compatible consumers(e.g. image analysis software or other website).

The model RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.
 Model is a Dict with the following keys:# BioImage.IO Model Resource Description File Specification 0.3.5
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing AI models with pretrained weights.
These fields are typically stored in YAML files which we called Model Resource Description Files or `model RDF`.
The model RDFs can be downloaded or uploaded to the bioimage.io website, produced or consumed by BioImage.IO-compatible consumers(e.g. image analysis software or other website).

The model RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.

  * <a id="model:format_version"></a>`format_version` _String_ Version of the BioImage.IO Model Resource Description File Specification used.
This is mandatory, and important for the consumer software to verify before parsing the fields.
The recommended behavior for the implementation is to keep backward compatibility and throw an error if the model yaml
is in an unsupported format version. The current format version described here is
0.3.5
  * <a id="model:authors"></a>`authors` _List\[Author\]_ A list of authors. The authors are the creators of the specifications and the primary points of contact.
    1. _Author_   is a Dict with the following keys:
    * <a id="model:authors:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="model:authors:email"></a>`email` _optional Email_ 
    * <a id="model:authors:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="model:authors:name"></a>`name` _optional String_ Full name.
    * <a id="model:authors:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="model:cite"></a>`cite` _List\[CiteEntry\]_ A list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used.
    1. _CiteEntry_   is a Dict with the following keys:
    * <a id="model:cite:text"></a>`text` _String_ 
    * <a id="model:cite:doi"></a>`doi` _optional* String_ 
    * <a id="model:cite:url"></a>`url` _optional* String_ 
  * <a id="model:description"></a>`description` _String_ A string containing a brief description.
  * <a id="model:documentation"></a>`documentation` _Union\[URL→URI | RelativeLocalPath→Path\]_ Relative path to file with additional documentation in markdown. This means: 1) only relative file path is allowed 2) the file must be in markdown format with `.md` file name extension 3) URL is not allowed. It is recommended to use `README.md` as the documentation name.
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:license"></a>`license` _String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
  * <a id="model:name"></a>`name` _String_ Name of this model. It should be human-readable and only contain letters, numbers, `_`, `-` or spaces and not be longer than 36 characters.
  * <a id="model:tags"></a>`tags` _List\[String\]_ A list of tags.
  * <a id="model:test_inputs"></a>`test_inputs` _List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ List of URIs or local relative paths to test inputs as described in inputs for **a single test case**. This means if your model has more than one input, you should provide one URI for each input.Each test input should be a file with a ndarray in [numpy.lib file format](https://numpy.org/doc/stable/reference/generated/numpy.lib.format.html#module-numpy.lib.format).The extension must be '.npy'.
    1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:test_outputs"></a>`test_outputs` _List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ Analog to to test_inputs.
    1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:timestamp"></a>`timestamp` _DateTime_ Timestamp of the initial creation of this model in [ISO 8601](#https://en.wikipedia.org/wiki/ISO_8601) format.
  * <a id="model:type"></a>`type` _String_ 
  * <a id="model:weights"></a>`weights` _Dict\[String, Union\[PytorchStateDictWeightsEntry | PytorchScriptWeightsEntry | KerasHdf5WeightsEntry | TensorflowJsWeightsEntry | TensorflowSavedModelBundleWeightsEntry | OnnxWeightsEntry\]\]_ The weights for this model. Weights can be given for different formats, but should otherwise be equivalent. The available weight formats determine which consumers can use this model.
    1. _String_ Format of this set of weights. Weight formats can define additional (optional or required) fields. See [weight_formats_spec_0_3.md](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/weight_formats_spec_0_3.md). One of: pytorch_state_dict, pytorch_script, keras_hdf5, tensorflow_js, tensorflow_saved_model_bundle, onnx
  * <a id="model:attachments"></a>`attachments` _Attachments_ Attachments. Additional, unknown keys are allowed. Attachments is a Dict with the following keys:
    * <a id="model:attachments:files"></a>`files` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ File attachments; included when packaging the resource.
      1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
      1. _optional URI→String_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="model:badges"></a>`badges` _optional List\[Badge\]_ a list of badges
    1. _Badge_ Custom badge Badge is a Dict with the following keys:Custom badge
    * <a id="model:badges:label"></a>`label` _String_ e.g. 'Open in Colab'
    * <a id="model:badges:icon"></a>`icon` _optional String_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
    * <a id="model:badges:url"></a>`url` _optional Union\[URL→URI | RelativeLocalPath→Path\]_ e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'
      1. _optional URL→URI_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="model:config"></a>`config` _optional YamlDict→Dict\[Any, Any\]_ A custom configuration field that can contain any keys not present in the RDF spec. This means you should not store, for example, github repo URL in `config` since we already have the `git_repo` key defined in the spec.
Keys in `config` may be very specific to a tool or consumer software. To avoid conflicted definitions, it is recommended to wrap configuration into a sub-field named with the specific domain or tool name, for example:
    ```yaml
       config:
          bioimage_io:  # here is the domain name
            my_custom_key: 3837283
            another_key:
               nested: value
          imagej:
            macro_dir: /path/to/macro/file
    ```
    If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.

    For example:
    ```yaml
    config:
      # custom config for DeepImageJ, see https://github.com/bioimage-io/configuration/issues/23
      deepimagej:
        model_keys:
          # In principle the tag "SERVING" is used in almost every tf model
          model_tag: tf.saved_model.tag_constants.SERVING
          # Signature definition to call the model. Again "SERVING" is the most general
          signature_definition: tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY
        test_information:
          input_size: [2048x2048] # Size of the input images
          output_size: [1264x1264 ]# Size of all the outputs
          device: cpu # Device used. In principle either cpu or GPU
          memory_peak: 257.7 Mb # Maximum memory consumed by the model in the device
          runtime: 78.8s # Time it took to run the model
          pixel_size: [9.658E-4µmx9.658E-4µm] # Size of the pixels of the input
    ```

  * <a id="model:covers"></a>`covers` _optional List\[Union\[URL→URI | RelativeLocalPath→Path\]\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
    1. _optional Union\[URL→URI | RelativeLocalPath→Path\]_ 
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:dependencies"></a>`dependencies` _optional Dependencies→String_ Dependency manager and dependency file, specified as `<dependency manager>:<relative path to file>`. For example: 'conda:./environment.yaml', 'maven:./pom.xml', or 'pip:./requirements.txt'
  * <a id="model:download_url"></a>`download_url` _optional URL→URI_ recommended url to the zipped file if applicable
  * <a id="model:framework"></a>`framework` _optional String_ The deep learning framework of the source code. One of: pytorch, tensorflow. This field is only required if the field `source` is present.
  * <a id="model:git_repo"></a>`git_repo` _optional String_ A url to the git repository, e.g. to Github or Gitlab.If the model is contained in a subfolder of a git repository, then a url to the exact folder(which contains the configuration yaml file) should be used.
  * <a id="model:icon"></a>`icon` _optional String_ an icon for the resource
  * <a id="model:inputs"></a>`inputs` _optional List\[InputTensor\]_ Describes the input tensors expected by this model.
    1. _InputTensor_   is a Dict with the following keys:
    * <a id="model:inputs:axes"></a>`axes` _Axes→String_ Axes identifying characters from: bitczyx. Same length and order as the axes in `shape`.

    | character | description |
    | --- | --- |
    |  b  |  batch (groups multiple samples) |
    |  i  |  instance/index/element |
    |  t  |  time |
    |  c  |  channel |
    |  z  |  spatial dimension z |
    |  y  |  spatial dimension y |
    |  x  |  spatial dimension x |
    * <a id="model:inputs:data_type"></a>`data_type` _String_ The data type of this tensor. For inputs, only `float32` is allowed and the consumer software needs to ensure that the correct data type is passed here. For outputs can be any of `float32, float64, (u)int8, (u)int16, (u)int32, (u)int64`. The data flow in bioimage.io models is explained [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).
    * <a id="model:inputs:name"></a>`name` _String_ Tensor name.
    * <a id="model:inputs:shape"></a>`shape` _Union\[ExplicitShape→List\[Integer\] | ParametrizedInputShape\]_ Specification of input tensor shape.
      1. _optional ExplicitShape→List\[Integer\]_ Exact shape with same length as `axes`, e.g. `shape: [1, 512, 512, 1]`
      1. _ParametrizedInputShape_ A sequence of valid shapes given by `shape = min + k * step for k in {0, 1, ...}`. ParametrizedInputShape is a Dict with the following keys:
      * <a id="model:inputs:shape:min"></a>`min` _List\[Integer\]_ The minimum input shape with same length as `axes`
      * <a id="model:inputs:shape:step"></a>`step` _List\[Integer\]_ The minimum shape change with same length as `axes`
    * <a id="model:inputs:data_range"></a>`data_range` _optional Tuple_ Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor. If not specified, the full data range that can be expressed in `data_type` is allowed.
    * <a id="model:inputs:description"></a>`description` _optional String_ 
    * <a id="model:inputs:preprocessing"></a>`preprocessing` _optional List\[Preprocessing\]_ Description of how this input should be preprocessed.
      1. _Preprocessing_   is a Dict with the following keys:
      * <a id="model:inputs:preprocessing:name"></a>`name` _String_ Name of preprocessing. One of: binarize, clip, scale_linear, sigmoid, zero_mean_unit_variance, scale_range.
      * <a id="model:inputs:preprocessing:kwargs"></a>`kwargs` _optional Kwargs→Dict\[String, Any\]_ Key word arguments as described in [preprocessing spec](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/preprocessing_spec_0_3.md).
  * <a id="model:kwargs"></a>`kwargs` _optional Kwargs→Dict\[String, Any\]_ Keyword arguments for the implementation specified by `source`. This field is only required if the field `source` is present.
  * <a id="model:language"></a>`language` _optional* String_ Programming language of the source code. One of: python, java. This field is only required if the field `source` is present.
  * <a id="model:links"></a>`links` _optional List\[String\]_ links to other bioimage.io resources
  * <a id="model:maintainers"></a>`maintainers` _optional List\[Maintainer\]_ Maintainers of this resource.
    1. _Maintainer_   is a Dict with the following keys:
    * <a id="model:maintainers:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="model:maintainers:email"></a>`email` _optional Email_ 
    * <a id="model:maintainers:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="model:maintainers:name"></a>`name` _optional String_ Full name.
    * <a id="model:maintainers:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="model:outputs"></a>`outputs` _optional List\[OutputTensor\]_ Describes the output tensors from this model.
    1. _OutputTensor_   is a Dict with the following keys:
    * <a id="model:outputs:axes"></a>`axes` _Axes→String_ Axes identifying characters from: bitczyx. Same length and order as the axes in `shape`.

    | character | description |
    | --- | --- |
    |  b  |  batch (groups multiple samples) |
    |  i  |  instance/index/element |
    |  t  |  time |
    |  c  |  channel |
    |  z  |  spatial dimension z |
    |  y  |  spatial dimension y |
    |  x  |  spatial dimension x |
    * <a id="model:outputs:data_type"></a>`data_type` _String_ The data type of this tensor. For inputs, only `float32` is allowed and the consumer software needs to ensure that the correct data type is passed here. For outputs can be any of `float32, float64, (u)int8, (u)int16, (u)int32, (u)int64`. The data flow in bioimage.io models is explained [in this diagram.](https://docs.google.com/drawings/d/1FTw8-Rn6a6nXdkZ_SkMumtcjvur9mtIhRqLwnKqZNHM/edit).
    * <a id="model:outputs:name"></a>`name` _String_ Tensor name.
    * <a id="model:outputs:shape"></a>`shape` _Union\[ExplicitShape→List\[Integer\] | ImplicitOutputShape\]_ Specification of output tensor shape.
      1. _optional ExplicitShape→List\[Integer\]_ 
      1. _ImplicitOutputShape_ In reference to the shape of an input tensor, the shape of the output tensor is `shape = shape(input_tensor) * scale + 2 * offset`. ImplicitOutputShape is a Dict with the following keys:
      * <a id="model:outputs:shape:offset"></a>`offset` _List\[Float\]_ Position of origin wrt to input. Multiple of 0.5.
      * <a id="model:outputs:shape:reference_tensor"></a>`reference_tensor` _String_ Name of the reference tensor.
      * <a id="model:outputs:shape:scale"></a>`scale` _List\[Float\]_ 'output_pix/input_pix' for each dimension.
    * <a id="model:outputs:data_range"></a>`data_range` _optional Tuple_ Tuple `(minimum, maximum)` specifying the allowed range of the data in this tensor. If not specified, the full data range that can be expressed in `data_type` is allowed.
    * <a id="model:outputs:description"></a>`description` _optional String_ 
    * <a id="model:outputs:halo"></a>`halo` _optional List\[Integer\]_ Hint to describe the potentially corrupted edge region of the output tensor, due to boundary effects. The `halo` is not cropped by the bioimage.io model, but is left to be cropped by the consumer software. An example implementation of prediction with tiling, accounting for the halo can be found [here](https://github.com/bioimage-io/core-bioimage-io-python/blob/main/bioimageio/core/prediction.py#L194-L236). Use `shape:offset` if the model output itself is cropped and input and output shapes not fixed. 
    * <a id="model:outputs:postprocessing"></a>`postprocessing` _optional List\[Postprocessing\]_ Description of how this output should be postprocessed.
      1. _Postprocessing_   is a Dict with the following keys:
      * <a id="model:outputs:postprocessing:name"></a>`name` _String_ Name of postprocessing. One of: binarize, clip, scale_linear, sigmoid, zero_mean_unit_variance, scale_range, scale_mean_variance.
      * <a id="model:outputs:postprocessing:kwargs"></a>`kwargs` _optional Kwargs→Dict\[String, Any\]_ Key word arguments as described in [postprocessing spec](https://github.com/bioimage-io/spec-bioimage-io/blob/gh-pages/postprocessing_spec_0_3.md).
  * <a id="model:packaged_by"></a>`packaged_by` _optional List\[Author\]_ The persons that have packaged and uploaded this model. Only needs to be specified if different from `authors` in root or any entry in `weights`.
    1. _Author_   is a Dict with the following keys:
    * <a id="model:packaged_by:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="model:packaged_by:email"></a>`email` _optional Email_ 
    * <a id="model:packaged_by:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="model:packaged_by:name"></a>`name` _optional String_ Full name.
    * <a id="model:packaged_by:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="model:parent"></a>`parent` _ModelParent_ Parent model from which the trained weights of this model have been derived, e.g. by finetuning the weights of this model on a different dataset. For format changes of the same trained model checkpoint, see `weights`. ModelParent is a Dict with the following keys:
    * <a id="model:parent:sha256"></a>`sha256` _optional SHA256→String_ Hash of the parent model RDF.
    * <a id="model:parent:uri"></a>`uri` _optional Union\[URI→String | RelativeLocalPath→Path\]_ Url of another model available on bioimage.io or path to a local model in the bioimage.io specification. If it is a url, it needs to be a github url linking to the page containing the model (NOT the raw file).
      1. _optional URI→String_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="model:run_mode"></a>`run_mode` _RunMode_ Custom run mode for this model: for more complex prediction procedures like test time data augmentation that currently cannot be expressed in the specification. No standard run modes are defined yet. RunMode is a Dict with the following keys:
    * <a id="model:run_mode:name"></a>`name` _String_ The name of the `run_mode`
    * <a id="model:run_mode:kwargs"></a>`kwargs` _optional Kwargs→Dict\[String, Any\]_ Key word arguments.
  * <a id="model:sample_inputs"></a>`sample_inputs` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ List of URIs/local relative paths to sample inputs to illustrate possible inputs for the model, for example stored as png or tif images. The model is not tested with these sample files that serve to inform a human user about an example use case.
    1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:sample_outputs"></a>`sample_outputs` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ List of URIs/local relative paths to sample outputs corresponding to the `sample_inputs`.
    1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:sha256"></a>`sha256` _optional String_ SHA256 checksum of the model source code file.You can drag and drop your file to this [online tool](http://emn178.github.io/online-tools/sha256_checksum.html) to generate it in your browser. Or you can generate the SHA256 code for your model and weights by using for example, `hashlib` in Python. 
    Code snippet to compute SHA256 checksum
    
    ```python
    import hashlib
    
    filename = "your filename here"
    with open(filename, "rb") as f:
      bytes = f.read() # read entire file as bytes
      readable_hash = hashlib.sha256(bytes).hexdigest()
      print(readable_hash)
      ```

 This field is only required if the field source is present.
  * <a id="model:source"></a>`source` _optional* ImportableSource→String_ Language and framework specific implementation. As some weights contain the model architecture, the source is optional depending on the present weight formats. `source` can either point to a local implementation: `<relative path to file>:<identifier of implementation within the source file>` or the implementation in an available dependency: `<root-dependency>.<sub-dependency>.<identifier>`.
For example: `my_function.py:MyImplementation` or `core_library.some_module.some_function`.
  * <a id="model:version"></a>`version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
* <a id="notebook"></a>`notebook` _optional List\[Union\[CollectionEntry | RDF\]\]_ 
  1. _optional Union\[CollectionEntry | RDF\]_ 
  1. _CollectionEntry_   is a Dict with the following keys:
  * <a id="notebook:id_"></a>`id_` _String_ 
  * <a id="notebook:source"></a>`source` _URL→URI_ 
  1. _RDF_ # BioImage.IO Resource Description File Specification 0.2.1
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks. 
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by 
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be 
specified.
 RDF is a Dict with the following keys:# BioImage.IO Resource Description File Specification 0.2.1
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks. 
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by 
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be 
specified.

  * <a id="notebook:format_version"></a>`format_version` _String_ Version of the BioImage.IO Resource Description File Specification used.The current general format version described here is 0.2.1. Note: The general RDF format is not to be confused with specialized RDF format like the Model RDF format.
  * <a id="notebook:authors"></a>`authors` _List\[Author\]_ A list of authors. The authors are the creators of the specifications and the primary points of contact.
    1. _Author_   is a Dict with the following keys:
    * <a id="notebook:authors:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="notebook:authors:email"></a>`email` _optional Email_ 
    * <a id="notebook:authors:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="notebook:authors:name"></a>`name` _optional String_ Full name.
    * <a id="notebook:authors:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="notebook:cite"></a>`cite` _List\[CiteEntry\]_ A list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used.
    1. _CiteEntry_   is a Dict with the following keys:
    * <a id="notebook:cite:text"></a>`text` _String_ 
    * <a id="notebook:cite:doi"></a>`doi` _optional* String_ 
    * <a id="notebook:cite:url"></a>`url` _optional* String_ 
  * <a id="notebook:description"></a>`description` _String_ A string containing a brief description.
  * <a id="notebook:documentation"></a>`documentation` _Union\[URL→URI | RelativeLocalPath→Path\]_ URL or relative path to markdown file with additional documentation. For markdown files the recommended documentation file name is `README.md`.
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="notebook:name"></a>`name` _String_ name of the resource, a human-friendly name
  * <a id="notebook:tags"></a>`tags` _List\[String\]_ A list of tags.
  * <a id="notebook:type"></a>`type` _String_ 
  * <a id="notebook:attachments"></a>`attachments` _Attachments_ Attachments. Additional, unknown keys are allowed. Attachments is a Dict with the following keys:
    * <a id="notebook:attachments:files"></a>`files` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ File attachments; included when packaging the resource.
      1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
      1. _optional URI→String_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="notebook:badges"></a>`badges` _optional List\[Badge\]_ a list of badges
    1. _Badge_ Custom badge Badge is a Dict with the following keys:Custom badge
    * <a id="notebook:badges:label"></a>`label` _String_ e.g. 'Open in Colab'
    * <a id="notebook:badges:icon"></a>`icon` _optional String_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
    * <a id="notebook:badges:url"></a>`url` _optional Union\[URL→URI | RelativeLocalPath→Path\]_ e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'
      1. _optional URL→URI_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="notebook:config"></a>`config` _optional YamlDict→Dict\[Any, Any\]_ 
  * <a id="notebook:covers"></a>`covers` _optional List\[Union\[URL→URI | RelativeLocalPath→Path\]\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
    1. _optional Union\[URL→URI | RelativeLocalPath→Path\]_ 
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="notebook:download_url"></a>`download_url` _optional URL→URI_ recommended url to the zipped file if applicable
  * <a id="notebook:git_repo"></a>`git_repo` _optional URL→URI_ A url to the git repository, e.g. to Github or Gitlab.
  * <a id="notebook:icon"></a>`icon` _optional String_ an icon for the resource
  * <a id="notebook:license"></a>`license` _optional String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
  * <a id="notebook:links"></a>`links` _optional List\[String\]_ links to other bioimage.io resources
  * <a id="notebook:maintainers"></a>`maintainers` _optional List\[Maintainer\]_ Maintainers of this resource.
    1. _Maintainer_   is a Dict with the following keys:
    * <a id="notebook:maintainers:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="notebook:maintainers:email"></a>`email` _optional Email_ 
    * <a id="notebook:maintainers:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="notebook:maintainers:name"></a>`name` _optional String_ Full name.
    * <a id="notebook:maintainers:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="notebook:source"></a>`source` _optional Union\[URI→String | RelativeLocalPath→Path\]_ url or local relative path to the source of the resource
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="notebook:version"></a>`version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
* <a id="source"></a>`source` _optional Union\[URI→String | RelativeLocalPath→Path\]_ url or local relative path to the source of the resource
  1. _optional URI→String_ 
  1. _optional RelativeLocalPath→Path_ 
* <a id="version"></a>`version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
