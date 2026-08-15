"""
core/validation.py

Validation utilities for Four-Bar Mechanism.
"""

from core.constants import (
    MIN_LINK_LENGTH,
    MAX_LINK_LENGTH,
    DOUBLE_CRANK,
    CRANK_ROCKER,
    DOUBLE_ROCKER,
    CHANGE_POINT,
    NON_GRASHOF,
)


class ValidationError(Exception):
    """Custom exception for invalid mechanism input."""
    pass


def validate_link_lengths(l1, l2, l3, l4):
    """
    Validate basic link lengths.

    Returns
    -------
    (bool, str)
        Validation status and message.
    """

    links = [l1, l2, l3, l4]

    # Check numeric values
    for value in links:
        if not isinstance(value, (int, float)):
            return False, "All link lengths must be numeric."

    # Positive lengths
    for value in links:
        if value <= 0:
            return False, "Link lengths must be greater than zero."

    # Range check
    for value in links:
        if value < MIN_LINK_LENGTH or value > MAX_LINK_LENGTH:
            return (
                False,
                f"Link lengths must be between "
                f"{MIN_LINK_LENGTH} and {MAX_LINK_LENGTH}.",
            )

    return True, "Input is valid."


def grashof_check(l1, l2, l3, l4):
    """
    Check Grashof's Law.

    Returns
    -------
    tuple
        (is_grashof, shortest, longest)
    """

    links = [l1, l2, l3, l4]

    shortest = min(links)
    longest = max(links)

    remaining = sorted(links)
    remaining.remove(shortest)
    remaining.remove(longest)

    p, q = remaining

    is_grashof = (shortest + longest) <= (p + q)

    return is_grashof, shortest, longest


def classify_mechanism(l1, l2, l3, l4):
    """
    Classify the four-bar mechanism.

    Link numbering:

    L1 = Ground
    L2 = Crank
    L3 = Coupler
    L4 = Rocker

    Returns
    -------
    str
        Mechanism type.
    """

    links = [l1, l2, l3, l4]

    shortest = min(links)
    longest = max(links)

    remaining = sorted(links)
    remaining.remove(shortest)
    remaining.remove(longest)

    p, q = remaining

    total_short_long = shortest + longest
    total_middle = p + q

    # Non-Grashof
    if total_short_long > total_middle:
        return NON_GRASHOF

    # Change point
    if total_short_long == total_middle:
        return CHANGE_POINT

    # Grashof Classification
    if shortest == l1:
        return DOUBLE_CRANK

    elif shortest == l2:
        return CRANK_ROCKER

    elif shortest == l4:
        return CRANK_ROCKER

    else:
        return DOUBLE_ROCKER


def validate_mechanism(l1, l2, l3, l4):
    """
    Complete validation routine.

    Returns
    -------
    dict
    """

    ok, message = validate_link_lengths(l1, l2, l3, l4)

    if not ok:
        return {
            "valid": False,
            "message": message,
            "grashof": False,
            "type": None,
        }

    grashof, shortest, longest = grashof_check(
        l1,
        l2,
        l3,
        l4,
    )

    mech_type = classify_mechanism(
        l1,
        l2,
        l3,
        l4,
    )

    return {
        "valid": True,
        "message": "Mechanism validated successfully.",
        "grashof": grashof,
        "type": mech_type,
        "shortest": shortest,
        "longest": longest,
    }


if __name__ == "__main__":

    result = validate_mechanism(
        120,
        60,
        140,
        100,
    )

    print(result)