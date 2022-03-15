import json
from pathlib import Path
from setuptools import find_namespace_packages, setup

# Get the long description from the README file
ROOT_DIR = Path(__file__).parent.resolve()
long_description = (ROOT_DIR / "README.md").read_text(encoding="utf-8")
VERSION_FILE = ROOT_DIR / "bioimageio" / "spec" / "VERSION"
VERSION = json.loads(VERSION_FILE.read_text(encoding="utf-8"))["version"]


setup(
    name="bioimageio.spec",
    version=VERSION,
    description="Parser and validator library for BioImage.IO specifications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bioimage-io/spec-bioimage-io",
    author="Bioimage Team",
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_namespace_packages(exclude=["tests"]),  # Required
    install_requires=[
        "marshmallow-jsonschema",
        "marshmallow-union",
        "marshmallow>=3.6.0,<4.0",
        "numpy",
        "packaging>=17.0",
        "requests;platform_system!='Emscripten'",
        "ruamel.yaml;platform_system!='Emscripten'",
        "tqdm;platform_system!='Emscripten'",
        "typer",
        "typing-extensions",
    ],
    entry_points={"console_scripts": ["bioimageio = bioimageio.spec.__main__:app"]},
    extras_require={"test": ["pytest", "tox", "mypy"], "dev": ["pre-commit"]},
    scripts=[
        "scripts/generate_json_specs.py",
        "scripts/generate_processing_docs.py",
        "scripts/generate_rdf_docs.py",
        "scripts/generate_weight_formats_docs.py",
    ],
    include_package_data=True,
    project_urls={  # Optional
        "Bug Reports": "https://github.com/bioimage-io/spec-bioimage-io/issues",
        "Source": "https://github.com/bioimage-io/spec-bioimage-io",
    },
)
