import tomllib
from pathlib import Path


REQUIRED_PACKAGES = [
    "fastapi",
    "fastmcp",
    "librosa",
    "anthropic",
    "python-osc",
]


def test_required_packages_declared_in_pyproject() -> None:
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text())
    dependencies = data["project"]["dependencies"]

    for package in REQUIRED_PACKAGES:
        assert any(dep.startswith(package) for dep in dependencies)
