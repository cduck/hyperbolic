import numpy as np

from .. import util
from . import line


class Ellipse:
    def __init__(self, cx, cy, rx, ry, rot_deg=0):
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry
        self.rot_deg = rot_deg

    @property
    def rot(self):
        return np.deg2rad(self.rot_deg)

    def point_at_angle(self, deg):
        rad = np.deg2rad(deg - self.rot_deg)
        s = 1/(np.cos(rad)**2/self.rx**2+np.sin(rad)**2/self.ry**2)**0.5
        x, y = s*np.cos(np.deg2rad(deg)), s*np.sin(np.deg2rad(deg))
        return x+self.cx, y+self.cy

    def semi_major_line(self):
        '''Return a line along the semi-major axis, assuming rx is along the
        semi-major axis.
        '''
        rot = self.rot
        x = self.cx + self.rx * np.cos(rot)
        y = self.cy + self.rx * np.sin(rot)
        return line.Line.from_points(self.cx, self.cy, x, y)

    def semi_minor_line(self):
        '''Return a line along the semi-minor axis, assuming ry is along the
        semi-minor axis.
        '''
        rot = self.rot
        x = self.cx + self.ry * -np.sin(rot)
        y = self.cy + self.ry * np.cos(rot)
        return line.Line.from_points(self.cx, self.cy, x, y)

    @staticmethod
    def from_foci(x1, y1, x2, y2, rx):
        center_line = line.Line.from_points(x1, y1, x2, y2)
        cx, cy = center_line.midpoint()
        rot_deg = np.rad2deg(center_line.atan2())
        t = (rx**2 - center_line.length()**2)
        if t <= 1e-14:
            raise ValueError('Degenerate major radius length.')
        ry = t ** 0.5
        return Ellipse(cx, cy, rx, ry, rot_deg)

    @staticmethod
    def _fromCoefficients(a, b, c, d, f, g):
        '''Return the ellipse defined by the parametric equation
        ax2 + 2bxy + cy2 + 2dx + 2fy + g = 0.
        '''
        if util.near_zero(b*b - a*c):
            # Degenerate (point) ellipse
            return None
        # Equations 19-23 of https://mathworld.wolfram.com/Ellipse.html
        cx = (c*d - b*f) / (b*b - a*c)
        cy = (a*f - b*d) / (b*b - a*c)
        rx = (2 * (a*f*f+c*d*d+g*b*b-2*b*d*f-a*c*g)
              / ((b*b-a*c) * (((a-c)**2+4*b*b)**0.5 - (a+c)))
             ) ** 0.5
        ry = (2 * (a*f*f+c*d*d+g*b*b-2*b*d*f-a*c*g)
              / ((b*b-a*c) * (-((a-c)**2+4*b*b)**0.5 - (a+c)))
             ) ** 0.5
        rot_deg = np.rad2deg(0.5*np.arctan2(2*b, a-c))
        rot_deg += 180 * (a > c) - 90
        return Ellipse(cx, cy, rx, ry, rot_deg=rot_deg)

    def get_bounding_quad(self):
        rot = self.rot
        sx = self.rx * np.cos(rot)
        sy = self.rx * np.sin(rot)
        tx = self.ry * -np.sin(rot)
        ty = self.ry * np.cos(rot)
        return ((self.cx-sx+tx, self.cy-sy+ty),
                (self.cx+sx+tx, self.cy+sy+ty),
                (self.cx+sx-tx, self.cy+sy-ty),
                (self.cx-sx-tx, self.cy-sy-ty))

    @staticmethod
    def from_bounding_quad(x0, y0, x1, y1, x2, y2, x3, y3):
        # Equations from http://chrisjones.id.au/Ellipses/ellipse.html
        mat = np.array([
            [ x1*x2*y3 - x0*x2*y3 - x1*y2*x3 + x0*y2*x3 - x0*y1*x3 + y0*x1*x3 + x0*y1*x2 - y0*x1*x2,
              x0*x2*y3 - x0*x1*y3 - x1*y2*x3 + y1*x2*x3 - y0*x2*x3 + y0*x1*x3 + x0*x1*y2 - x0*y1*x2,
              x1*x2*y3 - x0*x1*y3 - x0*y2*x3 - y1*x2*x3 + y0*x2*x3 + x0*y1*x3 + x0*x1*y2 - y0*x1*x2,
            ],
            [ y1*x2*y3 - y0*x2*y3 - x0*y1*y3 + y0*x1*y3 - y1*y2*x3 + y0*y2*x3 + x0*y1*y2 - y0*x1*y2,
             -x1*y2*y3 + x0*y2*y3 + y1*x2*y3 - x0*y1*y3 - y0*y2*x3 + y0*y1*x3 + y0*x1*y2 - y0*y1*x2,
              x1*y2*y3 - x0*y2*y3 + y0*x2*y3 - y0*x1*y3 - y1*y2*x3 + y0*y1*x3 + x0*y1*y2 - y0*y1*x2,
            ],
            [ x1*y3 - x0*y3 - y1*x3 + y0*x3 - x1*y2 + x0*y2 + y1*x2 - y0*x2,
              x2*y3 - x1*y3 - y2*x3 + y1*x3 + x0*y2 - y0*x2 - x0*y1 + y0*x1,
              x2*y3 - x0*y3 - y2*x3 + y0*x3 + x1*y2 - y1*x2 + x0*y1 - y0*x1,
            ]
        ], dtype=float)

        try:
            (j, k, l), (m, n, o), (p, q, r) = np.linalg.inv(mat)
        except np.linalg.LinAlgError:
            # Degenerate ellipse
            return None
        a = j*j + m*m - p*p
        b = j*k + m*n - p*q
        c = k*k + n*n - q*q
        d = j*l + m*o - p*r
        f = k*l + n*o - q*r
        g = l*l + o*o - r*r
        return Ellipse._fromCoefficients(a, b, c, d, f, g)

    def draw_to_path(self, path, include_m=True, include_l=False, cw=True):
        rot = self.rot
        sx = self.rx * np.cos(rot)
        sy = self.rx * np.sin(rot)
        ex, ey = -sx, -sy
        if include_l:
            path.L(self.cx+sx, self.cy+sy)
        elif include_m:
            path.M(self.cx+sx, self.cy+sy)
        path.A(self.rx, self.ry, self.rot_deg, False^cw, cw,
               self.cx+ex, self.cy+ey)
        path.A(self.rx, self.ry, self.rot_deg, True^cw, cw,
               self.cx+sx, self.cy+sy)

    def to_drawables(self, **ellipse_args):
        import drawsvg as draw
        trans = 'translate({}, {}) rotate({}) translate({}, {})'.format(
            self.cx, self.cy, self.rot_deg, -self.cx, -self.cy)
        if 'transform' in ellipse_args:
            ellipse_args['transform'] += ' ' + trans
        else:
            ellipse_args['transform'] = trans
        yield draw.Ellipse(self.cx, self.cy, self.rx, self.ry,
                               **ellipse_args)
