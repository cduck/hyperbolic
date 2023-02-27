import math

from .. import util
from . import ellipse


class EllipseArc(ellipse.Ellipse):
    def __init__(self, cx, cy, rx, ry, rot_deg, start_deg, end_deg, cw=True):
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry
        self.rot_deg = rot_deg
        self.start_deg = start_deg
        self.end_deg = end_deg
        self.cw = cw

    def start_point(self):
        return self.point_at_angle(self.start_deg)

    def end_point(self):
        return self.point_at_angle(self.end_deg)

    def mid_degree(self):
        if not self.cw:
            start_deg, end_deg = self.end_deg, self.start_deg
        else:
            start_deg, end_deg = self.start_deg, self.end_deg
        diff_deg = (end_deg - start_deg) % 360
        return (start_deg + diff_deg/2) % 360

    def midpoint(self):
        return self.point_at_angle(self.mid_degree())

    def reversed(self):
        return EllipseArc(self.cx, self.cy, self.rx, self.ry, self.rot_deg,
                          self.end_deg, self.start_deg, cw=not self.cw)

    @staticmethod
    def from_bounding_quad(x0, y0, x1, y1, x2, y2, x3, y3, sx, sy, ex, ey, mx,
                           my, exclude_mid=False):
        e = ellipse.Ellipse.from_bounding_quad(x0, y0, x1, y1, x2, y2, x3, y3)
        if e is None:
            return None  # Degenerate ellipse
        sx, ex, mx = sx-e.cx, ex-e.cx, mx-e.cx
        sy, ey, my = sy-e.cy, ey-e.cy, my-e.cy
        start_deg = math.degrees(math.atan2(sy, sx))
        end_deg = math.degrees(math.atan2(ey, ex))
        mid_deg = math.degrees(math.atan2(my, mx))
        # Clockwise around ellipse if mid_deg is not between start and end
        cw = (mid_deg-start_deg)%360 <= (end_deg-start_deg)%360
        cw = cw ^ exclude_mid
        return EllipseArc(e.cx, e.cy, e.rx, e.ry, e.rot_deg, start_deg, end_deg,
                          cw=cw)

    def draw_to_path(self, path, include_m=True, include_l=False):
        sx, sy = self.start_point()
        ex, ey = self.end_point()
        large_arc = ((self.end_deg - self.start_deg) % 360 <= 180) ^ self.cw
        if include_l:
            path.L(sx, sy)
        elif include_m:
            path.M(sx, sy)
        path.A(self.rx, self.ry, self.rot_deg, large_arc, self.cw, ex, ey)

    def to_drawables(self, **kwargs):
        import drawsvg as draw
        path = draw.Path(**kwargs)
        self.draw_to_path(path, include_m=True)
        return (path,)
