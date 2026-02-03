import os
import tempfile
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
def get_huggingface_api():
    from huggingface_hub import HfApi

    return HfApi(library_name="bioimageio.spec", library_version=VERSION)


def push_to_hub(
    descr: ModelDescr,
    username_or_org: str,
    *,
    prep_dir: Optional[Union[os.PathLike[str], str]] = None,
    prep_only_no_upload: bool = False,
):
    """Push the model package described by `descr` to the Hugging Face Hub.

    Args:
        descr: The model description to be pushed to the Hugging Face Hub.
        username_or_org: The Hugging Face username or organization under which the model package will be uploaded.
            The model ID from `descr.id` will be used as the repository name.
        prep_dir: Optional path to an empty directory where the model package will be prepared before uploading.
        prep_only_no_upload: If `True`, only prepare the model package in `prep_dir` without uploading it to the Hugging Face Hub.
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
):
    from huggingface_hub import create_branch, list_repo_refs

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

    if not prep_only:
        logger.info(f"Pushing model '{descr.id}' to Hugging Face Hub")

        api = get_huggingface_api()
        repo_url = api.create_repo(repo_id=repo_id, exist_ok=True, repo_type="model")
        logger.info(f"Created repository at {repo_url}")

        version_tag = f"v{descr.version}" if descr.version else None
        existing_refs = list_repo_refs(
            repo_id=repo_id, repo_type="model", include_pull_requests=True
        )
        has_draft_ref = False
        for ref in existing_refs.branches + existing_refs.tags:
            if ref.name == version_tag:
                raise ValueError(
                    f"Version '{version_tag}' already exists in the repository."
                )
            if ref.name == "draft":
                has_draft_ref = True

        if descr.version is None:
            base_revision = "draft"
            if not has_draft_ref:
                create_branch(repo_id=repo_id, branch="draft", repo_type="model")
        else:
            base_revision = "main"

        commit_info = api.upload_folder(
            repo_id=repo_id,
            revision=base_revision,
            folder_path=prep_dir,
            delete_patterns=[f"{sf}/*" for sf in referenced_files_subfolders]
            + ["package/*"],
            commit_message=commit_message,
            commit_description=commit_description,
        )
        logger.info(f"Created commit {commit_info.commit_url}")
        if descr.version:
            api.create_tag(
                repo_id=repo_id,
                tag=str(descr.version),
                revision=commit_info.oid,
                tag_message=descr.version_comment,
                exist_ok=False,
            )
