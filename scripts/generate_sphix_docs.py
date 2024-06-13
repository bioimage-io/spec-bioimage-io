import subprocess;
from pathlib import Path
import os

try:
    import sphinxcontrib.autodoc_pydantic # type: ignore
except ImportError as e:
    import sys
    print("You need to install 'autodoc_pydantic'. Try running \npip install autodoc_pydantic", file=sys.stdout)
    exit(1)

os.chdir(Path(__file__).parent.parent)
_ = subprocess.run(["sphinx-build", "-M", "html", "sphinx_docs/source", "sphinx_docs/build/"])
