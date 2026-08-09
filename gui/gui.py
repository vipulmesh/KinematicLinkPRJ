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
    QScrollArea,
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
    QRadioButton,
    QButtonGroup,
    QMenuBar,
    QDialog,
    QFrame,
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import (
    QAction,
    QPixmap,
    QPainter,
    QPainterPath,
    QColor,
    QDesktopServices,
    QFont,
)

from gui.animation import AnimationCanvas
from core.mechanism import FourBarMechanism


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About 4-Bar Kinematic Chain Simulator")
        self.setFixedSize(1200, 800)
        
        self.setStyleSheet('''
            QDialog {
                background-color: #1e1e2e;
                color: #cdd6f4;
            }
            QLabel {
                color: #cdd6f4;
            }
            QFrame#card {
                background-color: #313244;
                border-radius: 12px;
            }
            QLabel#cardTitle {
                font-size: 14px;
                font-weight: bold;
                color: #cba6f7;
                margin-bottom: 5px;
            }
            QPushButton#linkBtn {
                background-color: #45475a;
                color: #cdd6f4;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #585b70;
            }
            QPushButton#linkBtn:hover {
                background-color: #585b70;
                border: 1px solid #cba6f7;
            }
            QPushButton#closeBtn {
                background-color: #f38ba8;
                color: #11111b;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#closeBtn:hover {
                background-color: #eba0ac;
            }
            QLabel#badge {
                background-color: #45475a;
                color: #89b4fa;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 13px;
            }
        ''')
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # ---------------------------------------------------------
        # HEADER
        # ---------------------------------------------------------
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        title_lbl = QLabel("FOUR-BAR KINEMATIC CHAIN SIMULATOR")
        title_lbl.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_font.setLetterSpacing(QFont.AbsoluteSpacing, 2.0)
        title_lbl.setFont(title_font)
        
        version_lbl = QLabel("Version 1.0")
        version_lbl.setAlignment(Qt.AlignCenter)
        version_font = QFont()
        version_font.setPointSize(14)
        version_lbl.setFont(version_font)
        version_lbl.setStyleSheet("color: #a6adc8;")
        
        header_layout.addWidget(title_lbl)
        header_layout.addWidget(version_lbl)
        main_layout.addLayout(header_layout)
        
        line_top = QFrame()
        line_top.setFrameShape(QFrame.HLine)
        line_top.setStyleSheet("background-color: #45475a;")
        main_layout.addWidget(line_top)

        # ---------------------------------------------------------
        # MAIN SCROLL AREA
        # ---------------------------------------------------------
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; } QWidget#scrollContent { background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("scrollContent")
        content_layout = QHBoxLayout(scroll_content)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(20)

        # =========================================================
        # LEFT COLUMN (50%)
        # =========================================================
        left_layout = QVBoxLayout()
        left_layout.setSpacing(15)
        
        # CARD 1: About the Software
        about_card = QFrame()
        about_card.setObjectName("card")
        about_layout = QVBoxLayout(about_card)
        about_layout.setContentsMargins(20, 20, 20, 20)
        
        about_title = QLabel("ABOUT THE SOFTWARE")
        about_title.setObjectName("cardTitle")
        about_desc = QLabel("This desktop application is a comprehensive tool designed for the robust simulation "
                           "and kinematic analysis of planar four-bar mechanisms. Built for both educational "
                           "and professional engineering contexts, it bridges the gap between theoretical machine "
                           "design and visual, real-time validation.<br><br>"
                           "The software evaluates position, velocity, and acceleration matrices at every degree of "
                           "crank rotation. It preemptively validates physical assembly feasibility and Grashof's Law "
                           "conditions before permitting simulation, ensuring that the mechanism behaves precisely "
                           "as it would in the physical world.")
        about_desc.setWordWrap(True)
        about_desc.setStyleSheet("font-size: 14px; line-height: 1.6;")
        
        about_layout.addWidget(about_title)
        about_layout.addSpacing(5)
        about_layout.addWidget(about_desc)
        
        left_layout.addWidget(about_card)

        # CARD 2: Project Information
        info2_card = QFrame()
        info2_card.setObjectName("card")
        info2_layout = QVBoxLayout(info2_card)
        info2_layout.setContentsMargins(20, 20, 20, 20)
        
        info2_title = QLabel("PROJECT INFORMATION")
        info2_title.setObjectName("cardTitle")
        info2_layout.addWidget(info2_title)
        info2_layout.addSpacing(5)
        
        info2_grid = QGridLayout()
        info2_grid.setSpacing(15)
        
        info_items = [
            ("Project Name", "Four-Bar Kinematic Chain Simulator"),
            ("Faculty Guide", "<Faculty Name>"),
            ("Department", "Mechanical Engineering"),
            ("Institute", "JSPM Rajarshi Shahu College of Engineering, Pune"),
            ("Academic Year", "2026–27")
        ]
        
        for i, (k, v) in enumerate(info_items):
            lbl_k = QLabel(k)
            lbl_k.setStyleSheet("font-weight: bold; font-size: 14px; color: #bac2de;")
            lbl_k.setWordWrap(True)
            lbl_v = QLabel(v)
            lbl_v.setStyleSheet("font-size: 14px;")
            lbl_v.setWordWrap(True)
            info2_grid.addWidget(lbl_k, i, 0)
            info2_grid.addWidget(lbl_v, i, 1)
            
        info2_layout.addLayout(info2_grid)
        
        left_layout.addWidget(info2_card)
        left_layout.addStretch()

        # =========================================================
        # RIGHT COLUMN (50%)
        # =========================================================
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        
        # CARD 3: Key Features
        feat_card = QFrame()
        feat_card.setObjectName("card")
        feat_layout = QVBoxLayout(feat_card)
        feat_layout.setContentsMargins(20, 20, 20, 20)
        
        feat_title = QLabel("KEY FEATURES")
        feat_title.setObjectName("cardTitle")
        feat_layout.addWidget(feat_title)
        feat_layout.addSpacing(5)
        
        feat_grid = QGridLayout()
        feat_grid.setSpacing(10)
        features = [
            "• Position Analysis", "• Assembly Validation",
            "• Velocity Analysis", "• Motion Validation",
            "• Acceleration Analysis", "• RPM-Based Input",
            "• Joint A Acceleration", "• Real-Time Animation",
            "• Joint B Acceleration", "• Fixed Viewport",
            "• Grashof Law Validation"
        ]
        
        for i, f in enumerate(features):
            lbl = QLabel(f)
            lbl.setStyleSheet("font-size: 14px;")
            lbl.setWordWrap(True)
            feat_grid.addWidget(lbl, i // 2, i % 2)
            
        feat_layout.addLayout(feat_grid)

        right_layout.addWidget(feat_card)
        
        # CARD 4: Technologies
        tech_card = QFrame()
        tech_card.setObjectName("card")
        tech_layout = QVBoxLayout(tech_card)
        tech_layout.setContentsMargins(20, 20, 20, 20)
        
        tech_title = QLabel("TECHNOLOGIES USED")
        tech_title.setObjectName("cardTitle")
        tech_layout.addWidget(tech_title)
        tech_layout.addSpacing(10)
        
        badges_layout1 = QHBoxLayout()
        badges_layout1.setSpacing(10)
        for tech in ["Python", "PySide6", "NumPy"]:
            b = QLabel(tech)
            b.setObjectName("badge")
            badges_layout1.addWidget(b)
        badges_layout1.addStretch()
        
        badges_layout2 = QHBoxLayout()
        badges_layout2.setSpacing(10)
        for tech in ["SciPy", "Matplotlib"]:
            b = QLabel(tech)
            b.setObjectName("badge")
            badges_layout2.addWidget(b)
        badges_layout2.addStretch()
        
        tech_layout.addLayout(badges_layout1)
        tech_layout.addLayout(badges_layout2)

        right_layout.addWidget(tech_card)
        right_layout.addStretch()
        
        # Combine Left & Right into Scroll Content
        content_layout.addLayout(left_layout, 1)
        content_layout.addLayout(right_layout, 1)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # ---------------------------------------------------------
        # BOTTOM BAR
        # ---------------------------------------------------------
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 10, 0, 0)
        
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(2)
        lbl1 = QLabel("© 2026 Vipul Meshram")
        lbl1.setStyleSheet("color: #6c7086; font-size: 13px;")
        lbl2 = QLabel("Developed by Vipul Meshram")
        lbl2.setStyleSheet("color: #6c7086; font-size: 13px;")
        footer_layout.addWidget(lbl1)
        footer_layout.addWidget(lbl2)
        
        # Link Buttons
        links_layout = QHBoxLayout()
        links_layout.setSpacing(15)
        
        def create_link_btn(text, url):
            btn = QPushButton(text)
            btn.setObjectName("linkBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, u=url: QDesktopServices.openUrl(QUrl(u)))
            return btn
            
        links_layout.addWidget(create_link_btn("GitHub", "https://github.com/"))
        links_layout.addWidget(create_link_btn("LinkedIn", "https://linkedin.com/"))
        links_layout.addWidget(create_link_btn("Portfolio", "https://example.com/"))
        links_layout.addWidget(create_link_btn("Email", "mailto:example@example.com"))
        
        close_btn = QPushButton("Close")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(120, 40)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        
        bottom_layout.addLayout(footer_layout)
        bottom_layout.addStretch()
        bottom_layout.addLayout(links_layout)
        bottom_layout.addStretch()
        bottom_layout.addWidget(close_btn, alignment=Qt.AlignBottom)
        
        main_layout.addLayout(bottom_layout)



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
    def _setup_menu(self) -> None:
        menu_bar = self.menuBar()
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        menu_bar.addAction(about_action)

    def _show_about(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    def setup_ui(self) -> None:
        self._setup_menu()
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

        # Animation speed (Radio Buttons)
        speed_group = QGroupBox("Animation Speed")
        speed_vlayout = QVBoxLayout()
        self.speed_btn_group = QButtonGroup(self)
        
        self.speed_options = {
            "0.25×": 0.25,
            "0.5×": 0.5,
            "1×": 1.0,
            "2×": 2.0,
            "5×": 5.0
        }
        
        for i, text in enumerate(self.speed_options.keys()):
            rb = QRadioButton(text)
            if text == "1×":
                rb.setChecked(True)
            speed_vlayout.addWidget(rb)
            self.speed_btn_group.addButton(rb, i)
            
        speed_group.setLayout(speed_vlayout)
        left_layout.addWidget(speed_group, 8, 0, 1, 2)

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

        self.statusBar().showMessage("🟢 Ready")

        ####################################################
        # SIGNALS & INITIALIZATION
        ####################################################
        self.animation_area.kinematics_updated.connect(self._on_kinematics_update)

        self.start_btn.clicked.connect(self._on_start)
        self.pause_btn.clicked.connect(self._on_pause)
        self.reset_btn.clicked.connect(self._on_reset)
        self.validate_btn.clicked.connect(self._on_validate)

        self.speed_btn_group.buttonClicked.connect(self._on_speed_change)
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
        self.statusBar().showMessage("🟢 Ready")

    def _on_start(self) -> None:
        """Start simulation: validate inputs, then run pre-flight feasibility check."""

        # ── Stage 1: Numeric input validation ────────────────────────────────
        try:
            l1, l2, l3, l4 = self._read_lengths()
            theta0 = float(self.theta_input.value())
            n_rpm = float(self.omega_input.value())
            if n_rpm <= 0:
                raise ValueError("Input Speed (N) must be a positive number.")
            omega = (2 * pi * n_rpm) / 60.0
            alpha = float(self.alpha_input.value())
        except ValueError as exc:
            self.statusBar().showMessage("🔴 Invalid Mechanism")
            QMessageBox.warning(self, "Invalid Input", str(exc))
            return

        direction_text = self.direction.currentText()
        direction = 1 if direction_text.lower().startswith("counter") else -1

        # ── Stage 2: Assembly feasibility ─────────────────────────────────────
        # The four links must be able to form a closed loop at some position.
        # Necessary condition: no single link can be longer than the sum of the others.
        links = [l1, l2, l3, l4]
        link_names = ["Ground (L1)", "Crank (L2)", "Coupler (L3)", "Follower (L4)"]
        for i, (L, name) in enumerate(zip(links, link_names)):
            others = sum(links) - L
            if L >= others:
                self.statusBar().showMessage("🔴 Invalid Mechanism")
                QMessageBox.critical(
                    self,
                    "Assembly Error",
                    f"Simulation cannot start.\n\n"
                    f"Reason:\n"
                    f"{name} ({L:.2f} mm) is too long to form a closed four-bar linkage.\n"
                    f"It must be shorter than the sum of the remaining three links ({others:.2f} mm).\n\n"
                    f"Please modify the link lengths."
                )
                return

        # Apply parameters before running the sweep
        self._apply_mechanism_params(l1, l2, l3, l4, theta0, omega, alpha, direction)

        # ── Stage 3: Grashof check (advisory — non-Grashof mechanisms can ────
        # still be valid rockers, so we warn but do not block)
        try:
            is_grashof, mtype = self.animation_area.solver.grashof()
            if not is_grashof:
                reply = QMessageBox.question(
                    self,
                    "Non-Grashof Mechanism",
                    f"The entered link lengths produce a Non-Grashof mechanism.\n"
                    f"The crank cannot make a full revolution — it will oscillate as a rocker.\n\n"
                    f"Do you still want to proceed?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    self.statusBar().showMessage("🔴 Invalid Mechanism")
                    return
        except Exception:
            pass

        # ── Stage 4: Motion feasibility sweep (0° → 360°, every 1°) ──────────
        # Re-use the existing solver — no kinematic logic is duplicated here.
        saved_theta = self.mechanism.theta2
        saved_last = self.animation_area.solver.last_solution
        # Reset solver continuity state for a clean sweep
        self.animation_area.solver.last_solution = None
        failed_angle = None

        for angle in range(0, 360, 1):
            self.mechanism.theta2 = float(angle)
            try:
                self.animation_area.solver.calculate_points()
            except Exception:
                failed_angle = angle
                break

        # Restore mechanism and solver state
        self.mechanism.theta2 = saved_theta
        self.animation_area.solver.last_solution = saved_last

        if failed_angle is not None:
            self.statusBar().showMessage("🔴 Invalid Mechanism")
            QMessageBox.critical(
                self,
                "Simulation Cannot Start",
                f"Simulation cannot start.\n\n"
                f"Reason:\n"
                f"The mechanism becomes unsolvable near \u03b8\u2082 = {failed_angle}\u00b0.\n\n"
                f"The solver could not find a valid configuration at this crank position.\n"
                f"This usually means the links cannot close into a valid four-bar loop\n"
                f"at that angle.\n\n"
                f"Please modify the link lengths."
            )
            return

        # ── All stages passed — launch animation ──────────────────────────────
        self.simulation_time = 0.0
        self.animation_area.coupler_trace = None
        self._apply_speed_slider()
        self.animation_area.draw_mechanism()
        self.animation_area.start()
        self.statusBar().showMessage("🟡 Running")

    def _on_pause(self) -> None:
        self.animation_area.pause()
        self.statusBar().showMessage("⏸ Paused")

    def _on_reset(self) -> None:
        # reset crank to initial angle, clear trace, reset timer
        self.animation_area.pause()
        self.simulation_time = 0.0
        self.animation_area.coupler_trace = None
        # set mechanism angle to initial
        self.mechanism.theta2 = float(self.theta_input.value())
        self.animation_area.draw_mechanism()
        self.statusBar().showMessage("🟢 Ready")

    def _on_speed_change(self, btn=None) -> None:
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
        """Set animation speed scale according to selected radio button (do not change ω₂)."""

        selected_btn = self.speed_btn_group.checkedButton()
        text = selected_btn.text() if selected_btn else "1×"
        factor = self.speed_options.get(text, 1.0)

        # Scale dt instead of timer interval to avoid OS timer resolution limits
        # maintaining a smooth 30ms fixed interval while advancing simulation faster/slower
        self.animation_area.set_speed_scale(factor)

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

        selected_btn = self.speed_btn_group.checkedButton()
        speed_text = selected_btn.text() if selected_btn else "1×"

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
