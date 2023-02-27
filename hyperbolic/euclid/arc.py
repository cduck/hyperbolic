import math

from .. import util
from . import circle


class Arc(circle.Circle):
    def __init__(self, cx, cy, r, start_deg, end_deg, cw=True):
        super().__init__(cx, cy, r)
        self.start_deg = start_deg
        self.end_deg = end_deg
        self.cw = cw
    def __repr__(self):
        return '{}({},{}, {}, {},{},{})'.format(type(self).__name__,
                round(self.cx, 3), round(self.cy, 3), round(self.r, 3),
                round(self.start_deg, 3), round(self.end_deg, 3),
                self.cw)
    def start_point(self):
        x = self.r * math.cos(math.radians(self.start_deg))
        y = self.r * math.sin(math.radians(self.start_deg))
        return self.cx+x, self.cy+y
    def end_point(self):
        x = self.r * math.cos(math.radians(self.end_deg))
        y = self.r * math.sin(math.radians(self.end_deg))
        return self.cx+x, self.cy+y
    def mid_degree(self):
        if not self.cw:
            start_deg, end_deg = self.end_deg, self.start_deg
        else:
            start_deg, end_deg = self.start_deg, self.end_deg
        diff_deg = (end_deg - start_deg) % 360
        return (start_deg + diff_deg/2) % 360
    def midpoint(self):
        ang = math.radians(self.mid_degree())
        return (self.cx + self.r * math.cos(ang),
                self.cy + self.r * math.sin(ang))
    def reverse(self):
        self.start_deg, self.end_deg = self.end_deg, self.start_deg
        self.cw = not self.cw
    def reversed(self):
        return Arc(self.cx, self.cy, self.r, self.end_deg, self.start_deg,
                   cw=not self.cw)
    def is_point_on_segment(self, x, y):
        '''Return True if (x, y) is on this arc, assuming the given point is on
        the circle.
        '''
        start_deg, end_deg = self.start_deg % 360, self.end_deg % 360
        if self.cw:
            start_deg, end_deg = end_deg, start_deg
        px = x - self.cx
        py = y - self.cy
        p_deg = math.degrees(math.atan2(py, px)) % 360
        if util.near_zero(p_deg-start_deg) or util.near_zero(p_deg-end_deg):
            return True
        if start_deg<end_deg:
            return start_deg<=p_deg<=end_deg
        else:
            return (end_deg<=p_deg) ^ (p_deg<=start_deg)
    @classmethod
    def from_points(cls, sx, sy, ex, ey, mx, my, exclude_mid=False, **kwargs):
        cx, cy, rad = cls._centerRadFromPoints(sx, sy, ex, ey, mx, my)
        sx, ex, mx = sx-cx, ex-cx, mx-cx
        sy, ey, my = sy-cy, ey-cy, my-cy
        start_deg = math.degrees(math.atan2(sy, sx))
        end_deg = math.degrees(math.atan2(ey, ex))
        mid_deg = math.degrees(math.atan2(my, mx))
        # Clockwise around circle if mid_deg is not between start and end
        cw = (mid_deg-start_deg)%360 <= (end_deg-start_deg)%360
        cw = cw ^ exclude_mid
        return cls(cx, cy, rad, start_deg, end_deg, cw=cw, **kwargs)
    @classmethod
    def from_points_with_center(cls, sx, sy, ex, ey, cx, cy,
                                r=None, cw=True, **kwargs):
        sx, sy, ex, ey = sx-cx, sy-cy, ex-cx, ey-cy
        sr = math.hypot(sx, sy)
        er = math.hypot(ex, ey)
        if r is None:
            r = (sr + er) / 2
        assert util.near_zero(sr-r) and util.near_zero(er-r), 'Rounding error'
        start_deg = math.degrees(math.atan2(sy, sx))
        end_deg = math.degrees(math.atan2(ey, ex))
        return cls(cx, cy, r, start_deg, end_deg, cw=cw, **kwargs)
    def to_drawables(self, **kwargs):
        import drawsvg as draw
        return (draw.Arc(self.cx, self.cy, self.r, self.start_deg,
                 self.end_deg, cw=self.cw, **kwargs),)
    def draw_to_path(self, path, include_m=True, include_l=False):
        path.arc(self.cx, self.cy, self.r, self.start_deg, self.end_deg,
                 cw=self.cw, include_m=include_m, include_l=include_l)
