"""
core/solver.py

Comprehensive solver for planar four-bar linkage:

- Position analysis (vector loop solved with SciPy's `fsolve`)
- Velocity analysis (linear system from differentiated loop)
- Acceleration analysis (linear system from second derivative)

The file provides `FourBarSolver` as the main API and preserves the
previous `PositionSolver` name for backward compatibility.

Mathematical summary
--------------------
Vector loop:
    l2*e^{iθ2} + l3*e^{iθ3} - l4*e^{iθ4} - l1 = 0

Separating real/imaginary parts gives two scalar equations used by
`fsolve` to compute `θ3` and `θ4`. Differentiating once and twice
produces linear 2x2 systems for angular velocities `[ω3, ω4]` and
angular accelerations `[α3, α4]` respectively.

All angles in the public API are in degrees. Internally we compute
with radians.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple
import numpy as np
from scipy.optimize import fsolve

from math import radians, degrees


class SolverError(RuntimeError):
    """Raised when the mechanism is singular or solver fails."""


@dataclass
class KinematicState:
    """Container for solved kinematic state (angles in degrees)."""

    theta2: float
    theta3: float
    theta4: float
    omega2: float = 0.0
    omega3: float = 0.0
    omega4: float = 0.0
    alpha2: float = 0.0
    alpha3: float = 0.0
    alpha4: float = 0.0


class FourBarSolver:
    """Solver for planar four-bar linkages.

    Parameters
    ----------
    mechanism : FourBarMechanism-like
        Object exposing `l1,l2,l3,l4,theta2,omega2,alpha2` attributes and
        methods used in the project. See `core.mechanism.FourBarMechanism`.

    Notes
    -----
    - The solver keeps `last_solution` to provide continuity between
      successive solves (helps avoid branch-switching during animation).
    - Public methods return angles in degrees and Cartesian vectors in
      SI units consistent with the mechanism link lengths.
    """

    def __init__(self, mechanism) -> None:
        self.mechanism = mechanism
        # store last (theta3_deg, theta4_deg) to prefer continuous branch
        self.last_solution: Optional[Tuple[float, float]] = None

    # --------------------------
    # Grashof condition helper
    # --------------------------
    def grashof(self) -> Tuple[bool, str]:
        """Return (is_grashof, type) classification.

        Type string is one of: 'Grashof (crank-rocker)', 'Non-Grashof',
        'Grashof (double-crank)', 'Grashof (double-rocker)'.
        """

        l = sorted([self.mechanism.l1, self.mechanism.l2, self.mechanism.l3, self.mechanism.l4])
        s, p, q, L = l
        is_grashof = (s + L) <= (p + q)
        if not is_grashof:
            return False, "Non-Grashof"
        # simple classification (educational)
        if self.mechanism.l2 == s:
            return True, "Grashof (crank-rocker)"
        if self.mechanism.l4 == s:
            return True, "Grashof (rocker-crank)"
        return True, "Grashof (ambiguous)"

    # --------------------------
    # Position analysis
    # --------------------------
    def _vector_loop_eq(self, vars_rad: Iterable[float]) -> np.ndarray:
        """Return the vector-loop residuals (radians inputs)."""

        theta3_rad, theta4_rad = vars_rad

        l1, l2, l3, l4 = (
            self.mechanism.l1,
            self.mechanism.l2,
            self.mechanism.l3,
            self.mechanism.l4,
        )

        theta2_rad = radians(self.mechanism.theta2)

        eq1 = l2 * np.cos(theta2_rad) + l3 * np.cos(theta3_rad) - l4 * np.cos(theta4_rad) - l1
        eq2 = l2 * np.sin(theta2_rad) + l3 * np.sin(theta3_rad) - l4 * np.sin(theta4_rad)

        return np.array([eq1, eq2], dtype=float)

    def solve_position(self, initial_guess: Optional[Tuple[float, float]] = None, deg: bool = True) -> Tuple[float, float]:
        """Solve for `theta3` and `theta4`.

        Parameters
        ----------
        initial_guess : optional tuple (theta3_deg, theta4_deg)
            If not provided, solver will use a heuristic based on `last_solution`.
        deg : bool
            Return angles in degrees if True (default).

        Returns
        -------
        theta3, theta4 : tuple of floats
            Angles in degrees by default.

        Raises
        ------
        SolverError if SciPy fails to converge.
        """

        # prepare initial guess in radians
        if initial_guess is None:
            if self.last_solution is not None:
                guess_deg = self.last_solution
            else:
                # heuristic: put theta3 slightly ahead of crank, theta4 opposite
                guess_deg = (self.mechanism.theta2 + 30.0, self.mechanism.theta2 + 90.0)
        else:
            guess_deg = initial_guess

        guess_rad = [radians(guess_deg[0]), radians(guess_deg[1])]

        try:
            sol_rad, infodict, ier, mesg = fsolve(self._vector_loop_eq, guess_rad, full_output=True, xtol=1e-12, maxfev=1000)
        except Exception as exc:
            raise SolverError(f"Position solver failed: {exc}")

        if ier != 1:
            raise SolverError(f"Position solver did not converge: {mesg}")

        theta3_rad, theta4_rad = float(sol_rad[0]), float(sol_rad[1])

        theta3_deg = degrees(theta3_rad)
        theta4_deg = degrees(theta4_rad)

        # normalize to [0,360)
        theta3_deg = theta3_deg % 360.0
        theta4_deg = theta4_deg % 360.0

        # store for continuity
        self.last_solution = (theta3_deg, theta4_deg)

        return (theta3_deg, theta4_deg) if deg else (theta3_rad, theta4_rad)

    # Backwards compatible name
    def solve(self) -> Tuple[float, float]:
        """Compatibility wrapper replicating the old `solve()` behaviour.

        Returns (theta3_deg, theta4_deg).
        """

        return self.solve_position()

    def calculate_points(self) -> Dict[str, Tuple[float, float]]:
        """Return joint coordinates and solved angles.

        Returns a dictionary with keys: `theta3`, `theta4`, `O2`, `A`, `B`, `O4`.
        """

        theta3_deg, theta4_deg = self.solve_position()
        theta2_rad = radians(self.mechanism.theta2)
        theta3_rad = radians(theta3_deg)

        # ground
        O2 = (0.0, 0.0)
        O4 = (self.mechanism.l1, 0.0)

        # crank end A
        Ax = self.mechanism.l2 * np.cos(theta2_rad)
        Ay = self.mechanism.l2 * np.sin(theta2_rad)
        A = (float(Ax), float(Ay))

        # coupler end B
        Bx = Ax + self.mechanism.l3 * np.cos(theta3_rad)
        By = Ay + self.mechanism.l3 * np.sin(theta3_rad)
        B = (float(Bx), float(By))

        return {
            "theta3": float(theta3_deg),
            "theta4": float(theta4_deg),
            "O2": O2,
            "A": A,
            "B": B,
            "O4": O4,
        }

    # --------------------------
    # Velocity analysis
    # --------------------------
    def _velocity_matrix(self, theta3_rad: float, theta4_rad: float) -> np.ndarray:
        """Return the 2x2 coefficient matrix for angular velocities."""

        l3 = self.mechanism.l3
        l4 = self.mechanism.l4

        M = np.array(
            [
                [-l3 * np.sin(theta3_rad), l4 * np.sin(theta4_rad)],
                [l3 * np.cos(theta3_rad), -l4 * np.cos(theta4_rad)],
            ],
            dtype=float,
        )

        return M

    def solve_velocity(self, state: Optional[KinematicState] = None) -> Tuple[float, float]:
        """Solve for `omega3` and `omega4` given the current mechanism state.

        Parameters
        ----------
        state : optional KinematicState
            If provided, uses `state.theta2` etc.; otherwise reads from the mechanism.

        Returns
        -------
        (omega3, omega4) in same units as `mechanism.omega2`.
        """

        if state is None:
            theta2_deg = self.mechanism.theta2
            omega2 = self.mechanism.omega2
        else:
            theta2_deg = state.theta2
            omega2 = state.omega2

        # ensure position solved
        theta3_deg, theta4_deg = self.solve_position()
        theta2_rad = radians(theta2_deg)
        theta3_rad = radians(theta3_deg)
        theta4_rad = radians(theta4_deg)

        l2 = self.mechanism.l2

        # RHS terms from differentiating vector loop
        b = np.array(
            [l2 * omega2 * np.sin(theta2_rad), -l2 * omega2 * np.cos(theta2_rad)],
            dtype=float,
        )

        M = self._velocity_matrix(theta3_rad, theta4_rad)

        det = np.linalg.det(M)
        if abs(det) < 1e-9:
            raise SolverError("Velocity equations singular (mechanism at or near a singularity)")

        omega3, omega4 = np.linalg.solve(M, b)

        # store into mechanism-compatible state if possible
        try:
            self.mechanism.omega3 = float(omega3)
            self.mechanism.omega4 = float(omega4)
        except Exception:
            pass

        return float(omega3), float(omega4)

    # --------------------------
    # Acceleration analysis
    # --------------------------
    def solve_acceleration(self, state: Optional[KinematicState] = None) -> Tuple[float, float]:
        """Solve for `alpha3` and `alpha4` (angular accelerations).

        Uses the previously computed angular velocities for Coriolis-like terms.
        """

        if state is None:
            theta2_deg = self.mechanism.theta2
            omega2 = self.mechanism.omega2
            alpha2 = self.mechanism.alpha2
        else:
            theta2_deg = state.theta2
            omega2 = state.omega2
            alpha2 = state.alpha2

        # ensure velocities are available
        omega3, omega4 = None, None
        try:
            # try reading stored values
            omega3 = float(getattr(self.mechanism, "omega3"))
            omega4 = float(getattr(self.mechanism, "omega4"))
        except Exception:
            # compute if missing
            omega3, omega4 = self.solve_velocity(state)

        theta3_deg, theta4_deg = self.solve_position()
        theta2_rad = radians(theta2_deg)
        theta3_rad = radians(theta3_deg)
        theta4_rad = radians(theta4_deg)

        l2 = self.mechanism.l2
        l3 = self.mechanism.l3
        l4 = self.mechanism.l4

        # RHS for acceleration linear system (see derivation in docstring)
        rhs1 = l2 * alpha2 * np.sin(theta2_rad) + l2 * (omega2 ** 2) * np.cos(theta2_rad) + l3 * (omega3 ** 2) * np.cos(theta3_rad) - l4 * (omega4 ** 2) * np.cos(theta4_rad)
        rhs2 = -l2 * alpha2 * np.cos(theta2_rad) + l2 * (omega2 ** 2) * np.sin(theta2_rad) + l3 * (omega3 ** 2) * np.sin(theta3_rad) - l4 * (omega4 ** 2) * np.sin(theta4_rad)

        b = np.array([rhs1, rhs2], dtype=float)

        M = self._velocity_matrix(theta3_rad, theta4_rad)

        det = np.linalg.det(M)
        if abs(det) < 1e-9:
            raise SolverError("Acceleration equations singular (mechanism at or near a singularity)")

        alpha3, alpha4 = np.linalg.solve(M, b)

        # store into mechanism-compatible state if possible
        try:
            self.mechanism.alpha3 = float(alpha3)
            self.mechanism.alpha4 = float(alpha4)
        except Exception:
            pass

        return float(alpha3), float(alpha4)


# Backwards compatible name
class PositionSolver(FourBarSolver):
    """Compatibility subclass preserving the original `PositionSolver` name.

    It inherits the full-featured behaviour of `FourBarSolver` and keeps the
    legacy `solve()` and `calculate_points()` methods available.
    """


if __name__ == "__main__":
    # Quick self-test demo (uses core.mechanism.FourBarMechanism)
    from core.mechanism import FourBarMechanism

    mech = FourBarMechanism(l1=120.0, l2=60.0, l3=140.0, l4=100.0)
    mech.theta2 = 35.0
    mech.omega2 = 1.0  # rad/s or deg/s depending on user's convention
    mech.alpha2 = 0.1

    solver = FourBarSolver(mech)

    print("Grashof:", solver.grashof())

    theta3, theta4 = solver.solve_position()
    print("Theta3, Theta4 (deg):", theta3, theta4)

    pts = solver.calculate_points()
    print("Points:", pts)

    w3, w4 = solver.solve_velocity()
    print("Omega3, Omega4:", w3, w4)

    a3, a4 = solver.solve_acceleration()
    print("Alpha3, Alpha4:", a3, a4)
