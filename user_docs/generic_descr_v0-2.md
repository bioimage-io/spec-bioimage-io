# bioimage.io generic specification
Specification of the fields used in a generic bioimage.io-compliant resource description file (RDF).

An RDF is a YAML file that describes a resource such as a model, a dataset, or a notebook.
Note that those resources are described with a type-specific RDF.
Use this generic resource description, if none of the known specific types matches your resource.

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

## `type`<sub> str</sub> ≝ `generic`




## `format_version`<sub> Literal[0.2.4]</sub> ≝ `0.2.4`




## `description`<sub> str</sub>




## `name`<sub> str</sub>




## `attachments`<sub> Optional[AttachmentsDescr]</sub> ≝ `None`


<details><summary>Optional[AttachmentsDescr]

</summary>


**AttachmentsDescr:**
### `attachments.files`<sub> Sequence</sub> ≝ `[]`


<details><summary>Sequence[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Sequence of Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f4d2fbb5a80>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

</details>

## `authors`<sub> Sequence[Author]</sub> ≝ `[]`


<details><summary>Sequence[Author]

</summary>


**Author:**
### `authors.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




### `authors.i.email`<sub> Optional[Email]</sub> ≝ `None`




### `authors.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#authorsiorcid) '0000-0001-2345-6789'


Optional[_internal.validated_string.ValidatedString[Annotated[str, AfterValidator]]]

### `authors.i.name`<sub> str</sub>




### `authors.i.github_user`<sub> Optional[str]</sub> ≝ `None`




</details>

## `badges`<sub> Sequence[BadgeDescr]</sub> ≝ `[]`


<details><summary>Sequence[BadgeDescr]

</summary>


**BadgeDescr:**
### `badges.i.label`<sub> str</sub>

[*Example:*](#badgesilabel) 'Open in Colab'



### `badges.i.icon`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`

[*Example:*](#badgesiicon) 'https://colab.research.google.com/assets/colab-badge.svg'



### `badges.i.url`<sub> _internal.url.HttpUrl</sub>

[*Example:*](#badgesiurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



</details>

## `cite`<sub> Sequence[CiteEntry]</sub> ≝ `[]`


<details><summary>Sequence[CiteEntry]

</summary>


**CiteEntry:**
### `cite.i.text`<sub> str</sub>




### `cite.i.doi`<sub> Optional</sub> ≝ `None`



Optional[_internal.validated_string.ValidatedString[Annotated[str, StringConstraints]]]

### `cite.i.url`<sub> Optional[str]</sub> ≝ `None`




</details>

## `config`<sub> Dict[str, YamlValue]</sub> ≝ `{}`

[*Example:*](#config) {'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}



## `covers`<sub> Sequence</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')
[*Example:*](#covers) 'cover.png'

<details><summary>Sequence[Union[_internal.url.HttpUrl, Path*, _internal.io.RelativeFilePath]*]

</summary>

Sequence of Union of
- _internal.url.HttpUrl
- Path (PathType(path_type='file'); Predicate(func=<function PurePath.is_absolute at 0x7f4d32e41940>))
- _internal.io.RelativeFilePath

(WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg'), case_sensitive=False); PlainSerializer(func=<function _package at 0x7f4d2fbb5a80>, return_type=PydanticUndefined, when_used='unless-none'))

</details>

## `documentation`<sub> Optional</sub> ≝ `None`

[*Examples:*](#documentation) ['https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md', '…']

<details><summary>Optional[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*]

</summary>

Optional[Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])

(AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f4d2fbb5a80>, return_type=PydanticUndefined, when_used='unless-none'))]

</details>

## `download_url`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`




## `git_repo`<sub> Optional[str]</sub> ≝ `None`

[*Example:*](#git_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



## `icon`<sub> Union</sub> ≝ `None`


<details><summary>Union[Union[Path*, _internal.io.RelativeFilePath, _internal.url.HttpUrl, Url*]*, str*, None]

</summary>

Union of
- Union of
  - Path (PathType(path_type='file'))
  - _internal.io.RelativeFilePath
  - _internal.url.HttpUrl
  - Url (max_length=2083 allowed_schemes=['http', 'https'])

  (AfterValidator(wo_special_file_name); PlainSerializer(func=<function _package at 0x7f4d2fbb5a80>, return_type=PydanticUndefined, when_used='unless-none'))
- str (Len(min_length=1, max_length=2))
- None


</details>

## `id`<sub> Optional</sub> ≝ `None`



Optional[_internal.validated_string.ValidatedString[Annotated[str, MinLen, Annotated[TypeVar, Predicate], Predicate]]]

## `id_emoji`<sub> Optional</sub> ≝ `None`



Optional[str (Len(min_length=1, max_length=1))]

## `license`<sub> Union</sub> ≝ `None`

[*Examples:*](#license) ['CC-BY-4.0', 'MIT', 'BSD-2-Clause']


Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId, str, None]

## `links`<sub> Sequence[str]</sub> ≝ `[]`

[*Example:*](#links) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



## `maintainers`<sub> Sequence[Maintainer]</sub> ≝ `[]`


<details><summary>Sequence[Maintainer]

</summary>


**Maintainer:**
### `maintainers.i.affiliation`<sub> Optional[str]</sub> ≝ `None`




### `maintainers.i.email`<sub> Optional[Email]</sub> ≝ `None`




### `maintainers.i.orcid`<sub> Optional</sub> ≝ `None`

[*Example:*](#maintainersiorcid) '0000-0001-2345-6789'


Optional[_internal.validated_string.ValidatedString[Annotated[str, AfterValidator]]]

### `maintainers.i.name`<sub> Optional</sub> ≝ `None`



Optional[str (AfterValidator(_remove_slashes))]

### `maintainers.i.github_user`<sub> str</sub>




</details>

## `rdf_source`<sub> Union</sub> ≝ `None`


<details><summary>Union[Path*, ..., None]

</summary>

Union of
- Path (PathType(path_type='file'))
- _internal.io.RelativeFilePath
- _internal.url.HttpUrl
- Url (max_length=2083 allowed_schemes=['http', 'https'])
- None


</details>

## `source`<sub> Optional[_internal.url.HttpUrl]</sub> ≝ `None`




## `tags`<sub> Sequence[str]</sub> ≝ `[]`

[*Example:*](#tags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



## `uploader`<sub> Optional[Uploader]</sub> ≝ `None`


<details><summary>Optional[Uploader]

</summary>


**Uploader:**
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
### `badges.i.label`
Open in Colab
### `badges.i.icon`
https://colab.research.google.com/assets/colab-badge.svg
### `badges.i.url`
https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb
### `config`
{'bioimageio': {'my_custom_key': 3837283, 'another_key': {'nested': 'value'}}, 'imagej': {'macro_dir': 'path/to/macro/file'}}
### `covers`
cover.png
### `documentation`
- https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_descriptions/models/unet2d_nuclei_broad/README.md
- README.md

### `git_repo`
https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad
### `license`
- CC-BY-4.0
- MIT
- BSD-2-Clause

### `links`
('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')
### `maintainers.i.orcid`
0000-0001-2345-6789
### `tags`
('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')
