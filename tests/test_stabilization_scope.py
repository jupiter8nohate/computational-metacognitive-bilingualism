from __future__ import annotations

import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "stabilization" / "scope-baseline.json"
PYPROJECT_PATH = ROOT / "pyproject.toml"
SRC_PATH = ROOT / "src"


def _baseline() -> dict[str, object]:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def _pyproject() -> dict[str, object]:
    with PYPROJECT_PATH.open("rb") as stream:
        return tomllib.load(stream)


def test_stabilization_top_level_python_package_surface_is_frozen() -> None:
    baseline = _baseline()
    expected = baseline["top_level_python_packages"]
    assert isinstance(expected, list)

    actual = sorted(
        path.name
        for path in SRC_PATH.iterdir()
        if path.is_dir() and (path / "__init__.py").is_file()
    )

    assert actual == expected, (
        "Stabilization scope changed: top-level Python package surface differs "
        "from stabilization/scope-baseline.json. New subsystems require an "
        "explicit freeze-boundary review and deliberate baseline update."
    )


def test_stabilization_installed_cli_surface_is_frozen() -> None:
    baseline = _baseline()
    expected = baseline["installed_cli_commands"]
    assert isinstance(expected, list)

    project = _pyproject()
    scripts = project["project"]["scripts"]
    assert isinstance(scripts, dict)
    actual = sorted(scripts)

    assert actual == expected, (
        "Stabilization scope changed: installed CLI surface differs from "
        "stabilization/scope-baseline.json. New commands require an explicit "
        "freeze-boundary review and deliberate baseline update."
    )
