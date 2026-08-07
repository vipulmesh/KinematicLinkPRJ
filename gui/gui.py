"""
gui/gui.py

Main GUI for the 4-Bar Kinematic Chain Simulator.

Provides a professional input panel with validation, an embedded
animation canvas, and a live-results panel. Uses `core.solver.FourBarSolver`
through the existing `AnimationCanvas` and preserves the application's
architecture.
"""

from __future__ import annotations

from typing import Tuple
from math import radians, pi

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QTextEdit,
    QMessageBox,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
)
from PySide6.QtCore import Qt

from gui.animation import AnimationCanvas
from core.mechanism import FourBarMechanism


class MainWindow(QMainWindow):
    """Main application window.

    The window exposes an input panel on the left, an embedded animation
    in the center, and a live-results panel on the right. All inputs are
    validated before simulation starts.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("4-Bar Kinematic Chain Simulator")
        self.resize(1400, 800)

        # Simulation state
        self.initial_angle_deg = 0.0
        self.simulation_time = 0.0

        self._base_timer_interval_ms = 30  # baseline for 1x speed

        self.setup_ui()

    # -------------------------
    # UI Construction
    # -------------------------
    def setup_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        ####################################################
        # LEFT PANEL - INPUTS
        ####################################################
        left_panel = QGroupBox("Input Parameters")
        left_layout = QGridLayout()

        # Link lengths (use QDoubleSpinBox for numeric validation)
        left_layout.addWidget(QLabel("Ground Link (L1)"), 0, 0)
        self.l1_input = QDoubleSpinBox()
        self.l1_input.setRange(0.001, 1e6)
        self.l1_input.setValue(120.0)
        self.l1_input.setSuffix(" mm")
        left_layout.addWidget(self.l1_input, 0, 1)

        left_layout.addWidget(QLabel("Crank (L2)"), 1, 0)
        self.l2_input = QDoubleSpinBox()
        self.l2_input.setRange(0.001, 1e6)
        self.l2_input.setValue(60.0)
        self.l2_input.setSuffix(" mm")
        left_layout.addWidget(self.l2_input, 1, 1)

        left_layout.addWidget(QLabel("Coupler (L3)"), 2, 0)
        self.l3_input = QDoubleSpinBox()
        self.l3_input.setRange(0.001, 1e6)
        self.l3_input.setValue(140.0)
        self.l3_input.setSuffix(" mm")
        left_layout.addWidget(self.l3_input, 2, 1)

        left_layout.addWidget(QLabel("Follower (L4)"), 3, 0)
        self.l4_input = QDoubleSpinBox()
        self.l4_input.setRange(0.001, 1e6)
        self.l4_input.setValue(100.0)
        self.l4_input.setSuffix(" mm")
        left_layout.addWidget(self.l4_input, 3, 1)

        # Initial crank angle (degrees)
        left_layout.addWidget(QLabel("Initial Angle (\u03B8\u2082)"), 4, 0)
        self.theta_input = QDoubleSpinBox()
        self.theta_input.setRange(0.0, 360.0)
        self.theta_input.setValue(0.0)
        self.theta_input.setSuffix(" °")
        left_layout.addWidget(self.theta_input, 4, 1)

        # Input Speed (N) in RPM
        left_layout.addWidget(QLabel("Input Speed (N)"), 5, 0)
        self.omega_input = QDoubleSpinBox()
        self.omega_input.setRange(-1e6, 1e6)
        self.omega_input.setDecimals(2)
        self.omega_input.setValue(60.0)
        self.omega_input.setSuffix(" RPM")
        left_layout.addWidget(self.omega_input, 5, 1)

        # Calculated Angular Velocity (Read-Only)
        self.omega_calc_display = QLineEdit()
        self.omega_calc_display.setReadOnly(True)
        left_layout.addWidget(self.omega_calc_display, 6, 0, 1, 2)

        # Angular acceleration (rad/s^2)
        left_layout.addWidget(QLabel("Angular Acceleration (\u03B1\u2082)"), 7, 0)
        self.alpha_input = QDoubleSpinBox()
        self.alpha_input.setRange(-1e6, 1e6)
        self.alpha_input.setDecimals(6)
        self.alpha_input.setValue(0.0)
        self.alpha_input.setSuffix(" rad/s\u00B2")
        left_layout.addWidget(self.alpha_input, 7, 1)

        # Animation speed slider
        left_layout.addWidget(QLabel("Animation Speed"), 8, 0)
        speed_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 5)
        self.speed_slider.setValue(3)  # default to 1x at position 3
        self.speed_slider.setTickPosition(QSlider.TicksBelow)
        self.speed_slider.setTickInterval(1)
        speed_layout.addWidget(self.speed_slider)
        self.speed_label = QLabel("1×")
        speed_layout.addWidget(self.speed_label)
        left_layout.addLayout(speed_layout, 8, 1)

        # Direction
        left_layout.addWidget(QLabel("Direction"), 9, 0)
        self.direction = QComboBox()
        self.direction.addItems(["Counter Clockwise", "Clockwise"])  # CCW positive
        left_layout.addWidget(self.direction, 9, 1)

        # Buttons
        self.validate_btn = QPushButton("Validate")
        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.reset_btn = QPushButton("Reset")

        left_layout.addWidget(self.validate_btn, 10, 0)
        left_layout.addWidget(self.start_btn, 10, 1)
        left_layout.addWidget(self.pause_btn, 11, 0)
        left_layout.addWidget(self.reset_btn, 11, 1)

        left_panel.setLayout(left_layout)

        ####################################################
        # CENTER PANEL - ANIMATION
        ####################################################
        center_panel = QGroupBox("Animation")
        center_layout = QVBoxLayout()

        # Default mechanism
        self.mechanism = FourBarMechanism(
            l1=float(self.l1_input.value()),
            l2=float(self.l2_input.value()),
            l3=float(self.l3_input.value()),
            l4=float(self.l4_input.value()),
        )

        # set initial angle
        self.mechanism.theta2 = float(self.theta_input.value())

        # Animation Canvas
        self.animation_area = AnimationCanvas(self.mechanism)
        # Ensure baseline timer interval
        self.animation_area.set_timer_interval(self._base_timer_interval_ms)

        center_layout.addWidget(self.animation_area)
        center_panel.setLayout(center_layout)

        ####################################################
        # RIGHT PANEL - LIVE RESULTS
        ####################################################
        right_panel = QGroupBox("Simulation Results")
        right_layout = QVBoxLayout()

        self.results = QTextEdit()
        self.results.setReadOnly(True)
        right_layout.addWidget(self.results)

        right_panel.setLayout(right_layout)

        ####################################################
        # MAIN LAYOUT
        ####################################################
        left_panel.setMaximumWidth(320)
        right_panel.setMaximumWidth(360)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(center_panel, 1)
        main_layout.addWidget(right_panel)

        self.statusBar().showMessage("Ready")

        ####################################################
        # SIGNALS & INITIALIZATION
        ####################################################
        self.animation_area.kinematics_updated.connect(self._on_kinematics_update)

        self.start_btn.clicked.connect(self._on_start)
        self.pause_btn.clicked.connect(self._on_pause)
        self.reset_btn.clicked.connect(self._on_reset)
        self.validate_btn.clicked.connect(self._on_validate)

        self.speed_slider.valueChanged.connect(self._on_speed_change)
        self.omega_input.valueChanged.connect(self._update_omega_calc_display)

        # initial display
        self._update_omega_calc_display(self.omega_input.value())
        self._update_results_display_empty()
        self.animation_area.draw_mechanism()

    # -------------------------
    # UI callbacks
    # -------------------------
    def _update_omega_calc_display(self, val: float) -> None:
        """Update the read-only calculated angular velocity field."""
        if val <= 0:
            self.omega_calc_display.setText("Angular Velocity (\u03C9\u2082): -- rad/s")
        else:
            omega = (2 * pi * val) / 60.0
            self.omega_calc_display.setText(f"Angular Velocity (\u03C9\u2082): {omega:.4f} rad/s")

    def _on_validate(self) -> None:
        """Validate inputs and update mechanism without starting simulation."""

        try:
            l1, l2, l3, l4 = self._read_lengths()
            theta0 = float(self.theta_input.value())
            n_rpm = float(self.omega_input.value())
            if n_rpm <= 0:
                raise ValueError("Input Speed (N) must be a positive number.")
            # Convert N (RPM) to ω₂ (rad/s) using ω = (2 × π × N) / 60
            # This conversion follows standard machine design conventions.
            omega = (2 * pi * n_rpm) / 60.0
            alpha = float(self.alpha_input.value())
        except ValueError as exc:
            QMessageBox.warning(self, "Validation Error", str(exc))
            return

        # Update mechanism
        self._apply_mechanism_params(l1, l2, l3, l4, theta0, omega, alpha)

        self.animation_area.draw_mechanism()
        self.statusBar().showMessage("Parameters validated and applied")

    def _on_start(self) -> None:
        """Start simulation: validate inputs, reset animation, and start timer."""

        try:
            l1, l2, l3, l4 = self._read_lengths()
            theta0 = float(self.theta_input.value())
            n_rpm = float(self.omega_input.value())
            if n_rpm <= 0:
                raise ValueError("Input Speed (N) must be a positive number.")
            # Convert N (RPM) to ω₂ (rad/s) using ω = (2 × π × N) / 60
            # This conversion follows standard machine design conventions.
            omega = (2 * pi * n_rpm) / 60.0
            alpha = float(self.alpha_input.value())
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid Input", str(exc))
            return

        # direction
        direction_text = self.direction.currentText()
        direction = 1 if direction_text.lower().startswith("counter") else -1

        # Apply parameters to mechanism
        self._apply_mechanism_params(l1, l2, l3, l4, theta0, omega, alpha, direction)

        # Reset sim time and coupler trace
        self.simulation_time = 0.0
        self.animation_area.coupler_trace = None

        # Ensure timer interval reflects slider position
        self._apply_speed_slider()

        # Redraw and start
        self.animation_area.draw_mechanism()
        self.animation_area.start()
        self.statusBar().showMessage("Simulation started")

    def _on_pause(self) -> None:
        self.animation_area.pause()
        self.statusBar().showMessage("Paused")

    def _on_reset(self) -> None:
        # reset crank to initial angle, clear trace, reset timer
        self.animation_area.pause()
        self.simulation_time = 0.0
        self.animation_area.coupler_trace = None
        # set mechanism angle to initial
        self.mechanism.theta2 = float(self.theta_input.value())
        self.animation_area.draw_mechanism()
        self.statusBar().showMessage("Reset")

    def _on_speed_change(self, value: int) -> None:
        # update label and apply mapping
        mapping = {1: 0.25, 2: 0.5, 3: 1.0, 4: 2.0, 5: 5.0}
        factor = mapping.get(int(value), 1.0)
        self.speed_label.setText(f"{factor}×")
        self._apply_speed_slider()

    # -------------------------
    # Helpers
    # -------------------------
    def _read_lengths(self) -> Tuple[float, float, float, float]:
        l1 = float(self.l1_input.value())
        l2 = float(self.l2_input.value())
        l3 = float(self.l3_input.value())
        l4 = float(self.l4_input.value())

        if not (l1 > 0 and l2 > 0 and l3 > 0 and l4 > 0):
            raise ValueError("Link lengths must be positive numbers.")

        return l1, l2, l3, l4

    def _apply_mechanism_params(self, l1: float, l2: float, l3: float, l4: float, theta0_deg: float, omega_rad_s: float, alpha_rad_s2: float, direction: int = 1) -> None:
        """Apply validated parameters to the mechanism object."""

        self.mechanism.l1 = float(l1)
        self.mechanism.l2 = float(l2)
        self.mechanism.l3 = float(l3)
        self.mechanism.l4 = float(l4)

        # set initial angle (degrees)
        self.mechanism.theta2 = float(theta0_deg) % 360.0
        self.initial_angle_deg = float(theta0_deg) % 360.0

        # omega/alpha are expected in rad/s and rad/s^2
        self.mechanism.set_input_motion(omega=float(omega_rad_s), alpha=float(alpha_rad_s2), direction=direction)

    def _apply_speed_slider(self) -> None:
        """Set QTimer interval according to slider (do not change ω₂)."""

        mapping = {1: 0.25, 2: 0.5, 3: 1.0, 4: 2.0, 5: 5.0}
        val = int(self.speed_slider.value())
        factor = mapping.get(val, 1.0)

        # base interval for 1x
        base = self._base_timer_interval_ms
        # To achieve factor f, shorten interval by f (faster) or lengthen for <1
        interval_ms = int(max(1, base / factor))
        self.animation_area.set_timer_interval(interval_ms)

    # -------------------------
    # Kinematics update receiver
    # -------------------------
    def _on_kinematics_update(self, data: dict) -> None:
        # Update simulation time (only while playing)
        if getattr(self.animation_area, "playing", False):
            dt = float(self.animation_area._interval_ms) / 1000.0
            self.simulation_time += dt

        # Determine mechanism type via solver
        try:
            is_g, mtype = self.animation_area.solver.grashof()
        except Exception:
            mtype = "Unknown"

        speed_text = self.speed_label.text()

        n_rpm_current = (abs(data['omega2']) * 60) / (2 * pi)

        txt = (
            f"θ2 : {data['theta2']:.4f} °\n"
            f"θ3 : {data['theta3']:.4f} °\n"
            f"θ4 : {data['theta4']:.4f} °\n\n"
            f"Input Speed : {n_rpm_current:g} RPM\n"
            f"Angular Velocity : {abs(data['omega2']):.3f} rad/s\n"
            f"ω3 : {data['omega3']:.6f} rad/s\n"
            f"ω4 : {data['omega4']:.6f} rad/s\n\n"
            f"Joint A Linear Acceleration\n"
            f"Ax : {data.get('a_Ax', 0.0):.4f} mm/s²\n"
            f"Ay : {data.get('a_Ay', 0.0):.4f} mm/s²\n"
            f"Net : {data.get('a_Anet', 0.0):.4f} mm/s²\n"
            f"--------------------------------------\n"
            f"Joint B Linear Acceleration\n"
            f"Ax : {data.get('a_Bx', 0.0):.4f} mm/s²\n"
            f"Ay : {data.get('a_By', 0.0):.4f} mm/s²\n"
            f"Net : {data.get('a_Bnet', 0.0):.4f} mm/s²\n"
            f"--------------------------------------\n"
            f"Mechanism Type: {mtype}\n"
            f"Simulation Time: {self.simulation_time:.3f} s\n"
            f"Animation Speed: {speed_text}\n"
        )

        self.results.setPlainText(txt)

    def _update_results_display_empty(self) -> None:
        self.results.setPlainText("No simulation yet. Press Start.")


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
