from pathlib import Path

import pytest


@pytest.mark.parametrize("obj_name", ["A_Class", "a_func"])
def test_flatten_source(obj_name: str, tmp_path: Path):
    from bioimageio.spec._flatten_source import generate_flat_source_from_object

    from .dummy_src.a import A_Class, a_func

    obj = {"A_Class": A_Class, "a_func": a_func}[obj_name]
    expected = {
        "A_Class": """# Auto-generated flat dependency file

# ===== From dummy_src/b.py =====
from pathlib import Path

class B_Class:
    p: Path = Path()


# ===== Exported object =====
class A_Class(B_Class):
    pass


""",
        "a_func": """# Auto-generated flat dependency file

# ===== From dummy_src/b.py =====
import numpy as np

def b_func():
    return np.zeros((2, 2))


# ===== Exported object =====
def a_func():
    return b_func()


""",
    }
    out_path = tmp_path / "flat.py"
    generate_flat_source_from_object(
        obj,
        known_third_party={"numpy", "torch"},
        output_file=out_path,
    )
    assert expected[obj_name] == out_path.read_text()
