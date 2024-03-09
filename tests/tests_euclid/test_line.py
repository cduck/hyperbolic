import math

import pytest

from hyperbolic.euclid.line import Line


@pytest.mark.parametrize(
    'x1, y1, x2, y2, expected_repr',
    [
        (0, 0, 0, 0, 'Line(0, 0, 0, 0)'),
        (0.0001, 0.0001, 0.0001, 0.0001, 'Line(0.0, 0.0, 0.0, 0.0)'),
    ]
)
def test_repr(x1, y1, x2, y2, expected_repr):
    origin_line = Line(x1=x1, y1=y1, x2=x2, y2=y2)
    if expected_repr != origin_line.__repr__():
        raise ValueError(f'Expected: {expected_repr}. Got {origin_line.__repr__()}')


@pytest.mark.parametrize(
    'x1, y1, x2, y2, expected_x1, expected_y1, expected_x2, expected_y2',
    [
        (0, 0, 0, 0, 0, 0, 0, 0),
        (1, 1, -1, -1, -1, -1, 1, 1),
        (1, -1, -1, 1, -1, 1, 1, -1),
    ]
)
def test_reverse(x1, y1, x2, y2, expected_x1, expected_y1, expected_x2, expected_y2):
    line = Line(x1=x1, y1=y1, x2=x2, y2=y2)
    line.reverse()

    if (line.x1, line.y1, line.x2, line.y2) != (expected_x1, expected_y1, expected_x2, expected_y2):
        raise ValueError(
            f'Expected {(expected_x1, expected_y1, expected_x2, expected_y2)}, but got'
            f'{(line.x1, line.y1, line.x2, line.y2)}.'
        )


@pytest.mark.parametrize(
    'x1, y1, x2, y2, expected_x1, expected_y1, expected_x2, expected_y2',
    [
        (0, 0, 0, 0, 0, 0, 0, 0),
        (1, 1, -1, -1, -1, -1, 1, 1),
        (1, -1, -1, 1, -1, 1, 1, -1),
    ]
)
def test_reversed(x1, y1, x2, y2, expected_x1, expected_y1, expected_x2, expected_y2):
    line = Line(x1=x1, y1=y1, x2=x2, y2=y2)
    reversed_line = line.reversed()

    if isinstance(reversed_line, Line) is False:
        raise TypeError(f"Expected type Line, but got {type(reversed_line)}.")

    points = (reversed_line.x1, reversed_line.y1, reversed_line.x2, reversed_line.y2)
    if points != (expected_x1, expected_y1, expected_x2, expected_y2):
        raise ValueError(
            f'Expected {(expected_x1, expected_y1, expected_x2, expected_y2)}, but got'
            f'{points}.'
        )


@pytest.mark.parametrize(
    'line, expected_atan2_value',
    [
        (Line(0, 0, 0, 0), 0),
        (Line(0, 0, 1, 1), 0.7853981633974483),
        (Line(0, 0, 0, 1), 1.5707963267948966),
        (Line(0, 0, 1, 0), 0.0),
    ]
)
def test_atan2(line, expected_atan2_value):
    if line.atan2() != expected_atan2_value:
        raise ValueError(f"Expected {expected_atan2_value}, but got {line.atan2()}.")


@pytest.mark.parametrize(
    'line, expected_length',
    [
        (Line(0, 0, 0, 0), 0),
        (Line(0, 0, 1, 1), math.sqrt(2)),
        (Line(0, 0, 0, 1), 1.0),
        (Line(0, 0, 1, 0), 1.0),
    ]
)
def test_length(line, expected_length):
    if line.length() != expected_length:
        raise ValueError(f"Expected {expected_length}, but got {line.length()}.")


@pytest.mark.parametrize(
    'line_1, line_2, answer',
    [
        (Line(0, 0, 0, 0), Line(0, 0, 0, 0), True),
        (Line(0, 0, 0, 1), Line(1, 0, 1, 0), False),
        (Line(0, 0, 1, 1), Line(0, 1, 1, 0), False),
        (Line(0, 0, 1, 0), Line(1, 0, 1, 0), True),
    ]
)
def test_parallel_to(line_1, line_2, answer):
    if line_1.parallel_to(line_2) != answer:
        raise ValueError(
            f"Expected {answer}, but got {line_1.parallel_to(line_2)}, \n"
            f"for lines {line_1} and {line_2}."
        )


@pytest.mark.parametrize(
    'line_1, line_2, answer',
    [
        (Line(0, 0, 0, 0), Line(0, 0, 0, 0), True),
        (Line(0, 0, 0, 1), Line(1, 0, 1, 0), False),
        (Line(0, 0, 1, 1), Line(0, 1, 1, 0), False),
        (Line(0, 0, 1, 0), Line(1, 0, 1, 0), True),
    ]
)
def test_parallel_dir_to(line_1, line_2, answer):
    if line_1.parallel_dir_to(line_2) != answer:
        raise ValueError(
            f"Expected {answer}, but got {line_1.parallel_dir_to(line_2)}, \n"
            f"for lines {line_1} and {line_2}."
        )


@pytest.mark.parametrize(
    'line_1, line_2, answer',
    [
        (Line(0, 0, 0, 0), Line(0, 0, 0, 0), False),
        (Line(0, 0, 0, 1), Line(1, 0, 1, 0), False),
        (Line(0, 0, 1, 1), Line(0, 1, 1, 0), False),
        (Line(0, 0, 1, 0), Line(1, 0, 1, 0), False),
    ]
)
def test_anti_parallel_to(line_1, line_2, answer):
    if line_1.antiparallel_to(line_2) != answer:
        raise ValueError(
            f"Expected {answer}, but got {line_1.antiparallel_to(line_2)}, \n"
            f"for lines {line_1} and {line_2}."
        )


@pytest.mark.parametrize(
    'line, expected_point',
    [
        (Line(0, 0, 0, 0), (0, 0)),
        (Line(0, 0, 1, 1), (0, 0)),
        (Line(1, 2, 3, 4), (1, 2)),
        (Line(4, 3, 2, 1), (4, 3)),
    ]
)
def test_start_point(line, expected_point):
    if line.start_point() != expected_point:
        raise ValueError(
            f"Expected {expected_point}, but got {line.start_point()}."
        )


@pytest.mark.parametrize(
    'line, expected_point',
    [
        (Line(0, 0, 0, 0), (0, 0)),
        (Line(0, 0, 1, 1), (1, 1)),
        (Line(1, 2, 3, 4), (3, 4)),
        (Line(4, 3, 2, 1), (2, 1)),
    ]
)
def test_end_point(line, expected_point):
    if line.end_point() != expected_point:
        raise ValueError(
            f"Expected {expected_point}, but got {line.start_point()}."
        )


@pytest.mark.parametrize(
    'line, trimmed',
    [
        (Line(0, 0, 10, 10), (1, 1, 9, 9)),
        (Line(0, 0, 1, 0), (-1, 0, 2, 0))
    ]
)
def test_trimmed_with_valid_inputs(line, trimmed):
    trimmed_line = line.trimmed(*trimmed)
    assert trimmed_line.start_point() == (trimmed[0], trimmed[1])
    assert trimmed_line.end_point() == (trimmed[2], trimmed[3])


@pytest.mark.parametrize(
    "x1, y1, x2, y2, expected_midpoint",
    [
        (0, 0, 10, 10, (5, 5)),
        (-10, -10, 10, 10, (0, 0)),
        (0.5, 0.5, 2.5, 2.5, (1.5, 1.5)),
    ]
)
def test_midpoint(x1, y1, x2, y2, expected_midpoint):
    line = Line(x1, y1, x2, y2)
    assert line.midpoint() == expected_midpoint


@pytest.mark.parametrize(
    "x1, y1, x2, y2, x, y, length, expected_line",
    [
        (0, 0, 10, 10, 5, 5, 1, Line(5, 5, 4.293, 5.707)),
        (-10, -10, 10, 10, 0, 0, 2, Line(0, 0, -1.414, 1.414)),
        (0.5, 0.5, 2.5, 2.5, 1, 1, 0.5, Line(1, 1,  0.646, 1.354)),
    ]
)
def test_make_perpendicular(x1, y1, x2, y2, x, y, length, expected_line):
    line = Line(x1, y1, x2, y2)
    new_line = line.make_perpendicular(x, y, length)

    new_line_variables = vars(new_line)
    expected_line_variables = vars(expected_line)

    for variable in ['x1', 'x2', 'y1', 'y2']:
        assert abs(new_line_variables[variable] - expected_line_variables[variable]) < 10e-3


@pytest.mark.parametrize(
    "x1, y1, x2, y2, x, y, expected_result",
    [
        (0, 0, 10, 10, 5, 5, True),
        (-10, -10, 10, 10, 0, 0, True),
        (0.5, 0.5, 2.5, 2.5, 1, 1, True),
        (0, 0, 10, 10, 15, 15, False),
        (-10, -10, 10, 10, 15, 15, False),
        (0.5, 0.5, 2.5, 2.5, 3, 3, False),
    ]
)
def test_is_point_on_segment(x1, y1, x2, y2, x, y, expected_result):
    line = Line(x1, y1, x2, y2)
    assert line.is_point_on_segment(x, y) == expected_result