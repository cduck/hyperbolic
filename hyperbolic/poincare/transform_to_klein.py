import math, cmath
import numpy as np

from .. import util
from . import Point, Ideal, Transform
from ..euclid import Circle, Arc, Line, intersection


class TransformToKlein:
    def __init__(self, inverse=False):
        self.inverse = inverse
    def __repr__(self):
        return '{}({})'.format(type(self).__name__,
                *'inverse=True' if self.inverse else '')
    def apply_to_tuple(self, point):
        # https://en.wikipedia.org/wiki/Poincar%C3%A9_disk_model#Relation_to_the_Klein_disk_model
        x, y = point
        if self.inverse:
            in_root = max(0., 1 - x**2 - y**2)
            denom = 1 + math.sqrt(in_root)
            return x / denom, y / denom
        else:
            denom = 1 + x**2 + y**2
            return 2 * x / denom, 2 * y / denom
    def apply_to_point(self, point):
        return Point(*self.apply_to_tuple(point))
    def apply_to_ideal(self, point, verify=False):
        x, y = self.apply_to_tuple(point)
        if verify and not util.near_zero(math.hypot(x, y) - 1):
            raise ValueError('Invalid transform')
        return Ideal(math.atan2(y, x))
    def apply_to_list(self, points, verify=False):
        if len(points) > 0:
            if isinstance(points[0], Ideal):
                if verify:
                    def f(p): return self.apply_to_ideal(p, verify=True)
                else:
                    f = self.apply_to_ideal
            elif isinstance(points[0], Point):
                f = self.apply_to_point
            else:
                f = self.apply_to_tuple
        return [f(p) for p in points]
    def apply_to_shape(self, shape):
        '''Transform a euclidean shape.

        Supports euclidean Circle, Arc, and Line.
        '''
        if isinstance(shape, (Arc, Line)):
            closed = False
            p1 = shape.start_point()
            p2 = shape.midpoint()
            p3 = shape.end_point()
        elif isinstance(shape, Circle):
            closed = True
            p1 = shape.cx+shape.r, shape.cy
            p2 = shape.cx, shape.cy+shape.r
            p3 = shape.cx-shape.r, shape.cy
            if shape.cw:
                p1, p3 = p3, p1
        else:
            raise TypeError('Unsupported shape: {}'.format(shape))
        # Transform
        p1, p2, p3 = self.apply_to_list((p1, p2, p3))
        # Create shape
        try:
            # See if it is an arc or circle
            out = Arc.from_points(*p1, *p3, *p2)
            if closed:  # It's a circle
                out = Circle(out.cx, out.cy, out.r, cw=out.cw)
            return out
        except (intersection.InfiniteIntersections, np.linalg.LinAlgError):
            # It is a line
            return Line(*p1, *p3)
    def __call__(self, *points, verify=False):
        return self.apply_to_list(points, verify=verify)
    def inverted(self):
        return TransformToKlein(inverse=True)
    @staticmethod
    def identity():
        return Transform(1,0,0,1,1)
    @staticmethod
    def merge(*transfoms):
        raise NotImplementedError()
