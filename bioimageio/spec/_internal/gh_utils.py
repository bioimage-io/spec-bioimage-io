import inspect
import os

from loguru import logger


def set_github_warning(title: str, message: str):
    if (
        not os.getenv("GITHUB_ACTIONS")
        or (current_frame := inspect.currentframe()) is None
        or (caller_frame := current_frame.f_back) is None
    ):
        # fallback to regular logging
        logger.opt(depth=1).warning("{}: {}", title, message)
        return

    frameinfo = inspect.getframeinfo(caller_frame)
    frameinfo.lineno

    # log according to
    # https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions#setting-a-warning-message
    print(
        f"::warning file={frameinfo.filename},"
        + f"line={frameinfo.lineno},endLine={frameinfo.lineno+1},"
        + f"title={title}::{message}"
    )
