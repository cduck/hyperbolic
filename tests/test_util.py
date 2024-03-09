import pytest
from hyperbolic.util import (
    near_zero,
    circ_inv,
)



@pytest.mark.parametrize(
    'val, expected_output',
    [(0, True), (2**-30, True), (2**-29, False), (-2**-29, False), (1, False)],
)
def test_near_zero(val, expected_output):
    if near_zero(val=val) is not expected_output:
        raise ValueError(F"Expected {expected_output}, got {near_zero(val=val)}.")


@pytest.mark.parametrize('x, y, cx, cy, r, expected',
    [
        (1, 1, 0, 0, 1, (0.5, 0.5)),
        (1, 1, 2, 2, 2, (0.0, 0.0)),
        (-1, -1, 0, 0, 1, (-0.5, -0.5)),
    ]
)
def test_circ_inv(x, y, cx, cy, r, expected):
    result = circ_inv(x, y, cx, cy, r)
    if result != expected:
        raise ValueError(f"Expected {expected}, got {result}.")
