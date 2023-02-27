import math

from .. import util
from ..euclid import Circle, Arc, Line as ELine, intersection
from . import hypercycle


class Line(hypercycle.Hypercycle):
    def __init__(self, proj_shape, segment=False):
        # TODO: Verify that this is a hyperbolic line, not hypercycle
        super().__init__(proj_shape, segment=segment)
    @classmethod
    def from_hypercycle_offset(cls, *args, **kwargs):
        raise TypeError('Not supported for Line subclass')
    @classmethod
    def from_points(cls, x1, y1, x2, y2, segment=False, **kwargs):
        if util.near_zero(x1-x2) and util.near_zero(y1-y2):
            raise ValueError('Start and end points are the same')
        if cls._pointsInlineWithOrigin(x1, y1, x2, y2):
            if segment:
                shape = ELine(x1, y1, x2, y2)
                return cls(shape, segment=True, **kwargs)
            else:
                line_rad = math.atan2(y2-y1, x2-x1)
                sx, sy = math.cos(line_rad), math.sin(line_rad)
                shape = ELine(-sx, -sy, sx, sy)
                return cls(shape, segment=False, **kwargs)
        r1 = math.hypot(x1, y1)
        r2 = math.hypot(x2, y2)
        if util.near_zero(r1-1) and util.near_zero(r2-1):
            # Both points are ideal points so circ_inv will not give a 3rd point
            a1 = math.atan2(y1, x1)
            a2 = math.atan2(y2, x2)
            swap = (a2 - a1) % (math.pi*2) > math.pi
            if swap:
                a1, a2 = a2, a1
            a_diff = (a2 - a1) % (math.pi*2)
            assert a_diff <= math.pi
            center_dist = 1/math.cos(a_diff/2)
            center_ang = a1 + a_diff/2
            cx = math.cos(center_ang) * center_dist
            cy = math.sin(center_ang) * center_dist
            r = center_dist * math.sin(a_diff/2)
            arc_deg = 180 - math.degrees(a_diff)
            arc_start_deg = math.degrees(a1) - 90
            arc_end_deg = arc_start_deg - arc_deg
            if swap:
                arc_start_deg, arc_end_deg = arc_end_deg, arc_start_deg
            arc = Arc(cx, cy, r, arc_end_deg, arc_start_deg, cw=not swap)
            return cls(arc, segment=False, **kwargs)
            # Even if segment is True, the given points span the
            # entire line so it isn't a segment
        else:
            ex_mid = True
            if util.near_zero(r1-1):
                x3, y3 = util.circ_inv(x2, y2)
                if r2 > 1:
                    ex_mid = False
            else:
                x3, y3 = util.circ_inv(x1, y1)
                if r1 > 1:
                    ex_mid = False
            arc = Arc.from_points(x1, y1, x2, y2, x3, y3, exclude_mid=ex_mid)
            if segment:
                return cls(arc, segment=True, **kwargs)
            else:
                x1, y1, x2, y2 = intersection.circle_circle(arc, Circle(0,0,1))
                if not arc.cw:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                arc_full = Arc.from_points(
                        x1, y1, x2, y2, x3, y3, exclude_mid=ex_mid)
                assert arc.cw == arc_full.cw
                return cls(arc_full, segment=False, **kwargs)
