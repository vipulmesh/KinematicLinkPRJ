"""
gui/animation.py

Embedded Matplotlib canvas for animating the four-bar mechanism
inside a PySide6 application. This module exposes `AnimationCanvas`.

Features
- Uses `core.solver.FourBarSolver` (not duplicating kinematic math).
- QTimer-based animation with `start()`, `pause()`, `resume()`, `reset()`.
- Emits `kinematics_updated` Qt signal each frame with numeric values
  for real-time GUI updates.
- Adjustable playback speed and optional coupler-curve tracing.
- Auto-scaling and equal aspect ratio.
"""

from typing import Dict, Optional

from PySide6.QtCore import QTimer, Signal
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from core.solver import FourBarSolver


class AnimationCanvas(FigureCanvas):
    """Matplotlib canvas that animates a four-bar mechanism.

    Parameters
    ----------
    mechanism : FourBarMechanism
        The mechanism instance from `core.mechanism`.

    Signals
    -------
    kinematics_updated : Signal(dict)
        Emitted every frame with keys: theta2, theta3, theta4 (deg),
        omega2, omega3, omega4 (rad/s), alpha2, alpha3, alpha4 (rad/s^2),
        points: {'O2','A','B','O4'} with cartesian tuples.
    """

    kinematics_updated = Signal(object)

    def __init__(self, mechanism):
        self.mechanism = mechanism

        # Use the comprehensive solver (velocity/acceleration handled there)
        self.solver = FourBarSolver(mechanism)

        self.figure = Figure(figsize=(6, 6), tight_layout=True)
        super().__init__(self.figure)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.grid(True)
        self.ax.set_title("4-Bar Mechanism")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        
        self._last_link_lengths = None
        self._xmin = self._xmax = self._ymin = self._ymax = 0.0

        # Animation timer
        self._timer = QTimer(self)
        self._interval_ms = 30  # default ~33 FPS
        self._timer.setInterval(self._interval_ms)
        self._timer.timeout.connect(self._on_timeout)

        # Playback control
        self.playing = False
        self.speed_scale = 1.0  # multiplies input angular speed

        # Tracing
        self.coupler_trace: Optional[np.ndarray] = None
        self.trace_enabled = False

        # Initial drawing limits (will auto-scale)
        self._padding = 0.1

        # Draw initial mechanism
        self.draw_mechanism()

    # -------------------------
    # Public control methods
    # -------------------------
    def start(self) -> None:
        """Start (or restart) the animation timer."""

        if not self._timer.isActive():
            self._timer.start()
        self.playing = True

    def pause(self) -> None:
        """Pause playback."""

        if self._timer.isActive():
            self._timer.stop()
        self.playing = False

    def resume(self) -> None:
        """Resume playback after pause."""

        if not self._timer.isActive():
            self._timer.start()
        self.playing = True

    def reset(self) -> None:
        """Reset mechanism state and clear traces."""

        self.pause()
        # Reset mechanism kinematics
        try:
            self.mechanism.reset()
        except Exception:
            # best-effort reset
            self.mechanism.theta2 = 0.0
            self.mechanism.omega2 = 0.0
            self.mechanism.alpha2 = 0.0

        self.coupler_trace = None
        self.draw_mechanism()

    def set_speed_scale(self, scale: float) -> None:
        """Scale playback speed (1.0 = real time based on `mechanism.omega2`)."""

        self.speed_scale = float(scale)

    def enable_trace(self, enabled: bool = True) -> None:
        """Enable or disable coupler (B point) trace."""

        self.trace_enabled = bool(enabled)
        if not self.trace_enabled:
            self.coupler_trace = None
        self.draw_mechanism()

    def set_timer_interval(self, interval_ms: int) -> None:
        """Change timer interval in milliseconds."""

        self._interval_ms = int(interval_ms)
        self._timer.setInterval(self._interval_ms)

    # -------------------------
    # Internal animation loop
    # -------------------------
    def _on_timeout(self) -> None:
        """Called by QTimer every frame; advance mechanism and redraw."""

        # Time step in seconds
        dt = (self._interval_ms / 1000.0) * self.speed_scale

        # mechanism.omega2 is expected to be in radians/sec for solver
        omega2 = float(getattr(self.mechanism, "omega2", 0.0))

        # convert angular velocity to degrees/sec for incrementing theta2
        deg_per_sec = np.degrees(omega2)

        step_deg = deg_per_sec * dt

        # Advance crank: mechanism.increment_angle expects degrees
        # and applies `mechanism.direction` internally.
        try:
            self.mechanism.increment_angle(step_deg)
        except Exception:
            # fallback: manual increment
            self.mechanism.theta2 = (self.mechanism.theta2 + self.mechanism.direction * step_deg) % 360.0

        # Recompute kinematics and redraw
        self.draw_mechanism()

    # -------------------------
    # Drawing helpers
    # -------------------------
    def _update_viewport_limits(self) -> None:
        """Compute fixed viewport limits based on a full 360-degree virtual revolution."""
        m = self.mechanism
        current_lengths = (m.l1, m.l2, m.l3, m.l4)
        
        if self._last_link_lengths != current_lengths:
            self._last_link_lengths = current_lengths
            
            # Save current state
            saved_theta = m.theta2
            
            all_xs = []
            all_ys = []
            
            # Sweep through a full revolution to find true workspace bounds
            for angle in range(0, 360, 2):
                m.theta2 = float(angle)
                try:
                    points = self.solver.calculate_points()
                    for pt_name in ["O2", "A", "B", "O4"]:
                        all_xs.append(points[pt_name][0])
                        all_ys.append(points[pt_name][1])
                except Exception:
                    pass  # Ignore invalid non-Grashof configurations
                    
            # Restore state
            m.theta2 = saved_theta
            
            if not all_xs:
                all_xs, all_ys = [0.0, m.l1], [0.0, 0.0]
                
            min_x, max_x = min(all_xs), max(all_xs)
            min_y, max_y = min(all_ys), max(all_ys)
            
            dx = max_x - min_x
            dy = max_y - min_y
            
            if dx == 0: dx = 1.0
            if dy == 0: dy = 1.0
            
            # 10% safety margin
            margin_x = dx * 0.10
            margin_y = dy * 0.10
            
            self._xmin = min_x - margin_x
            self._xmax = max_x + margin_x
            self._ymin = min_y - margin_y
            self._ymax = max_y + margin_y
            
        self.ax.set_xlim(self._xmin, self._xmax)
        self.ax.set_ylim(self._ymin, self._ymax)

    def draw_mechanism(self) -> None:
        """Compute kinematics via solver and draw the mechanism frame."""

        self.ax.clear()
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.grid(True)
        self._update_viewport_limits()

        # Position, velocity, acceleration via solver
        try:
            points = self.solver.calculate_points()
            theta3 = float(points["theta3"])
            theta4 = float(points["theta4"])
            O2 = points["O2"]
            A = points["A"]
            B = points["B"]
            O4 = points["O4"]
        except Exception as exc:
            # If solver fails, show message and return
            self.ax.text(0.5, 0.5, f"Solver error: {exc}", transform=self.ax.transAxes, ha="center")
            self.draw()
            return

        # Draw links
        self.ax.plot([O2[0], O4[0]], [O2[1], O4[1]], linewidth=4, color="black", zorder=1)
        self.ax.plot([O2[0], A[0]], [O2[1], A[1]], linewidth=3, color="red", zorder=2)
        self.ax.plot([A[0], B[0]], [A[1], B[1]], linewidth=3, color="blue", zorder=2)
        self.ax.plot([B[0], O4[0]], [B[1], O4[1]], linewidth=3, color="green", zorder=2)

        # Joints
        self.ax.scatter([O2[0], A[0], B[0], O4[0]], [O2[1], A[1], B[1], O4[1]], s=70, color="orange", zorder=10)

        # Coupler trace
        if self.trace_enabled:
            if self.coupler_trace is None:
                self.coupler_trace = np.array([[B[0], B[1]]], dtype=float)
            else:
                self.coupler_trace = np.vstack([self.coupler_trace, [B[0], B[1]]])

            self.ax.plot(self.coupler_trace[:, 0], self.coupler_trace[:, 1], color="magenta", linewidth=1, alpha=0.8)



        # Render
        self.draw()

        # Compute velocities and accelerations (best-effort; solver will raise on singularity)
        try:
            omega3, omega4 = self.solver.solve_velocity()
        except Exception:
            omega3 = float(getattr(self.mechanism, "omega3", 0.0))
            omega4 = float(getattr(self.mechanism, "omega4", 0.0))

        try:
            alpha3, alpha4 = self.solver.solve_acceleration()
        except Exception:
            alpha3 = float(getattr(self.mechanism, "alpha3", 0.0))
            alpha4 = float(getattr(self.mechanism, "alpha4", 0.0))

        try:
            a_Ax, a_Ay, a_Anet = self.solver.calculate_joint_A_acceleration()
        except Exception:
            a_Ax, a_Ay, a_Anet = 0.0, 0.0, 0.0

        try:
            a_Bx, a_By, a_Bnet = self.solver.calculate_joint_B_acceleration()
        except Exception:
            a_Bx, a_By, a_Bnet = 0.0, 0.0, 0.0

        # Emit numeric state for GUI consumption
        kinematics: Dict[str, object] = {
            "theta2": float(self.mechanism.theta2),
            "theta3": float(theta3),
            "theta4": float(theta4),
            "omega2": float(getattr(self.mechanism, "omega2", 0.0)),
            "omega3": float(omega3),
            "omega4": float(omega4),
            "alpha2": float(getattr(self.mechanism, "alpha2", 0.0)),
            "alpha3": float(alpha3),
            "alpha4": float(alpha4),
            "a_Ax": float(a_Ax),
            "a_Ay": float(a_Ay),
            "a_Anet": float(a_Anet),
            "a_Bx": float(a_Bx),
            "a_By": float(a_By),
            "a_Bnet": float(a_Bnet),
            "points": {"O2": O2, "A": A, "B": B, "O4": O4},
        }

        try:
            self.kinematics_updated.emit(kinematics)
        except Exception:
            # If no receivers, ignore
            pass

    # -------------------------
    # Frame capture / recording
    # -------------------------
    def capture_frame(self) -> "np.ndarray":
        """Return the current canvas as an RGB uint8 numpy array."""

        # draw() ensures canvas is updated
        self.draw()
        # grab the renderer buffer
        buf = self.buffer_rgba()
        # buffer is RGBA uint8
        arr = np.asarray(buf)
        # Convert to RGB
        if arr.shape[2] == 4:
            arr = arr[:, :, :3]
        return arr.astype("uint8")

    def capture_frames(self, n_frames: int, step_deg: float = 2.0) -> list:
        """Capture `n_frames` frames advancing the crank by `step_deg` each frame.

        The mechanism state is advanced; caller should reset if necessary.
        Returns a list of RGB uint8 frames.
        """

        frames = []
        saved_theta = float(self.mechanism.theta2)
        try:
            for _ in range(int(n_frames)):
                self.draw_mechanism()
                frames.append(self.capture_frame())
                # advance
                try:
                    self.mechanism.increment_angle(step_deg)
                except Exception:
                    self.mechanism.theta2 = (self.mechanism.theta2 + self.mechanism.direction * step_deg) % 360.0
        finally:
            # restore
            self.mechanism.theta2 = saved_theta

        return frames
