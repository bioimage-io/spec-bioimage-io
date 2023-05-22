import os
from pathlib import Path
from typing import Optional

import pytest

from bioimageio.spec.shared.raw_nodes import URI


def mock_download(uri: URI, output: Optional[os.PathLike] = None, pbar=None):
    return Path(__file__).resolve()


@pytest.mark.parametrize(
    "src",
    [
        "https://example.com/fake",
        Path(__file__),
        __file__,
        URI("https://example.com/fake"),
    ],
)
def test_get_resolved_source_path(src):
    from bioimageio.spec.shared import get_resolved_source_path

    import bioimageio.spec

    bioimageio.spec.shared._resolve_source._download_url = mock_download
    res = get_resolved_source_path(src, root_path=Path(__file__).parent)
    assert isinstance(res, Path)
    assert res.exists()
    assert res == Path(__file__).resolve()
