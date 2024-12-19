# 
Bioimage.io description of a Jupyter notebook.
**General notes on this documentation:**
| symbol | explanation |
| --- | --- |
| `field`<sub>type hint</sub> | A fields's <sub>expected type</sub> may be shortened. If so, the abbreviated or full type is displayed below the field's description and can expanded to view further (nested) details if available. |
| Union[A, B, ...] | indicates that a field value may be of type A or B, etc.|
| Literal[a, b, ...] | indicates that a field value must be the specific value a or b, etc.|
| Type* := Type (restrictions) | A field Type* followed by an asterisk indicates that annotations, e.g. value restriction apply. These are listed in parentheses in the expanded type description. They are not always intuitively understandable and merely a hint at more complex validation.|
| \<type\>.v\<major\>_\<minor\>.\<sub spec\> | Subparts of a spec might be taken from another spec type or format version. |
| `field` ≝ `default` | Default field values are indicated after '≝' and make a field optional. However, `type` and `format_version` alwyas need to be set for resource descriptions written as YAML files and determine which bioimage.io specification applies. They are optional only when creating a resource description in Python code using the appropriate, `type` and `format_version` specific class.|
| `field` ≝ 🡇 | Default field value is not displayed in-line, but in the code block below. |
| ∈📦  | Files referenced in fields which are marked with '∈📦 ' are included when packaging the resource to a .zip archive. The resource description YAML file (RDF) is always included well as 'rdf.yaml'. |

## `type`<sub> Literal[notebook]</sub> ≝ `notebook`




## `format_version`<sub> Literal[0.3.0]</sub> ≝ `0.3.0`
The **format** version of this resource specification



## `authors`<sub> Sequence[generic.v0_3.Author]</sub>
The authors are the creators of this resource description and the primary points of contact.

<details><summary>Sequence[generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
### `authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



### `authors.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



### `authors.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#authorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `authors.i.name`<sub> str</sub>




### `authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

## `cite`<sub> Sequence[generic.v0_3.CiteEntry]</sub>
citations

<details><summary>Sequence[generic.v0_3.CiteEntry]

</summary>


**generic.v0_3.CiteEntry:**
### `cite.i.text`<sub> str</sub>
free text description



### `cite.i.doi`<sub> Optional[_internal.types.Doi]</sub> ≝ `None`
A digital object identifier (DOI) is the prefered citation reference.
See https://www.doi.org/ for details. (alternatively specify `url`)



### `cite.i.url`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`
URL to cite (preferably specify a `doi` instead)



</details>

## `description`<sub> str</sub>
A string containing a brief description.



## `license`<sub> Union</sub>
A [SPDX license identifier](https://spdx.org/licenses/).
We do not support custom license beyond the SPDX license list, if you need that please
[open a GitHub issue](https://github.com/bioimage-io/spec-bioimage-io/issues/new/choose)
to discuss your intentions with the community.
[*Examples:*](#license) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId]

## `name`<sub> str</sub>
A human-friendly name of the resource description.
May only contains letters, digits, underscore, minus, parentheses and spaces.



## `source`<sub> Union</sub>
The Jupyter notebook

<details><summary>Union[_internal.url.HttpUrl*, Path*, _internal.io.RelativeFilePath*]

</summary>

Union of
- _internal.url.HttpUrl (WithSuffix(suffix='.ipynb', case_sensitive=True))
- Path (PathType(path_type='file'); Predicate(is_absolute); ; WithSuffix(suffix='.ipynb', case_sensitive=True))
- _internal.io.RelativeFilePath (WithSuffix(suffix='.ipynb', case_sensitive=True))


</details>

## `attachments`<sub> Sequence[_internal.io.FileDescr]</sub> ≝ `[]`
file attachments

<details><summary>Sequence[_internal.io.FileDescr]

</summary>


**_internal.io.FileDescr:**
### `attachments.i.source`<sub> Union</sub>
∈📦 file source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `attachments.i.sha256`<sub> Optional</sub> ≝ `None`
SHA256 checksum of the source file


Optional[_internal.io_basics.Sha256]

</details>

## `badges`<sub> Sequence</sub> ≝ `[]`
badges associated with this resource

<details><summary>Sequence[generic.v0_2.BadgeDescr]

</summary>


**generic.v0_2.BadgeDescr:**
### `badges.i.label`<sub> str</sub>
badge label to display on hover
[*Example:*](#badgesilabel) 'Open in Colab'



### `badges.i.icon`<sub> Union</sub> ≝ `None`
badge icon
[*Example:*](#badgesiicon) 'https://colab.research.google.com/assets/colab-badge.svg'

<details><summary>Union[Union[Path*, _internal.io.RelativeFilePath]*, _internal.url.HttpUrl, Url*, None]

</summary>

Union of
- Union[Path (PathType(path_type='file'); ), _internal.io.RelativeFilePath]
  (AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f080bba0680>, return_type=PydanticUndefined, when_used='unless-none'))
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])
- None


</details>

### `badges.i.url`<sub> _internal.url.HttpUrl</sub>
target URL
[*Example:*](#badgesiurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



</details>

## `config`<sub> Dict[str, YamlValue]</sub> ≝ `{}`
A field for custom configuration that can contain any keys not present in the RDF spec.
This means you should not store, for example, a GitHub repo URL in `config` since there is a `git_repo` field.
Keys in `config` may be very specific to a tool or consumer software. To avoid conflicting definitions,
it is recommended to wrap added configuration into a sub-field named with the specific domain or tool name,
for example:
```yaml
config:
    bioimageio:  # here is the domain name
        my_custom_key: 3837283
        another_key:
            nested: value
    imagej:       # config specific to ImageJ
        macro_dir: path/to/macro/file
```
If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.
You may want to list linked files additionally under `attachments` to include them when packaging a resource.
(Packaging a resource means downloading/copying important linked files and creating a ZIP archive that contains
an altered rdf.yaml file with local references to the downloaded files.)
[*Example:*](#config) {'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}



## `covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1 or 1:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')

<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'); Predicate(is_absolute); )
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl

(union_mode='left_to_right'; WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False); PlainSerializer(func=<function _package at 0x7f080bba0680>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

## `documentation`<sub> Optional</sub> ≝ `None`
∈📦 URL or relative path to a markdown file encoded in UTF-8 with additional documentation.
The recommended documentation file name is `README.md`. An `.md` suffix is mandatory.
[*Examples:*](#documentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']

<details><summary>Optional[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl]*]

</summary>

Optional[Union of
- Path (PathType(path_type='file'); Predicate(is_absolute); )
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl

(union_mode='left_to_right'; AfterValidator(_validate_md_suffix); PlainSerializer(func=<function _package at 0x7f080bba0680>, return_type=PydanticUndefined, when_used='unless-none'))]

</details>

## `git_repo`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`
A URL to the Git repository where the resource is being developed.
[*Example:*](#git_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



## `icon`<sub> Union</sub> ≝ `None`
An icon for illustration, e.g. on bioimage.io

<details><summary>Union[str*, Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]
  (union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f080bba0680>, return_type=PydanticUndefined, when_used='unless-none'))
- None


</details>

## `id`<sub> Optional[NotebookId]</sub> ≝ `None`
bioimage.io-wide unique resource identifier
assigned by bioimage.io; version **un**specific.



## `id_emoji`<sub> Optional</sub> ≝ `None`
UTF-8 emoji for display alongside the `id`.


Optional[str (Len(min_length=1, max_length=2); )]

## `links`<sub> Sequence[str]</sub> ≝ `[]`
IDs of other bioimage.io resources
[*Example:*](#links) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



## `maintainers`<sub> Sequence</sub> ≝ `[]`
Maintainers of this resource.
If not specified, `authors` are maintainers and at least some of them has to specify their `github_user` name

<details><summary>Sequence[generic.v0_3.Maintainer]

</summary>


**generic.v0_3.Maintainer:**
### `maintainers.i.affiliation`<sub> Optional[str]</sub> ≝ `None`
Affiliation



### `maintainers.i.email`<sub> Optional[Email]</sub> ≝ `None`
Email



### `maintainers.i.orcid`<sub> Optional</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#maintainersiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `maintainers.i.name`<sub> Optional</sub> ≝ `None`



Optional[str (Predicate(_has_no_slash))]

### `maintainers.i.github_user`<sub> str</sub>




</details>

## `parent`<sub> Optional[NotebookId]</sub> ≝ `None`
The description from which this one is derived



## `tags`<sub> Sequence[str]</sub> ≝ `[]`
Associated tags
[*Example:*](#tags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



## `uploader`<sub> Optional[generic.v0_2.Uploader]</sub> ≝ `None`
The person who uploaded the model (e.g. to bioimage.io)

<details><summary>Optional[generic.v0_2.Uploader]

</summary>


**generic.v0_2.Uploader:**
### `uploader.email`<sub> Email</sub>
Email



### `uploader.name`<sub> Optional</sub> ≝ `None`
name


Optional[str (AfterValidator(_remove_slashes))]

</details>

## `version`<sub> Optional</sub> ≝ `None`
The version of the resource following SemVer 2.0.


Optional[_internal.version_type.Version]

# Example values
### `authors.i.orcid`
0000-0001-2345-6789
### `license`
- CC0-1.0
- MIT
- BSD-2-Clause

### `badges.i.label`
Open in Colab
### `badges.i.icon`
https://colab.research.google.com/assets/colab-badge.svg
### `badges.i.url`
https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb
### `config`
{'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}
### `documentation`
- https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md
- README.md

### `git_repo`
https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad
### `links`
('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')
### `maintainers.i.orcid`
0000-0001-2345-6789
### `tags`
('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')
