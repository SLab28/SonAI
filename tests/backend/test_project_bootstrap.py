import tomllib
from pathlib import Path


REQUIRED_PACKAGES = [
    "fastapi",
    "fastmcp",
    "librosa",
    "essentia",
    "aubio",
    "python-osc",
]


def test_required_packages_declared_in_pyproject() -> None:
    pyproject = Path("/home/user/workspace/pyproject.toml")
    data = tomllib.loads(pyproject.read_text())
    dependencies = data["project"]["dependencies"]

    for package in REQUIRED_PACKAGES:
        assert any(dep.startswith(package) for dep in dependencies)
