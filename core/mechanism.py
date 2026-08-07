"""
core/mechanism.py

Represents a planar four-bar linkage mechanism.
"""

from dataclasses import dataclass
from math import cos, sin, radians
from typing import Tuple


@dataclass
class FourBarMechanism:
    """
    Four-Bar Linkage Model

    Link Naming:

    L1 -> Ground
    L2 -> Crank
    L3 -> Coupler
    L4 -> Rocker
    """

    l1: float
    l2: float
    l3: float
    l4: float

    theta2: float = 0.0

    omega2: float = 0.0

    alpha2: float = 0.0

    direction: int = 1

    def set_crank_angle(self, angle: float):
        """Set crank angle (degrees)."""
        self.theta2 = angle

    def increment_angle(self, step: float):
        """Increment crank angle."""

        self.theta2 += self.direction * step

        self.theta2 %= 360

    def set_input_motion(
        self,
        omega: float,
        alpha: float = 0.0,
        direction: int = 1,
    ):
        """
        Define input crank motion.
        """

        self.omega2 = omega

        self.alpha2 = alpha

        self.direction = direction

    # -----------------------------------------------------
    # Joint Coordinates
    # -----------------------------------------------------

    def ground_joints(self):
        """
        Returns

        O2 ---- O4
        """

        o2 = (0.0, 0.0)

        o4 = (self.l1, 0.0)

        return o2, o4

    def crank_end(self):
        """
        End point of crank.

        Returns point A.
        """

        theta = radians(self.theta2)

        x = self.l2 * cos(theta)

        y = self.l2 * sin(theta)

        return (x, y)

    def rocker_joint(self):
        """
        Returns fixed rocker joint.
        """

        return (self.l1, 0.0)

    # -----------------------------------------------------
    # Placeholder
    # -----------------------------------------------------

    def coupler_end(self):
        """
        Will be calculated using solver.py

        Returns point B.
        """

        return None

    # -----------------------------------------------------
    # Utilities
    # -----------------------------------------------------

    def get_link_lengths(self):

        return (
            self.l1,
            self.l2,
            self.l3,
            self.l4,
        )

    def reset(self):
        """Reset mechanism."""

        self.theta2 = 0.0

        self.omega2 = 0.0

        self.alpha2 = 0.0

    def __str__(self):

        return (
            f"Ground  : {self.l1}\n"
            f"Crank   : {self.l2}\n"
            f"Coupler : {self.l3}\n"
            f"Follower: {self.l4}\n"
            f"Theta2  : {self.theta2}"
        )


if __name__ == "__main__":

    mechanism = FourBarMechanism(
        l1=120,
        l2=60,
        l3=140,
        l4=100,
    )

    mechanism.set_crank_angle(45)

    print(mechanism)

    print()

    print("Ground Joints")

    print(mechanism.ground_joints())

    print()

    print("Crank End")

    print(mechanism.crank_end())