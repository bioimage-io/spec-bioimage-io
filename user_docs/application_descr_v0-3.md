# bioimage.io application specification
Bioimage.io description of an application.
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

## `type`<sub> Literal[application]</sub> ≝ `application`




## `format_version`<sub> Literal[0.3.0]</sub> ≝ `0.3.0`




## `authors`<sub> Sequence[generic.v0_3.Author]</sub>


<details><summary>Sequence[generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
### `authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




### `authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




### `authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#authorsiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `authors.i.name`<sub> str</sub>




### `authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

## `cite`<sub> Sequence[generic.v0_3.CiteEntry]</sub>


<details><summary>Sequence[generic.v0_3.CiteEntry]

</summary>


**generic.v0_3.CiteEntry:**
### `cite.i.text`<sub> str</sub>




### `cite.i.doi`<sub> Optional[_internal.types.Doi]</sub> ≝ `None`




### `cite.i.url`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`




</details>

## `description`<sub> str</sub>




## `license`<sub> Union</sub>

[*Examples:*](#license) ['CC0-1.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId]

## `name`<sub> str</sub>




## `attachments`<sub> Sequence[_internal.io.FileDescr]</sub> ≝ `[]`


<details><summary>Sequence[_internal.io.FileDescr]

</summary>


**_internal.io.FileDescr:**
### `attachments.i.source`<sub> Union</sub>


<details><summary>Union[Path*, _internal.url.HttpUrl, _internal.io.RelativeFilePath, Url*]

</summary>

Union of
- Path (PathType(path_type='file'))
- _internal.url.HttpUrl
- _internal.io.RelativeFilePath
- Url (max_length=2083 allowed_schemes=['http', 'https'])


</details>

### `attachments.i.sha256`<sub> Optional</sub> ≝ `None`



Optional[_internal.io_basics.Sha256]

</details>

## `badges`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[generic.v0_2.BadgeDescr]

</summary>


**generic.v0_2.BadgeDescr:**
### `badges.i.label`<sub> str</sub>

[*Example:*](#badgesilabel) 'Open in Colab'



### `badges.i.icon`<sub> Union</sub> ≝ `None`

[*Example:*](#badgesiicon) 'https://colab.research.google.com/assets/colab-badge.svg'

<details><summary>Union[Union[Path*, _internal.io.RelativeFilePath]*, _internal.url.HttpUrl, Url*, None]

</summary>

Union of
- Union[Path (PathType(path_type='file')), _internal.io.RelativeFilePath]
  (AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7fb36fe2dee0>, return_type=PydanticUndefined, when_used='unless-none'))
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])
- None


</details>

### `badges.i.url`<sub> _internal.url.HttpUrl</sub>

[*Example:*](#badgesiurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



</details>

## `config`<sub> Dict[str, YamlValue]</sub> ≝ `{}`

[*Example:*](#config) {'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}



## `covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1 or 1:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')

<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'); Predicate(func=<function PurePath.is_absolute at 0x7fb373363ba0>))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl

(union_mode='left_to_right'; WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg', '.tif', '.tiff'), case_sensitive=False); PlainSerializer(func=<function _package at 0x7fb36fe2dee0>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

## `documentation`<sub> Optional</sub> ≝ `None`

[*Examples:*](#documentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']

<details><summary>Optional[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl]*]

</summary>

Optional[Union of
- Path (PathType(path_type='file'); Predicate(func=<function PurePath.is_absolute at 0x7fb373363ba0>))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl

(union_mode='left_to_right'; AfterValidator(_validate_md_suffix); PlainSerializer(func=<function _package at 0x7fb36fe2dee0>, return_type=PydanticUndefined, when_used='unless-none'))]

</details>

## `git_repo`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`

[*Example:*](#git_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



## `icon`<sub> Union</sub> ≝ `None`


<details><summary>Union[str*, Union[Path*, _internal.url.HttpUrl, _internal.io.RelativeFilePath, Url*]*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- Union of
  - Path (PathType(path_type='file'))
  - _internal.url.HttpUrl
  - _internal.io.RelativeFilePath
  - Url (max_length=2083 allowed_schemes=['http', 'https'])

  (union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7fb36fe2dee0>, return_type=PydanticUndefined, when_used='unless-none'))
- None


</details>

## `id`<sub> Optional[ApplicationId]</sub> ≝ `None`




## `id_emoji`<sub> Optional</sub> ≝ `None`



Optional[str (Len(min_length=1, max_length=1))]

## `links`<sub> Sequence[str]</sub> ≝ `[]`

[*Example:*](#links) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



## `maintainers`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[generic.v0_3.Maintainer]

</summary>


**generic.v0_3.Maintainer:**
### `maintainers.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




### `maintainers.i.email`<sub> Optional[Email]</sub> ≝ `None`




### `maintainers.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#maintainersiorcid) '0000-0001-2345-6789'


Optional[_internal.types.OrcidId]

### `maintainers.i.name`<sub> Optional</sub> ≝ `None`



Optional[str (Predicate(_has_no_slash))]

### `maintainers.i.github_user`<sub> str</sub>




</details>

## `parent`<sub> Optional[ApplicationId]</sub> ≝ `None`




## `source`<sub> Optional</sub> ≝ `None`
URL or path to the source of the application

<details><summary>Optional[Union[Path*, _internal.url.HttpUrl, _internal.io.RelativeFilePath, Url*]*]

</summary>

Optional[Union of
- Path (PathType(path_type='file'))
- _internal.url.HttpUrl
- _internal.io.RelativeFilePath
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(union_mode='left_to_right'; AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7fb36fe2dee0>, return_type=PydanticUndefined, when_used='unless-none'))]

</details>

## `tags`<sub> Sequence[str]</sub> ≝ `[]`

[*Example:*](#tags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



## `uploader`<sub> Optional[generic.v0_2.Uploader]</sub> ≝ `None`


<details><summary>Optional[generic.v0_2.Uploader]

</summary>


**generic.v0_2.Uploader:**
### `uploader.email`<sub> Email</sub>




### `uploader.name`<sub> Optional</sub> ≝ `None`



Optional[str (AfterValidator(_remove_slashes))]

</details>

## `version`<sub> Optional</sub> ≝ `None`



Optional[_internal.version_type.Version]

## `version_number`<sub> Optional[int]</sub> ≝ `None`




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
