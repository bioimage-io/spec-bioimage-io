# BioImage.IO Resource Description File Specification 0.2.1
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks. 
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by 
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be 
specified.

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
  * <a id="application:links"></a>`links` _optional List\[String\]_ 
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
* <a id="collection"></a>`collection` _optional List\[Union\[CollectionEntry | RDF\]\]_ 
  1. _optional Union\[CollectionEntry | RDF\]_ 
  1. _CollectionEntry_   is a Dict with the following keys:
  * <a id="collection:id_"></a>`id_` _String_ 
  * <a id="collection:source"></a>`source` _URL→URI_ 
  * <a id="collection:links"></a>`links` _optional List\[String\]_ 
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

  * <a id="collection:format_version"></a>`format_version` _String_ Version of the BioImage.IO Resource Description File Specification used.The current general format version described here is 0.2.1. Note: The general RDF format is not to be confused with specialized RDF format like the Model RDF format.
  * <a id="collection:authors"></a>`authors` _List\[Author\]_ A list of authors. The authors are the creators of the specifications and the primary points of contact.
    1. _Author_   is a Dict with the following keys:
    * <a id="collection:authors:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="collection:authors:email"></a>`email` _optional Email_ 
    * <a id="collection:authors:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="collection:authors:name"></a>`name` _optional String_ Full name.
    * <a id="collection:authors:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="collection:cite"></a>`cite` _List\[CiteEntry\]_ A list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used.
    1. _CiteEntry_   is a Dict with the following keys:
    * <a id="collection:cite:text"></a>`text` _String_ 
    * <a id="collection:cite:doi"></a>`doi` _optional* String_ 
    * <a id="collection:cite:url"></a>`url` _optional* String_ 
  * <a id="collection:description"></a>`description` _String_ A string containing a brief description.
  * <a id="collection:documentation"></a>`documentation` _Union\[URL→URI | RelativeLocalPath→Path\]_ URL or relative path to markdown file with additional documentation. For markdown files the recommended documentation file name is `README.md`.
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="collection:name"></a>`name` _String_ name of the resource, a human-friendly name
  * <a id="collection:tags"></a>`tags` _List\[String\]_ A list of tags.
  * <a id="collection:type"></a>`type` _String_ 
  * <a id="collection:attachments"></a>`attachments` _Attachments_ Attachments. Additional, unknown keys are allowed. Attachments is a Dict with the following keys:
    * <a id="collection:attachments:files"></a>`files` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ File attachments; included when packaging the resource.
      1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
      1. _optional URI→String_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="collection:badges"></a>`badges` _optional List\[Badge\]_ a list of badges
    1. _Badge_ Custom badge Badge is a Dict with the following keys:Custom badge
    * <a id="collection:badges:label"></a>`label` _String_ e.g. 'Open in Colab'
    * <a id="collection:badges:icon"></a>`icon` _optional String_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
    * <a id="collection:badges:url"></a>`url` _optional Union\[URL→URI | RelativeLocalPath→Path\]_ e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'
      1. _optional URL→URI_ 
      1. _optional RelativeLocalPath→Path_ 
  * <a id="collection:config"></a>`config` _optional YamlDict→Dict\[Any, Any\]_ 
  * <a id="collection:covers"></a>`covers` _optional List\[Union\[URL→URI | RelativeLocalPath→Path\]\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
    1. _optional Union\[URL→URI | RelativeLocalPath→Path\]_ 
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="collection:download_url"></a>`download_url` _optional URL→URI_ recommended url to the zipped file if applicable
  * <a id="collection:git_repo"></a>`git_repo` _optional URL→URI_ A url to the git repository, e.g. to Github or Gitlab.
  * <a id="collection:icon"></a>`icon` _optional String_ an icon for the resource
  * <a id="collection:license"></a>`license` _optional String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
  * <a id="collection:links"></a>`links` _optional List\[String\]_ links to other bioimage.io resources
  * <a id="collection:maintainers"></a>`maintainers` _optional List\[Maintainer\]_ Maintainers of this resource.
    1. _Maintainer_   is a Dict with the following keys:
    * <a id="collection:maintainers:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="collection:maintainers:email"></a>`email` _optional Email_ 
    * <a id="collection:maintainers:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="collection:maintainers:name"></a>`name` _optional String_ Full name.
    * <a id="collection:maintainers:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="collection:source"></a>`source` _optional Union\[URI→String | RelativeLocalPath→Path\]_ url or local relative path to the source of the resource
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="collection:version"></a>`version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
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
  * <a id="dataset:links"></a>`links` _optional List\[String\]_ 
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
* <a id="model"></a>`model` _optional List\[Union\[CollectionEntry | RDF\]\]_ 
  1. _optional Union\[CollectionEntry | RDF\]_ 
  1. _CollectionEntry_   is a Dict with the following keys:
  * <a id="model:id_"></a>`id_` _String_ 
  * <a id="model:source"></a>`source` _URL→URI_ 
  * <a id="model:links"></a>`links` _optional List\[String\]_ 
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

  * <a id="model:format_version"></a>`format_version` _String_ Version of the BioImage.IO Resource Description File Specification used.The current general format version described here is 0.2.1. Note: The general RDF format is not to be confused with specialized RDF format like the Model RDF format.
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
  * <a id="model:documentation"></a>`documentation` _Union\[URL→URI | RelativeLocalPath→Path\]_ URL or relative path to markdown file with additional documentation. For markdown files the recommended documentation file name is `README.md`.
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:name"></a>`name` _String_ name of the resource, a human-friendly name
  * <a id="model:tags"></a>`tags` _List\[String\]_ A list of tags.
  * <a id="model:type"></a>`type` _String_ 
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
  * <a id="model:config"></a>`config` _optional YamlDict→Dict\[Any, Any\]_ 
  * <a id="model:covers"></a>`covers` _optional List\[Union\[URL→URI | RelativeLocalPath→Path\]\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
    1. _optional Union\[URL→URI | RelativeLocalPath→Path\]_ 
    1. _optional URL→URI_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:download_url"></a>`download_url` _optional URL→URI_ recommended url to the zipped file if applicable
  * <a id="model:git_repo"></a>`git_repo` _optional URL→URI_ A url to the git repository, e.g. to Github or Gitlab.
  * <a id="model:icon"></a>`icon` _optional String_ an icon for the resource
  * <a id="model:license"></a>`license` _optional String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
  * <a id="model:links"></a>`links` _optional List\[String\]_ links to other bioimage.io resources
  * <a id="model:maintainers"></a>`maintainers` _optional List\[Maintainer\]_ Maintainers of this resource.
    1. _Maintainer_   is a Dict with the following keys:
    * <a id="model:maintainers:affiliation"></a>`affiliation` _optional String_ Affiliation.
    * <a id="model:maintainers:email"></a>`email` _optional Email_ 
    * <a id="model:maintainers:github_user"></a>`github_user` _optional String_ GitHub user name.
    * <a id="model:maintainers:name"></a>`name` _optional String_ Full name.
    * <a id="model:maintainers:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  * <a id="model:source"></a>`source` _optional Union\[URI→String | RelativeLocalPath→Path\]_ url or local relative path to the source of the resource
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
  * <a id="model:version"></a>`version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
* <a id="notebook"></a>`notebook` _optional List\[Union\[CollectionEntry | RDF\]\]_ 
  1. _optional Union\[CollectionEntry | RDF\]_ 
  1. _CollectionEntry_   is a Dict with the following keys:
  * <a id="notebook:id_"></a>`id_` _String_ 
  * <a id="notebook:source"></a>`source` _URL→URI_ 
  * <a id="notebook:links"></a>`links` _optional List\[String\]_ 
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
