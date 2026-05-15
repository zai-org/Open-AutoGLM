import ast
from pathlib import Path

from packaging.requirements import Requirement
from packaging.version import Version

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SGLANG_PINNED_OPENAI_VERSION = Version("2.6.1")


def _openai_requirement_from_requirements_txt() -> Requirement:
    requirements_path = PROJECT_ROOT / "requirements.txt"
    for line in requirements_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("openai"):
            return Requirement(stripped)
    raise AssertionError("requirements.txt does not declare openai")


def _openai_requirement_from_setup_py() -> Requirement:
    setup_tree = ast.parse((PROJECT_ROOT / "setup.py").read_text(encoding="utf-8"))
    for node in ast.walk(setup_tree):
        if isinstance(node, ast.keyword) and node.arg == "install_requires":
            requirements = ast.literal_eval(node.value)
            for requirement in requirements:
                if requirement.startswith("openai"):
                    return Requirement(requirement)
    raise AssertionError("setup.py does not declare openai")


def test_openai_dependency_allows_sglang_pinned_version() -> None:
    for requirement in (
        _openai_requirement_from_requirements_txt(),
        _openai_requirement_from_setup_py(),
    ):
        assert SGLANG_PINNED_OPENAI_VERSION in requirement.specifier
