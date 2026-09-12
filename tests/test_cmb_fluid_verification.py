import importlib.util
from pathlib import Path

import sympy as sp


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "fluid-verification"
    / "cmb_navier_stokes.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "cmb_fluid_verification",
        MODULE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_forced_equilibrium_has_zero_residuals():
    module = _load_module()
    result = module.build_forced_equilibrium()

    assert sp.simplify(result.mass_residual) == 0
    assert sp.simplify(result.momentum_residual) == 0
    assert sp.simplify(result.energy_residual) == 0
    assert result.verified is True


def test_pressure_gradient_is_nonzero_before_balancing_force():
    module = _load_module()
    result = module.build_forced_equilibrium()

    assert result.pressure_gradient != 0
    assert sp.simplify(result.pressure_gradient - result.force_x) == 0
