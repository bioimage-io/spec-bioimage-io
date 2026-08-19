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
| `field` ≝ `default` | Default field values are indicated after '≝' and make a field optional. However, `type` and `format_version` alwyas need to be set for resource descriptions written as YAML files and determine which bioimage.io specification applies. They are optional only when creating a resource description in Python code using the appropriate, `type` and `format_version` specific class (here: [bioimageio.spec.notebook.v0_3.NotebookDescr](https://bioimage-io.github.io/spec-bioimage-io/bioimageio/spec/notebook/v0_3.html#NotebookDescr)).|
| `field` ≝ 🡇 | Default field value is not displayed in-line, but in the code block below. |
are included when packaging the resource to a .zip archive. The resource description YAML file (RDF) is always included as well as 'rdf.yaml'. |

## `type`<sub> Literal[notebook]</sub>




## `format_version`<sub> Literal[0.3.4]</sub>
The **format** version of this resource specification



## `name`<sub> str</sub>
A human-friendly name of the resource description.
May only contains letters, digits, underscore, minus, parentheses and spaces.



## `source`<sub> Union</sub>
The Jupyter notebook

<details><summary>Union[_internal.url.HttpUrl*, Path*, _internal.io.RelativeFilePath*]

</summary>

Union of
- _internal.url.HttpUrl (WithSuffix(suffix='.ipynb', case_sensitive=True, allow_any_parent_suffix=False))
- Path (PathType(path_type='file'); ; WithSuffix(suffix='.ipynb', case_sensitive=True, allow_any_parent_suffix=False))
- _internal.io.RelativeFilePath (WithSuffix(suffix='.ipynb', case_sensitive=True, allow_any_parent_suffix=False))


</details>

## `attachments`<sub> list</sub> ≝ `[]`
file attachments

<details><summary>list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7f7e7c08c400>), WrapSerializer(func=<function package_file_descr_serializer at 0x7f7e6dbf1080>, return_type=PydanticUndefined, when_used='unless-none')]]

</summary>

list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7f7e7c08c400>), WrapSerializer(func=<function package_file_descr_serializer at 0x7f7e6dbf1080>, return_type=PydanticUndefined, when_used='unless-none')]]

**_internal.io.FileDescr:**
### `attachments.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `attachments.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

## `authors`<sub> list</sub> ≝ `[]`
The authors are the creators of this resource description and the primary points of contact.

<details><summary>list[bioimageio.spec.generic.v0_3.Author]

</summary>


**generic.v0_3.Author:**
### `authors.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



### `authors.email`<sub> Email | None</sub> ≝ `None`
Email



### `authors.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#authorsorcid) '0000-0001-2345-6789'



### `authors.name`<sub> str</sub>




### `authors.github_user`<sub> str | None</sub> ≝ `None`




</details>

## `badges`<sub> list</sub> ≝ `[]`
badges associated with this resource

<details><summary>list[bioimageio.spec.generic.v0_2.BadgeDescr]

</summary>


**generic.v0_2.BadgeDescr:**
### `badges.label`<sub> str</sub>
badge label to display on hover
[*Example:*](#badgeslabel) 'Open in Colab'



### `badges.icon`<sub> Union</sub> ≝ `None`
badge icon (included in bioimage.io package if not a URL)
[*Example:*](#badgesicon) 'https://colab.research.google.com/assets/colab-badge.svg'

<details><summary>Union[Union[Path*, _internal.io.RelativeFilePath]*, _internal.url.HttpUrl, pydantic.networks.HttpUrl, None]

</summary>

Union of
- Union[Path (PathType(path_type='file'); ), _internal.io.RelativeFilePath]
  (AfterValidator(wo_special_file_name); PrettyPlainSerializer(func=<function _package_serializer at 0x7f7e6db37ec0>, return_type=PydanticUndefined, when_used='unless-none'))
- _internal.url.HttpUrl
- pydantic.networks.HttpUrl
- None


</details>

### `badges.url`<sub> _internal.url.HttpUrl</sub>
target URL
[*Example:*](#badgesurl) 'https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb'



</details>

## `cite`<sub> list</sub> ≝ `[]`
citations

<details><summary>list[bioimageio.spec.generic.v0_3.CiteEntry]

</summary>


**generic.v0_3.CiteEntry:**
### `cite.text`<sub> str</sub>
free text description



### `cite.doi`<sub> _internal.types.Doi | None</sub> ≝ `None`
A digital object identifier (DOI) is the prefered citation reference.
See https://www.doi.org/ for details.
Note:
    Either **doi** or **url** have to be specified.



### `cite.url`<sub> _internal.url.HttpUrl | None</sub> ≝ `None`
URL to cite (preferably specify a **doi** instead/also).
Note:
    Either **doi** or **url** have to be specified.



</details>

## `config`<sub> generic.v0_3.Config</sub> ≝ `bioimageio=BioimageioConfig()`
A field for custom configuration that can contain any keys not present in the RDF spec.
This means you should not store, for example, a GitHub repo URL in `config` since there is a `git_repo` field.
Keys in `config` may be very specific to a tool or consumer software. To avoid conflicting definitions,
it is recommended to wrap added configuration into a sub-field named with the specific domain or tool name,
for example:
```yaml
config:
    giraffe_neckometer:  # here is the domain name
        length: 3837283
        address:
            home: zoo
    imagej:              # config specific to ImageJ
        macro_dir: path/to/macro/file
```
If possible, please use [`snake_case`](https://en.wikipedia.org/wiki/Snake_case) for keys in `config`.
You may want to list linked files additionally under `attachments` to include them when packaging a resource.
(Packaging a resource means downloading/copying important linked files and creating a ZIP archive that contains
an altered rdf.yaml file with local references to the downloaded files.)

<details><summary>generic.v0_3.Config

</summary>


**generic.v0_3.Config:**
### `config.bioimageio`<sub> generic.v0_3.BioimageioConfig</sub> ≝ ``
bioimage.io internal metadata.



</details>

## `covers`<sub> list</sub> ≝ `[]`
Cover images. Please use an image smaller than 500KB and an aspect ratio width to height of 2:1 or 1:1.
The supported image formats are: ('.gif', '.jpeg', '.jpg', '.png', '.svg')
[*Example:*](#covers) ['cover.png']

<details><summary>list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7f7e7c08c400>), WrapSerializer(func=<function package_file_descr_serializer at 0x7f7e6dbf1080>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg'), case_sensitive=False, allow_any_parent_suffix=False)]]

</summary>

list[typing.Annotated[bioimageio.spec._internal.io.FileDescr, AfterValidator(func=<function wo_special_file_name at 0x7f7e7c08c400>), WrapSerializer(func=<function package_file_descr_serializer at 0x7f7e6dbf1080>, return_type=PydanticUndefined, when_used='unless-none'), WithSuffix(suffix=('.gif', '.jpeg', '.jpg', '.png', '.svg'), case_sensitive=False, allow_any_parent_suffix=False)]]

**_internal.io.FileDescr:**
### `covers.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `covers.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

## `description`<sub> str</sub> ≝ ``
A string containing a brief description.



## `documentation`<sub> Optional</sub> ≝ `None`
Additional model documentation.
The recommended documentation source file name is `README.md`. An `.md` suffix is mandatory.

<details><summary>Optional[_internal.io.FileDescr*]

</summary>

Optional[_internal.io.FileDescr
(AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7f7e6dbf1080>, return_type=PydanticUndefined, when_used='unless-none'); WithSuffix(suffix='.md', case_sensitive=True, allow_any_parent_suffix=False); )]

**_internal.io.FileDescr:**
### `documentation.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `documentation.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

## `git_repo`<sub> _internal.url.HttpUrl | None</sub> ≝ `None`
A URL to the Git repository where the resource is being developed.
[*Example:*](#git_repo) 'https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad'



## `icon`<sub> Union</sub> ≝ `None`
An icon for illustration, e.g. on bioimage.io

<details><summary>Union[str*, _internal.io.FileDescr*, None]

</summary>

Union of
- str (Len(min_length=1, max_length=2))
- _internal.io.FileDescr
  (AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7f7e6dbf1080>, return_type=PydanticUndefined, when_used='unless-none'))
- None


**_internal.io.FileDescr:**
### `icon.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `icon.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

## `id`<sub> NotebookId | None</sub> ≝ `None`
bioimage.io-wide unique resource identifier
assigned by bioimage.io; version **un**specific.



## `id_emoji`<sub> Optional</sub> ≝ `None`
UTF-8 emoji for display alongside the `id`.


Optional[str (Len(min_length=1, max_length=2); )]

## `license`<sub> Union</sub> ≝ `None`
A [SPDX license identifier](https://spdx.org/licenses/) or a custom license file.
[*Examples:*](#license) ['CC0-1.0', 'MIT', 'BSD-2-Clause']

<details><summary>Union[_internal.license_id.LicenseId, _internal.license_id.DeprecatedLicenseId, None, _internal.io.FileDescr*]

</summary>

Union of
- _internal.license_id.LicenseId
- _internal.license_id.DeprecatedLicenseId
- None
- _internal.io.FileDescr
  (AfterValidator(wo_special_file_name); WrapSerializer(func=<function package_file_descr_serializer at 0x7f7e6dbf1080>, return_type=PydanticUndefined, when_used='unless-none'))


**_internal.io.FileDescr:**
### `license.source`<sub> Union</sub>
FileSource: File source


Union[_internal.url.HttpUrl, _internal.io.RelativeFilePath, Path (PathType(path_type='file'); )]

### `license.sha256`<sub> _internal.io_basics.Sha256 | Non</sub> ≝ `None`
SHA256 hash value of the **source** file.


_internal.io_basics.Sha256 | None

</details>

## `links`<sub> list[str]</sub> ≝ `[]`
IDs of other bioimage.io resources
[*Example:*](#links) ('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')



## `maintainers`<sub> list</sub> ≝ `[]`
Maintainers of this resource.
If not specified, `authors` are maintainers and at least some of them has to specify their `github_user` name

<details><summary>list[bioimageio.spec.generic.v0_3.Maintainer]

</summary>


**generic.v0_3.Maintainer:**
### `maintainers.affiliation`<sub> str | None</sub> ≝ `None`
Affiliation



### `maintainers.email`<sub> Email | None</sub> ≝ `None`
Email



### `maintainers.orcid`<sub> _internal.types.OrcidId | None</sub> ≝ `None`
An [ORCID iD](https://support.orcid.org/hc/en-us/sections/360001495313-What-is-ORCID
) in hyphenated groups of 4 digits, (and [valid](
https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
) as per ISO 7064 11,2.)
[*Example:*](#maintainersorcid) '0000-0001-2345-6789'



### `maintainers.name`<sub> Optional</sub> ≝ `None`



Optional[str (Predicate(_has_no_slash))]

### `maintainers.github_user`<sub> str</sub>




</details>

## `parent`<sub> NotebookId | None</sub> ≝ `None`
The description from which this one is derived



## `tags`<sub> list[str]</sub> ≝ `[]`
Associated tags
[*Example:*](#tags) ('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')



## `uploader`<sub> generic.v0_2.Uploader | None</sub> ≝ `None`
The person who uploaded the model (e.g. to bioimage.io)

<details><summary>generic.v0_2.Uploader | None

</summary>


**generic.v0_2.Uploader:**
### `uploader.email`<sub> Email</sub>
Email



### `uploader.name`<sub> Optional</sub> ≝ `None`
name


Optional[str (AfterValidator(_remove_slashes))]

</details>

## `version`<sub> _internal.version_type.Version |</sub> ≝ `None`
The version of the resource following SemVer 2.0.


_internal.version_type.Version | None

## `version_comment`<sub> Optional</sub> ≝ `None`
A comment on the version of the resource.


Optional[str (MaxLen(max_length=512))]

# Example values
### `authors.orcid`
0000-0001-2345-6789
### `badges.label`
Open in Colab
### `badges.icon`
https://colab.research.google.com/assets/colab-badge.svg
### `badges.url`
https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/U-net_2D_ZeroCostDL4Mic.ipynb
### `covers`
['cover.png']
### `git_repo`
https://github.com/bioimage-io/spec-bioimage-io/tree/main/example_descriptions/models/unet2d_nuclei_broad
### `license`
- CC0-1.0
- MIT
- BSD-2-Clause

### `links`
('ilastik/ilastik', 'deepimagej/deepimagej', 'zero/notebook_u-net_3d_zerocostdl4mic')
### `maintainers.orcid`
0000-0001-2345-6789
### `tags`
('unet2d', 'pytorch', 'nucleus', 'segmentation', 'dsb2018')
