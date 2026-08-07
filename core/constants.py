"""
core/constants.py

Contains application-wide constants used throughout the simulator.
"""

# ==========================================================
# Window Configuration
# ==========================================================

WINDOW_TITLE = "4-Bar Kinematic Chain Simulator"

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800


# ==========================================================
# Animation Configuration
# ==========================================================

FPS = 60
TIME_STEP = 1 / FPS

CRANK_STEP = 2.0          # degrees per frame

DEFAULT_SCALE = 1.0


# ==========================================================
# Plot Configuration
# ==========================================================

PLOT_POINTS = 360


# ==========================================================
# Colors
# ==========================================================

GROUND_COLOR = "black"

CRANK_COLOR = "red"

COUPLER_COLOR = "blue"

FOLLOWER_COLOR = "green"

JOINT_COLOR = "orange"

TRACE_COLOR = "purple"


# ==========================================================
# Default Link Lengths
# ==========================================================

DEFAULT_L1 = 120.0

DEFAULT_L2 = 60.0

DEFAULT_L3 = 140.0

DEFAULT_L4 = 100.0


# ==========================================================
# Angular Values
# ==========================================================

DEFAULT_THETA2 = 0.0

DEFAULT_OMEGA2 = 10.0          # rad/sec

DEFAULT_ALPHA2 = 0.0


# ==========================================================
# Numerical Solver
# ==========================================================

MAX_ITERATIONS = 100

SOLVER_TOLERANCE = 1e-8


# ==========================================================
# Validation
# ==========================================================

MIN_LINK_LENGTH = 1.0

MAX_LINK_LENGTH = 10000.0


# ==========================================================
# Mechanism Types
# ==========================================================

DOUBLE_CRANK = "Double Crank"

CRANK_ROCKER = "Crank Rocker"

DOUBLE_ROCKER = "Double Rocker"

CHANGE_POINT = "Change Point"

NON_GRASHOF = "Non-Grashof"


# ==========================================================
# Rotation Direction
# ==========================================================

CLOCKWISE = -1

COUNTER_CLOCKWISE = 1