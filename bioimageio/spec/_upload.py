from typing import Union
from zipfile import ZipFile

import httpx
from loguru import logger

from bioimageio.spec._io import load_description

from ._description import (
    InvalidDescr,
    ResourceDescr,
    build_description,
)
from ._internal._settings import settings
from ._internal.common_nodes import ResourceDescrBase
from ._internal.io import BioimageioYamlContent, get_reader
from ._internal.io_basics import BIOIMAGEIO_YAML
from ._package import get_resource_package_content
from .common import PermissiveFileSource


def upload(
    source: Union[PermissiveFileSource, ZipFile, ResourceDescr, BioimageioYamlContent],
    /,
) -> Union[ResourceDescr, InvalidDescr]:
    """Upload a new resource description (version) to the hypha server to be shared at bioimage.io.
    To edit an existing resource **version**, please login to https://bioimage.io and use the web interface.

    Args:
        source: The resource description to upload.

    Returns:
        The uploaded resource description.
    """

    if settings.hypha_upload_token is None:
        raise ValueError(
            """
Upload token is not set. Please set BIOIMAGEIO_HYPHA_UPLOAD_TOKEN in your environment variables.
By setting this token you agree to our terms of service at https://bioimage.io/#/toc.

How to obtain a token:
    1. Login to https://bioimage.io
    2. Generate a new token at https://bioimage.io/#/api?tab=hypha-rpc
"""
        )

    if isinstance(source, ResourceDescrBase):
        # If source is already a ResourceDescr, we can use it directly
        descr = source
    elif isinstance(source, dict):
        descr = build_description(source)
    else:
        descr = load_description(source)

    if isinstance(descr, InvalidDescr):
        raise ValueError("Uploading invalid resource descriptions is not allowed.")

    content = get_resource_package_content(descr)

    manifest = content.pop(BIOIMAGEIO_YAML)
    assert isinstance(manifest, dict)

    # Create new model
    r = httpx.post(
        settings.hypha_upload,
        json={
            "parent_id": "bioimage-io/bioimage.io",
            "alias": descr.id,
            "type": descr.type,
            "manifest": manifest,
            "version": (
                artifact_version := (
                    "stage" if descr.version is None else str(descr.version)
                )
            ),
        },
        headers=(
            headers := {
                "Authorization": f"Bearer {settings.hypha_upload_token}",
                "Content-Type": "application/json",
            }
        ),
    )

    response = r.json()
    artifact_id = response.get("id")
    if artifact_id is None:
        raise RuntimeError(f"Upload did not return resource id: {response}")
    else:
        logger.info("Uploaded resource description {}", artifact_id)

    for file_name, file_source in content.items():
        assert not isinstance(file_source, dict)
        # Get upload URL for a file
        response = httpx.post(
            settings.hypha_upload.replace("/create", "/put_file"),
            json={
                "artifact_id": artifact_id,
                "version": artifact_version,  # TODO: is version valid here?
                "file_path": file_name,
            },
            headers=headers,
        )
        upload_url = response.json()

        # Upload file to the provided URL
        reader = get_reader(file_source)
        response = httpx.put(
            upload_url,
            files={file_name: reader},  # pyright: ignore[reportArgumentType]
            # TODO: follow up on https://github.com/encode/httpx/discussions/3611
            headers={"Content-Type": ""},  # Important for S3 uploads
        )
        logger.info("Uploaded '{}' successfully", file_name)

    # Update model status
    manifest["status"] = "request-review"
    response = httpx.post(
        settings.hypha_upload.replace("/create", "/edit"),
        json={
            "artifact_id": artifact_id,
            "version": artifact_version,
            "manifest": manifest,
        },
        headers=headers,
    )
    logger.info(
        "Updated status of {}/{} to 'request-review'", artifact_id, artifact_version
    )

    return load_description(f"{artifact_id}/{artifact_version}")
