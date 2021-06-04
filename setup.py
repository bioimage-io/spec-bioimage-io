from pathlib import Path
from setuptools import find_namespace_packages, setup

# Get the long description from the README file
long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="bioimageio.spec",
    version="0.3b",
    description="Parser library for bioimage model zoo specs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bioimage-io/spec-bioimage-io",
    author="Bioimage Team",
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=find_namespace_packages(exclude=["tests"]),  # Required
    install_requires=[
        "PyYAML>=5.2",
        "dataclasses; python_version>='3.7.2,<3.9'",
        "imageio>=2.5",
        "marshmallow>=3.6.0,<4.0",
        "marshmallow_jsonschema",
        "marshmallow_union",
        "python-stdnum",
        "requests",
        "ruamel.yaml",
        "spdx-license-list",
        "typer",
        "typing-extensions",
    ],
    extras_require={"test": ["pytest", "tox"], "dev": ["pre-commit"]},
    scripts=["scripts/gen_spec_doc.py"],
    project_urls={  # Optional
        "Bug Reports": "https://github.com/bioimage-io/spec-bioimage-io/issues",
        "Source": "https://github.com/bioimage-io/spec-bioimage-io",
    },
)
