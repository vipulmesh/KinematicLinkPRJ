"""
core/utils.py

Utility functions used across the 4-Bar Kinematic Chain Simulator.

This module provides small helpers for unit conversions and numeric
operations used by the GUI and exporters. It intentionally avoids
duplicating solver logic.
"""

from __future__ import annotations

from typing import Iterable, List
import numpy as np


def deg2rad(deg: float) -> float:
    """Convert degrees to radians."""

    return float(np.deg2rad(deg))


def rad2deg(rad: float) -> float:
    """Convert radians to degrees."""

    return float(np.rad2deg(rad))


def ensure_sequence_length(seq: Iterable[float], length: int) -> List[float]:
    """Ensure an iterable is converted to a list of specified length.

    Raises ValueError if lengths do not match.
    """

    lst = list(seq)
    if len(lst) != length:
        raise ValueError(f"Expected sequence length {length}, got {len(lst)}")
    return lst


def linspace_like(x: Iterable[float], n: int):
    """Generate `n` points spanning the min/max of `x`.

    Convenience for plotting functions when a uniformly sampled domain
    is required.
    """

    arr = np.asarray(list(x), dtype=float)
    return np.linspace(arr.min(), arr.max(), n)
