import os
import tempfile
import warnings
from contextlib import nullcontext
from functools import cache
from pathlib import Path
from typing import Optional, Union

from loguru import logger

from bioimageio.spec import save_bioimageio_package_as_folder
from bioimageio.spec._internal.validation_context import get_validation_context
from bioimageio.spec.model.v0_5 import ModelDescr

from ._hf_card import create_huggingface_model_card
from ._version import VERSION


@cache
def get_huggingface_api():  # pragma: no cover
    from huggingface_hub import HfApi

    return HfApi(library_name="bioimageio.spec", library_version=VERSION)


def push_to_hub(
    descr: ModelDescr,
    username_or_org: str,
    *,
    prep_dir: Optional[Union[os.PathLike[str], str]] = None,
    prep_only_no_upload: bool = False,
    create_pr: Optional[bool] = None,
):
    """Push the model package described by `descr` to the Hugging Face Hub.

    Args:
        descr: The model description to be pushed to the Hugging Face Hub.
        username_or_org: The Hugging Face username or organization under which the model package will be uploaded.
            The model ID from `descr.id` will be used as the repository name.
        prep_dir: Optional path to an empty directory where the model package will be prepared before uploading.
        prep_only_no_upload: If `True`, only prepare the model package in `prep_dir` without uploading it
            to the Hugging Face Hub.
        create_pr: If `True`, create a pull request instead of committing directly
            to the 'main' or 'draft' branch when uploading the model package.
            Defaults to `True` if uploading to a model description with version (to the main branch),
            and `False` if uploading a model description without version (to the 'draft' branch).

    Examples:
        Upload a model description as a new version to the main branch
        (id and version must be set):

        >>> my_model_descr = ModelDescr(id="my-model-id", version="1.0", create_pr=False, ...)
        >>> push_to_hub(my_model_descr, "my_hf_username")

        Upload a model description as a draft to the 'draft' branch
        (id must be set; version must be None):

        >>> my_model_descr = ModelDescr(id="my-model-id", version=None, ...)
        >>> push_to_hub(my_model_descr, "my_hf_username")

    """

    if descr.id is None:
        raise ValueError("descr.id must be set to push to Hugging Face Hub.")
    repo_id = f"{username_or_org}/{descr.id}"

    if prep_dir is None:
        ctxt = tempfile.TemporaryDirectory(suffix="_" + repo_id.replace("/", "_"))
    elif Path(prep_dir).exists() and any(Path(prep_dir).iterdir()):
        raise ValueError("Provided `prep_dir` is not empty.")
        # TODO: implement resuming upload
        # prep_dir: If a non-empty folder is provided, it will be attempted to continue an interrupted upload.
        # logger.info(f"Continuing upload from {prep_dir}")
        # if prep_only_no_upload:
        #     raise ValueError("`prep_only_no_upload` is True but `prep_dir` is non-empty.")
    else:
        ctxt = nullcontext(prep_dir)

    with ctxt as pdir:
        _push_to_hub_impl(
            descr,
            repo_id=repo_id,
            prep_dir=Path(pdir),
            prep_only=prep_only_no_upload,
        )


def _push_to_hub_impl(
    descr: ModelDescr,
    *,
    repo_id: str,
    prep_dir: Path,
    prep_only: bool,
    create_pr: Optional[bool],
):
    readme, referenced_files = create_huggingface_model_card(descr, repo_id=repo_id)
    referenced_files_subfolders = {"images"}
    assert not (
        unexpected := [
            rf
            for rf in referenced_files
            if not any(rf.startswith(f"{sf}/") for sf in referenced_files_subfolders)
        ]
    ), f"unexpected folder of referenced files: {unexpected}"

    logger.info(f"Preparing model for upload at {prep_dir}.")
    prep_dir.mkdir(parents=True, exist_ok=True)
    _ = (prep_dir / "README.md").write_text(readme, encoding="utf-8")
    for img_name, img_data in referenced_files.items():
        image_path = prep_dir / img_name
        image_path.parent.mkdir(parents=True, exist_ok=True)
        _ = image_path.write_bytes(img_data)

    with get_validation_context().replace(file_name="bioimageio.yaml"):
        _ = save_bioimageio_package_as_folder(descr, output_path=prep_dir / "package")

    logger.info(f"Prepared model for upload at {prep_dir}")

    commit_message = f"Upload {descr.version or 'draft'} with bioimageio.spec {VERSION}"
    commit_description = (
        f"Version comment: {descr.version_comment}" if descr.version_comment else None
    )

    if not prep_only:  # pragma: no cover
        logger.info(f"Pushing model '{descr.id}' to Hugging Face Hub")

        api = get_huggingface_api()
        repo_url = api.create_repo(repo_id=repo_id, exist_ok=True, repo_type="model")
        logger.info(f"Created repository at {repo_url}")

        existing_refs = api.list_repo_refs(
            repo_id=repo_id, repo_type="model", include_pull_requests=True
        )
        has_draft_ref = False
        has_tag = False
        for ref in existing_refs.branches + existing_refs.tags:
            if ref.name == str(descr.version):
                has_tag = True
            if ref.name == "draft":
                has_draft_ref = True

        if descr.version is None:
            revision = "draft"
            if not has_draft_ref:
                api.create_branch(repo_id=repo_id, branch="draft", repo_type="model")
        else:
            revision = None

        if create_pr is None:
            # default to creating a PR if commiting to main branch,
            # commit directly to 'draft' branch
            create_pr = revision is None

        commit_info = api.upload_folder(
            repo_id=repo_id,
            revision=revision,
            folder_path=prep_dir,
            delete_patterns=[f"{sf}/*" for sf in referenced_files_subfolders]
            + ["package/*"],
            commit_message=commit_message,
            commit_description=commit_description,
            create_pr=create_pr,
        )
        logger.info(f"Created commit {commit_info.commit_url}")
        if descr.version is not None:
            if has_tag:
                warnings.warn(f"Moving existing version tag {descr.version}.")

            api.create_tag(
                repo_id=repo_id,
                tag=str(descr.version),
                revision=commit_info.oid,
                tag_message=descr.version_comment,
                exist_ok=True,
            )
