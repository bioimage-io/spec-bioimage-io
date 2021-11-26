# BioImage.IO Resource Description File Specification 0.2.0
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks. 
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by 
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be 
specified.

* <a id="format_version"></a>`format_version` _String_ Version of the BioImage.IO Resource Description File Specification used.The current general format version described here is 0.2.0. Note: The general RDF format is not to be confused with specialized RDF format like the Model RDF format.
* <a id="cite"></a>`cite` _List\[CiteEntry\]_ A citation entry or list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used. List\[CiteEntry\] is a Dict with the following keys:
  * <a id="cite:text"></a>`text` _String_ 
  * <a id="cite:doi"></a>`doi` _optional* String_ 
  * <a id="cite:url"></a>`url` _optional* String_ 
* <a id="description"></a>`description` _String_ A string containing a brief description.
* <a id="documentation"></a>`documentation` _RelativeLocalPath→Path_ Relative path to file with additional documentation in markdown. This means: 1) only relative file path is allowed 2) the file must be in markdown format with `.md` file name extension 3) URL is not allowed. It is recommended to use `README.md` as the documentation name.
* <a id="name"></a>`name` _String_ name of the resource, a human-friendly name
* <a id="tags"></a>`tags` _List\[String\]_ A list of tags.
* <a id="type"></a>`type` _String_ 
* <a id="attachments"></a>`attachments` _optional Dict\[String, List\[Union\[URI→String | Raw\]\]\]_ 
  1. _optional* List\[Union\[URI→String | Raw\]\]_ Dictionary of text keys and URI (or a list of URI) values to additional, relevant files. E.g. we can place a list of URIs under the `files` to list images and other files that this resource depends on.
  1. _optional Union\[URI→String | Raw\]_ 
  1. _optional URI→String_ 
  1. _optional Raw_ 
* <a id="authors"></a>`authors` _optional List\[Union\[Author | String\]\]_ A list of authors. The authors are the creators of the specifications and the primary points of contact.
  1. _optional Union\[Author | String\]_ 
  1. _Author_   is a Dict with the following keys:
  * <a id="authors:name"></a>`name` _String_ Full name.
  * <a id="authors:affiliation"></a>`affiliation` _optional String_ Affiliation.
  * <a id="authors:orcid"></a>`orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
  1. _optional String_ 
* <a id="badges"></a>`badges` _optional List\[Badge\]_ a list of badges
  1. _Badge_ Custom badge Badge is a Dict with the following keys:Custom badge
  * <a id="badges:label"></a>`label` _String_ e.g. 'Open in Colab'
  * <a id="badges:icon"></a>`icon` _optional String_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
  * <a id="badges:url"></a>`url` _optional Union\[URI→String | RelativeLocalPath→Path\]_ e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'
    1. _optional URI→String_ 
    1. _optional RelativeLocalPath→Path_ 
* <a id="config"></a>`config` _optional Dict\[Any, Any\]_ 
* <a id="covers"></a>`covers` _optional List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
  1. _optional Union\[URI→String | RelativeLocalPath→Path\]_ 
  1. _optional URI→String_ 
  1. _optional RelativeLocalPath→Path_ 
* <a id="download_url"></a>`download_url` _optional String_ recommended url to the zipped file if applicable
* <a id="git_repo"></a>`git_repo` _optional String_ A url to the git repository, e.g. to Github or Gitlab.
* <a id="icon"></a>`icon` _optional String_ an icon for the resource
* <a id="license"></a>`license` _optional String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
* <a id="links"></a>`links` _optional List\[String\]_ links to other bioimage.io resources
* <a id="source"></a>`source` _optional Union\[URI→String | RelativeLocalPath→Path\]_ url or local relative path to the source of the resource
  1. _optional URI→String_ 
  1. _optional RelativeLocalPath→Path_ 
* <a id="version"></a>`version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
