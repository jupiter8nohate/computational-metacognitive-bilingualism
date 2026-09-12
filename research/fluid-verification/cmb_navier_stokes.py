from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


@dataclass(frozen=True)
class VerificationResult:
    pressure_gradient: sp.Expr
    force_x: sp.Expr
    mass_residual: sp.Expr
    momentum_residual: sp.Expr
    energy_residual: sp.Expr

    @property
    def verified(self) -> bool:
        return all(
            sp.simplify(residual) == 0
            for residual in (
                self.mass_residual,
                self.momentum_residual,
                self.energy_residual,
            )
        )


def build_forced_equilibrium() -> VerificationResult:
    t, x = sp.symbols("t x", real=True)
    rho0, omega, k, E0 = sp.symbols(
        "rho0 omega k E0",
        real=True,
    )

    theta = k * x - omega * t
    rho = rho0
    u = sp.Integer(0)
    p = sp.cos(theta)
    energy = E0

    pressure_gradient = sp.diff(p, x)

    # Residual convention used here:
    # d(rho*u)/dt + d(rho*u**2)/dx + dp/dx - f_x = 0
    force_x = pressure_gradient

    mass_residual = sp.simplify(
        sp.diff(rho, t) + sp.diff(rho * u, x)
    )
    momentum_residual = sp.simplify(
        sp.diff(rho * u, t)
        + sp.diff(rho * u**2, x)
        + pressure_gradient
        - force_x
    )
    energy_residual = sp.simplify(
        sp.diff(energy, t)
        + sp.diff(u * energy, x)
        + sp.diff(u * p, x)
    )

    return VerificationResult(
        pressure_gradient=pressure_gradient,
        force_x=force_x,
        mass_residual=mass_residual,
        momentum_residual=momentum_residual,
        energy_residual=energy_residual,
    )


def main() -> int:
    result = build_forced_equilibrium()

    print(
        r"""
𒄆𓁹✞𒀱✞𓁹𒄆
♃ CMB://FLUID_VERIFICATION_LAB ♃
꩜ Err ⃝or⃟⃤ GLITCHOLOGY ꩜

3D □ SPACE
 ↓
4D ◇ TIME
 ↓
5D ⬡ MASS_RESIDUAL
 ↓
6D △ MOMENTUM_RESIDUAL
 ↓
7D 🔥 ENERGY_RESIDUAL
 ↓
8D 𖤍 VERIFICATION

PATTERN != PROOF
MODEL != REALITY
RESIDUAL_ZERO != UNIVERSAL_TRUTH
"""
    )

    print(f"pressure_gradient -> {result.pressure_gradient}")
    print(f"force_x           -> {result.force_x}")
    print(f"□ MASS             -> {result.mass_residual}")
    print(f"△ MOMENTUM         -> {result.momentum_residual}")
    print(f"⬡ ENERGY           -> {result.energy_residual}")
    print(
        "STATUS             -> "
        + (
            "VERIFIED_UNDER_STATED_ASSUMPTIONS"
            if result.verified
            else "MODEL_REQUIRES_CORRECTION"
        )
    )

    return 0 if result.verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
