"""
plots/graphs.py

Matplotlib-based plotting helpers for the 4-Bar Kinematic Chain Simulator.

Provides `GraphsCanvas`, a PySide6-embeddable FigureCanvas with methods to
draw the required engineering plots:

- Angle vs Time
- Velocity vs Time
- Acceleration vs Time
- Angular Velocity vs Crank Angle
- Angular Acceleration vs Crank Angle
- Coupler Curve

The canvas exposes simple API methods that accept numpy arrays or Python
lists. It does not duplicate kinematic calculations — it only plots data
computed elsewhere (e.g., by `core.solver` during simulation).
"""

from __future__ import annotations

from typing import Sequence, Optional

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class GraphsCanvas(FigureCanvas):
    """Embeddable plotting canvas for all requested graphs.

    Usage:
        widget = GraphsCanvas()
        widget.plot_angles_vs_time(t, theta2, theta3, theta4)
        widget.plot_coupler_curve(x, y)
        widget.save_png("angles.png")
    """

    def __init__(self, parent=None, figsize=(8, 6)) -> None:
        self.figure = Figure(figsize=figsize, tight_layout=True)
        super().__init__(self.figure)
        self.setParent(parent)

        # Create a grid of axes to reuse for multiple plots
        # We'll create 3 rows x 2 columns layout and show/hide as needed
        axes_grid = self.figure.subplots(3, 2)
        # Flatten for easy indexing
        self.axes = axes_grid.flatten()

        # Map of names to axis indices for clarity
        self._ax_map = {
            "angles_time": 0,
            "velocity_time": 1,
            "acceleration_time": 2,
            "omega_vs_crank": 3,
            "alpha_vs_crank": 4,
            "coupler_curve": 5,
        }

        # Initialize empty plots
        for ax in self.axes:
            ax.clear()

    # ------------------
    # Utility
    # ------------------
    def _to_np(self, arr: Sequence[float]) -> np.ndarray:
        return np.asarray(arr, dtype=float)

    def clear(self) -> None:
        """Clear all subplots."""

        for ax in self.axes:
            ax.clear()
        self.draw()

    def save_png(self, path: str, dpi: int = 150) -> None:
        """Save the current figure as a PNG file."""

        self.figure.savefig(path, dpi=dpi)

    # ------------------
    # Plotting APIs
    # ------------------
    def plot_angles_vs_time(self, t: Sequence[float], theta2: Sequence[float], theta3: Sequence[float], theta4: Sequence[float]) -> None:
        """Plot crank/coupler/follower angles vs time.

        All arrays must have the same length.
        Angles are expected in degrees.
        """

        t = self._to_np(t)
        th2 = self._to_np(theta2)
        th3 = self._to_np(theta3)
        th4 = self._to_np(theta4)

        ax = self.axes[self._ax_map["angles_time"]]
        ax.clear()
        ax.plot(t, th2, label=r"$\theta_2$ (deg)")
        ax.plot(t, th3, label=r"$\theta_3$ (deg)")
        ax.plot(t, th4, label=r"$\theta_4$ (deg)")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Angle (deg)")
        ax.legend()
        ax.grid(True)
        self.draw()

    def plot_velocities_vs_time(self, t: Sequence[float], omega2: Sequence[float], omega3: Sequence[float], omega4: Sequence[float]) -> None:
        """Plot angular velocities vs time (rad/s expected)."""

        t = self._to_np(t)
        w2 = self._to_np(omega2)
        w3 = self._to_np(omega3)
        w4 = self._to_np(omega4)

        ax = self.axes[self._ax_map["velocity_time"]]
        ax.clear()
        ax.plot(t, w2, label=r"$\omega_2$ (rad/s)")
        ax.plot(t, w3, label=r"$\omega_3$ (rad/s)")
        ax.plot(t, w4, label=r"$\omega_4$ (rad/s)")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Angular velocity (rad/s)")
        ax.legend()
        ax.grid(True)
        self.draw()

    def plot_accelerations_vs_time(self, t: Sequence[float], alpha2: Sequence[float], alpha3: Sequence[float], alpha4: Sequence[float]) -> None:
        """Plot angular accelerations vs time (rad/s^2 expected)."""

        t = self._to_np(t)
        a2 = self._to_np(alpha2)
        a3 = self._to_np(alpha3)
        a4 = self._to_np(alpha4)

        ax = self.axes[self._ax_map["acceleration_time"]]
        ax.clear()
        ax.plot(t, a2, label=r"$\alpha_2$ (rad/s$^2$)")
        ax.plot(t, a3, label=r"$\alpha_3$ (rad/s$^2$)")
        ax.plot(t, a4, label=r"$\alpha_4$ (rad/s$^2$)")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Angular acceleration (rad/s^2)")
        ax.legend()
        ax.grid(True)
        self.draw()

    def plot_omega_vs_crank(self, theta2: Sequence[float], omega3: Sequence[float], omega4: Sequence[float]) -> None:
        """Plot angular velocities of links 3 and 4 vs crank angle (deg)."""

        th2 = self._to_np(theta2)
        w3 = self._to_np(omega3)
        w4 = self._to_np(omega4)

        ax = self.axes[self._ax_map["omega_vs_crank"]]
        ax.clear()
        ax.plot(th2, w3, label=r"$\omega_3$ vs $\theta_2$")
        ax.plot(th2, w4, label=r"$\omega_4$ vs $\theta_2$")
        ax.set_xlabel(r"Crank angle $\theta_2$ (deg)")
        ax.set_ylabel(r"Angular velocity (rad/s)")
        ax.legend()
        ax.grid(True)
        self.draw()

    def plot_alpha_vs_crank(self, theta2: Sequence[float], alpha3: Sequence[float], alpha4: Sequence[float]) -> None:
        """Plot angular accelerations of links 3 and 4 vs crank angle (deg)."""

        th2 = self._to_np(theta2)
        a3 = self._to_np(alpha3)
        a4 = self._to_np(alpha4)

        ax = self.axes[self._ax_map["alpha_vs_crank"]]
        ax.clear()
        ax.plot(th2, a3, label=r"$\alpha_3$ vs $\theta_2$")
        ax.plot(th2, a4, label=r"$\alpha_4$ vs $\theta_2$")
        ax.set_xlabel(r"Crank angle $\theta_2$ (deg)")
        ax.set_ylabel(r"Angular acceleration (rad/s^2)")
        ax.legend()
        ax.grid(True)
        self.draw()

    def plot_coupler_curve(self, x: Sequence[float], y: Sequence[float]) -> None:
        """Plot coupler curve (trajectory of point B).

        Parameters
        ----------
        x, y : sequences of equal length
            Cartesian coordinates of the coupler point sampled over time.
        """

        x = self._to_np(x)
        y = self._to_np(y)

        ax = self.axes[self._ax_map["coupler_curve"]]
        ax.clear()
        ax.plot(x, y, color="magenta", linewidth=1)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("Coupler Curve")
        ax.axis("equal")
        ax.grid(True)
        self.draw()
