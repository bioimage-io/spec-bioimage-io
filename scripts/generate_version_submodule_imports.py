import re
import sys
from argparse import ArgumentParser
from dataclasses import dataclass, field
from difflib import ndiff
from pathlib import Path
from typing import List, Literal

import black.files
import black.mode

ROOT_PATH = Path(__file__).parent.parent

AUTOGEN_START = "# autogen: start\n"
AUTOGEN_BODY_SINGLE = """from . import {info.latest_version_module}

{info.target_node} = {info.latest_version_module}.{info.target_node}
Any{info.target_node} = {info.latest_version_module}.{info.target_node}
"""
AUTOGEN_BODY_MULTIPLE = """\"\"\"
implementaions of all released minor versions are available in submodules:
{info.submodule_list}
\"\"\"

from typing import Union

from pydantic import Discriminator
from typing_extensions import Annotated

{info.all_version_modules_imports}

Any{info.target_node} = Annotated[Union[{info.all_target_nodes_plain_aliases}], Discriminator("format_version")]
\"\"\"Union of any released {info.target} desription\"\"\"
"""

AUTOGEN_STOP = "# autogen: stop\n"

VERSION_MODULE_PATTERN = r"v(?P<major>\d+)_(?P<minor>\d+).py"


def main(command: Literal["check", "generate"]):
    for target in [
        "generic",
        "model",
        "dataset",
        "notebook",
        "application",
    ]:
        process(
            Info(
                target=target,
                all_version_modules=get_ordered_version_submodules(target),
            ),
            check=command == "check",
        )

    return 0


def parse_args():
    p = ArgumentParser(
        description=(
            "script that generates imports in bioimageio.spec resource description"
            + " submodules"
        )
    )
    _ = p.add_argument(
        "command", choices=["check", "generate"], nargs="?", default="generate"
    )
    args = p.parse_args()
    return args


@dataclass
class Info:
    target: str
    all_version_modules: List[str]
    target_node: str = field(init=False)
    all_target_nodes_plain: str = field(init=False)
    all_target_nodes_plain_aliases: str = field(init=False)
    latest_version_module: str = field(init=False)
    all_version_modules_import_as: str = field(init=False)
    all_version_modules_imports: str = field(init=False)
    package_path: Path = field(init=False)
    submodule_list: str = field(init=False)

    def __post_init__(self):
        self.target_node = self.target.capitalize() + "Descr"
        self.all_target_nodes_plain = ", ".join(
            [f"{vm}.{self.target_node}" for vm in self.all_version_modules]
        )
        self.all_target_nodes_plain_aliases = ", ".join(
            [f"{self.target_node}_{vm}" for vm in self.all_version_modules]
        )
        self.latest_version_module = self.all_version_modules[-1]
        self.all_version_modules_import_as = ", ".join(
            f"{m} as {m}" for m in self.all_version_modules
        )

        avmi = (
            [f"from . import {', '.join(self.all_version_modules)}"]
            + [f"{self.target_node} = {self.latest_version_module}.{self.target_node}"]
            + [
                f"{self.target_node}_{m} = {m}.{self.target_node}"
                for m in self.all_version_modules
            ]
        )
        self.all_version_modules_imports = "\n".join(avmi)

        self.package_path = (ROOT_PATH / "bioimageio" / "spec" / self.target).resolve()
        self.submodule_list = "\n".join(
            [
                f"- {self.target} {vm}: `bioimageio.spec.{self.target}.{vm}."
                + f"{self.target_node}`"
                for vm in self.all_version_modules
            ]
        )


def process(info: Info, check: bool):
    package_init = info.package_path / "__init__.py"
    print(f"{'Checking' if check else 'Updating'} {package_init}")

    init_content = package_init.read_text()
    pattern = AUTOGEN_START + ".*" + AUTOGEN_STOP
    flags = re.DOTALL
    if not re.findall(pattern, init_content, flags=flags):
        raise RuntimeError(
            f"Could not find autogen markers in {package_init}. Expected to"
            + f" find:\n{AUTOGEN_START}...{AUTOGEN_STOP}"
        )

    autogen_body = (
        AUTOGEN_BODY_SINGLE
        if len(info.all_version_modules) == 1
        else AUTOGEN_BODY_MULTIPLE
    )
    updated = re.sub(
        pattern,
        AUTOGEN_START + autogen_body.format(info=info) + AUTOGEN_STOP,
        init_content,
        flags=flags,
    )
    black_config = black.files.parse_pyproject_toml(str(ROOT_PATH / "pyproject.toml"))
    black_config["target_versions"] = set(
        (
            getattr(black.mode.TargetVersion, tv.upper())
            for tv in black_config.pop("target_version")
        )
    )
    black_config.pop("extend_exclude", None)
    updated = black.format_str(updated, mode=black.mode.Mode(**black_config))
    if check:
        if init_content == updated:
            print("all seems fine")
        else:
            raise RuntimeError(
                "call with mode 'generate' to update:\n"
                + "".join(
                    ndiff(
                        init_content.splitlines(keepends=True),
                        updated.splitlines(keepends=True),
                    )
                )
            )
    else:
        with package_init.open("w", newline="\n", encoding="utf-8") as f:
            _ = f.write(updated)


def get_ordered_version_submodules(target: str):
    matches = [
        m
        for p in (ROOT_PATH / "bioimageio" / "spec" / target).iterdir()
        if p.is_file() and (m := re.fullmatch(VERSION_MODULE_PATTERN, p.name))
    ]
    if not matches:
        raise RuntimeError(f"No version modules found for target '{target}'")

    return [
        m.string[:-3]
        for m in sorted(matches, key=lambda m: (int(m["major"]), int(m["minor"])))
    ]


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(args.command))
