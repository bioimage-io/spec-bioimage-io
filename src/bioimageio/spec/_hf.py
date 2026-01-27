import os
from functools import cache
from pathlib import Path
from typing import Optional, Union

from loguru import logger

from bioimageio.spec.model.v0_5 import ModelDescr

from ._hf_card import create_hf_model_card
from ._version import VERSION


@cache
def get_hf_api():
    from huggingface_hub import HfApi

    return HfApi(library_name="bioimageio.spec", library_version=VERSION)


def push_to_hf(
    descr: ModelDescr,
    username_or_org: str,
    local_dry_run: Optional[Union[os.PathLike[str], str]] = None,
):
    """Push the model package described by `descr` to the Hugging Face Hub under the specified username or organization."""

    if descr.id is None:
        raise ValueError("descr.id must be set to push to Hugging Face Hub.")
    repo_id = f"{username_or_org}/{descr.id}"

    readme, images = create_hf_model_card(descr)
    if local_dry_run is not None:
        local_repo = Path(local_dry_run) / repo_id
        logger.info(
            f"Dry run: Saving to {local_repo} instead of pushing to Hugging Face Hub."
        )
        local_repo.mkdir(parents=True, exist_ok=True)
        _ = (local_repo / "README.md").write_text(readme, encoding="utf-8")
        for img_name, img_data in images.items():
            _ = (local_repo / img_name).write_bytes(img_data)

        logger.info(f"Dry run: Saved {local_repo}")
        return

    commit_message = descr.version_comment
    logger.info(f"Pushing model package '{descr.id}' to Hugging Face Hub...")

    # api = get_hf_api()

    # api.create_repo(repo_id=descr.id, token=token, exist_ok=True)
    # api.upload_file(
    #     path_or_fileobj=model_card,
    #     path_in_repo="README.md",
    #     repo_id=repo_id,
    #     token=token,
    #     commit_message=commit_message,
    # )


# def load_from_hf
