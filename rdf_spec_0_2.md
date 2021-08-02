# BioImage.IO Resource Description File Specification 0.2.0
This specification defines the fields used in a general BioImage.IO-compliant resource description file (`RDF`).
An RDF is stored as a YAML file and describes resources such as models, datasets, applications and notebooks. 
Note that models are described with an extended Model RDF specification.

The RDF contains mandatory and optional fields. In the following description, optional fields are indicated by 
_optional_. _optional*_ with an asterisk indicates the field is optional depending on the value in another field.
If no specialized RDF exists for the specified type (like model RDF for type='model') additional fields may be 
specified.

* `format_version` _String_ Version of the BioImage.IO Resource Description File Specification used.The current general format version described here is 0.2.0. Note: The general RDF format is not to be confused with specialized RDF format like the Model RDF format.
* `cite` _List\[CiteEntry\]_ A citation entry or list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used. List\[CiteEntry\] is a Dict with the following keys:
  * `text` _String_ 
  * `doi` _optional* String_ 
  * `url` _optional* String_ 
* `description` _String_ A string containing a brief description.
* `documentation` _RelativeLocalPath→Path_ Relative path to file with additional documentation in markdown. This means: 1) only relative file path is allowed 2) the file must be in markdown format with `.md` file name extension 3) URL is not allowed. It is recommended to use `README.md` as the documentation name.
* `name` _String_ name of the resource, a human-friendly name
* `tags` _List\[String\]_ A list of tags.
* `type` _String_ 
* `attachments` _optional Dict\[String, List\[Union\[URI→String | Raw\]\]\]_ 
  1. _optional* List\[Union\[URI→String | Raw\]\]_ Dictionary of text keys and URI (or a list of URI) values to additional, relevant files. E.g. we can place a list of URIs under the `files` to list images and other files that this resource depends on.
    1. _optional Union\[URI→String | Raw\]_ 
      1. _optional URI→String_ 
      1. _optional Raw_ 
* `authors` _optional List\[Union\[Author | String\]\]_ A list of authors. The authors are the creators of the specifications and the primary points of contact.
  1. _optional Union\[Author | String\]_ 
    1. _Author_   is a Dict with the following keys:
      * `name` _String_ Full name.
      * `affiliation` _optional String_ Affiliation.
      * `orcid` _optional String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
    1. _optional String_ 
* `badges` _optional List\[Badge\]_ a list of badges
  1. _Badge_ Custom badge Badge is a Dict with the following keys:Custom badge
    * `label` _String_ e.g. 'Open in Colab'
    * `icon` _optional String_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
    * `url` _optional URI→String_ e.g. 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'
* `config` _optional Dict\[Any, Any\]_ 
* `covers` _optional List\[URI→String\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'https'.Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
* `download_url` _optional String_ recommended url to the zipped file if applicable
* `git_repo` _optional String_ A url to the git repository, e.g. to Github or Gitlab.
* `icon` _optional String_ an icon for the resource
* `license` _optional String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
* `links` _optional List\[String\]_ links to other bioimage.io resources
* `source` _optional URI→String_ url to the source of the resource
* `version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
