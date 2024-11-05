import json
from pathlib import Path

from setuptools import (
    find_namespace_packages,
    setup,  # pyright: ignore[reportUnknownVariableType]
)

# Get the long description from the README file
ROOT_DIR = Path(__file__).parent.resolve()
long_description = (ROOT_DIR / "README.md").read_text(encoding="utf-8")
VERSION_FILE = ROOT_DIR / "bioimageio" / "spec" / "VERSION"
VERSION = json.loads(VERSION_FILE.read_text(encoding="utf-8"))["version"]

_ = setup(
    name="bioimageio.spec",
    version=VERSION,
    description="Parser and validator library for bioimage.io specifications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bioimage-io/spec-bioimage-io",
    author="bioimage.io Team",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    packages=find_namespace_packages(exclude=["tests"]),  # Required
    install_requires=[
        "annotated-types>=0.5.0,<1",
        "email_validator",
        "imageio",
        "loguru",
        "numpy>=1.21",
        "packaging>=17.0",
        "pooch>=1.5,<2",
        "pydantic-settings",
        "pydantic>=2.7.0,<3",
        "python-dateutil",
        "requests",
        "rich",
        "ruyaml",
        "tqdm",
        "typing-extensions",
    ],
    extras_require={
        "tests": (
            test_extras := [
                "deepdiff",
                "filelock",  # for session fixtures due to pytest-xdist
                "lxml",
                "psutil",  # parallel pytest with '-n auto'
                "pytest-cov",
                "pytest-xdist",  # parallel pytest
                "pytest",
            ]
        ),
        "dev": test_extras
        + [
            "black",
            "jupyter",
            "pdoc",
            "pre-commit",
            "pyright==1.1.378",  # requires py>=3.13
            "python-devtools",
            "ruff",  # check line length in cases black cannot fix it
        ],
        "json": [
            "json_schema_for_humans",
            "jsonschema",
        ],
    },
    scripts=[],
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/bioimage-io/spec-bioimage-io/issues",
        "Source": "https://github.com/bioimage-io/spec-bioimage-io",
    },
)
