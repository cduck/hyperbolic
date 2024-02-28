import pytest

from hyperbolic.euclid.line import Line
from hyperbolic.euclid.origin_line import OriginLine


@pytest.mark.parametrize(
    'px, py, expected_repr',
    [
        (0, 0, 'OriginLine(0, 0)'),
        (0.0001, 0.0001, 'OriginLine(0.0, 0.0)'),
    ]
)
def test_repr(px, py, expected_repr):
    origin_line = OriginLine(px=px, py=py)
    if expected_repr != origin_line.__repr__():
        raise ValueError(f'Expected: {expected_repr}. Got {origin_line.__repr__()}')


@pytest.mark.parametrize(
    'px, py, expected_line',
    [
        (1, 1, Line(0, 0, 1, 1)),
        (0, 0, Line(0, 0, 0, 0)),
    ]
)
def test_to_line(px, py, expected_line):
    origin_line = OriginLine(px=px, py=py)
    line = origin_line.to_line()
    if isinstance(line, Line) is False and line.__dict__ != expected_line.__dict__:
        raise ValueError(f'Expected: {expected_line}. Got {origin_line.to_line()}')


@pytest.mark.parametrize(
    'px, py, expected_px, expected_py',
    [
        (0, 0, 0, 0),
        (1, 1, -1, -1),
        (1, -1, -1, 1),
    ]
)
def test_reverse(px, py, expected_px, expected_py):
    origin_line = OriginLine(px=px, py=py)
    origin_line.reverse()

    error_message = ''
    if origin_line.px != expected_px:
        error_message += f'Expected {expected_px} for px. Got {origin_line.px}\n '

    if origin_line.py != expected_py:
        error_message += f'Expected {expected_py} for px. Got {origin_line.py}\n '

    if error_message:
        raise ValueError(error_message)


@pytest.mark.parametrize(
    'original_line, reversed_line',
    [
        (OriginLine(0, 0), OriginLine(0, 0)),
        (OriginLine(1, 0), OriginLine(-1, 0)),
        (OriginLine(0, 1), OriginLine(0, -1)),
        (OriginLine(1, 1), OriginLine(-1, -1)),
    ]
)
def test_reversed(original_line, reversed_line):
    reversed_original_line = original_line.reversed()

    if isinstance(reversed_original_line, OriginLine) is False:
        raise TypeError(f'Expected instance of class Originline. Got {type(reversed_original_line)}.')
    if reversed_original_line.__dict__ != reversed_line.__dict__:
        raise ValueError(f'Expected {reversed_original_line.__dict__}. Got {reversed_line.__dict__}.')

