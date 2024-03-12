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
    ],
    packages=find_namespace_packages(exclude=["tests"]),  # Required
    install_requires=[
        "annotated-types>=0.5.0",
        "email_validator",
        "imageio",
        "loguru",
        "numpy>=1.21",
        "packaging>=17.0",
        "pooch",
        "pydantic-settings",
        "pydantic>=2.6.3",
        "python-dateutil",
        "ruyaml",
        "tqdm",
        "typing-extensions",
    ],
    extras_require={
        "dev": [
            "black",
            "deepdiff",
            "filelock",  # for session fixtures due to pytest-xdist
            "jsonschema",
            "jupyter",
            "lxml",
            "pdoc",
            "pre-commit",
            "psutil",  # parallel pytest with '-n auto'
            "pyright",
            "pytest-xdist",  # parallel pytest
            "pytest",
            "ruff",  # check line length in cases black cannot fix it
        ]
    },
    scripts=[],
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/bioimage-io/spec-bioimage-io/issues",
        "Source": "https://github.com/bioimage-io/spec-bioimage-io",
    },
)
