import pytest
from pathlib import Path

from bioimageio.spec.shared.raw_nodes import URI


@pytest.mark.parametrize(
    "src",
    [
        "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/rdf.yaml",
        Path(__file__),
        __file__,
        URI(
            "https://raw.githubusercontent.com/bioimage-io/spec-bioimage-io/main/example_specs/models/unet2d_nuclei_broad/rdf.yaml"
        ),
    ],
)
def test_get_resolved_source_path(src):
    from bioimageio.spec.shared import get_resolved_source_path

    res = get_resolved_source_path(src, root_path=Path(__file__).parent)
    assert isinstance(res, Path)
    assert res.exists()
