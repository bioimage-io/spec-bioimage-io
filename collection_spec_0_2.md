# BioImage.IO Collection Resource Description File Specification 0.2.2
This specification defines the fields used in a BioImage.IO-compliant resource description file (`RDF`) for describing collections of other resources.
These fields are typically stored in YAML files which we call Collection Resource Description Files or `collection RDFs`.

The collection RDF YAML file contains mandatory and optional fields. In the following description, optional fields are indicated by _optional_.
_optional*_ with an asterisk indicates the field is optional depending on the value in another field.

* <a id="format_version"></a>`format_version` _required String_ Version of the BioImage.IO Resource Description File Specification used.The current general format version described here is 0.2.2. Note: The general RDF format is not to be confused with specialized RDF format like the Model RDF format.
* <a id="description"></a>`description` _required String_ A string containing a brief description.
* <a id="name"></a>`name` _required String_ name of the resource, a human-friendly name
* <a id="type"></a>`type` _required String_ 
* <a id="attachments"></a>`attachments` _optional Attachments_ Additional unknown keys are allowed. Attachments is a Dict with the following keys:
  * <a id="attachments:files"></a>`files` _List\[Union\[URI→String | RelativeLocalPath→Path\]\]_ File attachments; included when packaging the resource.
* <a id="authors"></a>`authors` _List\[Author\]_ A list of authors. The authors are the creators of the specifications and the primary points of contact.
  1. _Author_   is a Dict with the following keys:
  * <a id="authors:affiliation"></a>`affiliation` _String_ Affiliation.
  * <a id="authors:email"></a>`email` _Email_ 
  * <a id="authors:github_user"></a>`github_user` _String_ GitHub user name.
  * <a id="authors:name"></a>`name` _String_ Full name.
  * <a id="authors:orcid"></a>`orcid` _String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
* <a id="badges"></a>`badges` _List\[Badge\]_ a list of badges
  1. _Badge_ Custom badge. Badge is a Dict with the following keys:Custom badge.
  * <a id="badges:label"></a>`label` _String_ e.g. 'Open in Colab'
  * <a id="badges:icon"></a>`icon` _String_ e.g. 'https://colab.research.google.com/assets/colab-badge.svg'
* <a id="cite"></a>`cite` _List\[CiteEntry\]_ A list of citation entries.
Each entry contains a mandatory `text` field and either one or both of `doi` and `url`.
E.g. the citation for the model architecture and/or the training data used.
  1. _CiteEntry_   is a Dict with the following keys:
  * <a id="cite:text"></a>`text` _String_ 
  * <a id="cite:doi"></a>`doi` _DOI→String_ 
  * <a id="cite:url"></a>`url` _String_ 
* <a id="collection"></a>`collection` _List\[CollectionEntry\]_ Collection entries. Each entry needs to specify a valid RDF with an id. Each collection entry RDF is based on the collection RDF itself, updated by rdf_source content if rdf_source is specified, and updated by any fields specified directly in the entry. In this context 'update' refers to overwriting RDF root fields by name.Except for the `id` field, which appends to the collection RDF `id` such that full_collection_entry_id=<collection_id>/<entry_id>
  1. _CollectionEntry_   is a Dict with the following keys:
* <a id="config"></a>`config` _optional YamlDict→Dict\[Any, Any\]_ 
* <a id="covers"></a>`covers` _List\[Union\[URL→URI | RelativeLocalPath→Path\]\]_ A list of cover images provided by either a relative path to the model folder, or a hyperlink starting with 'http[s]'. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1. The supported image formats are: 'jpg', 'png', 'gif'.
* <a id="download_url"></a>`download_url` _optional URL→URI_ optional url to download the resource from
* <a id="git_repo"></a>`git_repo` _optional URL→URI_ A url to the git repository, e.g. to Github or Gitlab.
* <a id="icon"></a>`icon` _optional String_ an icon for the resource
* <a id="id"></a>`id` _optional String_ Unique id within a collection of resources.
* <a id="license"></a>`license` _optional String_ A [SPDX license identifier](https://spdx.org/licenses/)(e.g. `CC-BY-4.0`, `MIT`, `BSD-2-Clause`). We don't support custom license beyond the SPDX license list, if you need that please send an Github issue to discuss your intentions with the community.
* <a id="links"></a>`links` _List\[String\]_ links to other bioimage.io resources
* <a id="maintainers"></a>`maintainers` _List\[Maintainer\]_ Maintainers of this resource.
  1. _Maintainer_   is a Dict with the following keys:
  * <a id="maintainers:affiliation"></a>`affiliation` _String_ Affiliation.
  * <a id="maintainers:email"></a>`email` _Email_ 
  * <a id="maintainers:github_user"></a>`github_user` _String_ GitHub user name.
  * <a id="maintainers:name"></a>`name` _String_ Full name.
  * <a id="maintainers:orcid"></a>`orcid` _String_ [orcid](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID) id in hyphenated groups of 4 digits, e.g. '0000-0001-2345-6789' (and [valid](https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier) as per ISO 7064 11,2.)
* <a id="tags"></a>`tags` _List\[String\]_ A list of tags.
* <a id="version"></a>`version` _optional StrictVersion→String_ The version number of the model. The version number format must be a string in `MAJOR.MINOR.PATCH` format following the guidelines in Semantic Versioning 2.0.0 (see https://semver.org/), e.g. the initial version number should be `0.1.0`.
