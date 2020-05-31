
import numpy as np

from .. import util
from . import shapes, intersection

class Ellipse:
    def __init__(self, cx, cy, rx, ry, rotDeg=0):
        self.cx = cx
        self.cy = cy
        self.rx = rx
        self.ry = ry
        self.rotDeg = rotDeg

    @property
    def rot(self):
        return np.deg2rad(self.rotDeg)

    def pointAtAngle(self, deg):
        rad = np.deg2rad(deg - self.rotDeg)
        s = 1/(np.cos(rad)**2/self.rx**2+np.sin(rad)**2/self.ry**2)**0.5
        x, y = s*np.cos(np.deg2rad(deg)), s*np.sin(np.deg2rad(deg))
        return x+self.cx, y+self.cy

    def semiMajorLine(self):
        ''' Assumes rx is the semi-major axis and ry is minor '''
        rot = self.rot
        x = self.cx + self.rx * np.cos(rot)
        y = self.cy + self.rx * np.sin(rot)
        return shapes.Line.fromPoints(self.cx, self.cy, x, y)

    def semiMinorLine(self):
        ''' Assumes rx is the semi-major axis and ry is minor '''
        rot = self.rot
        x = self.cx + self.ry * -np.sin(rot)
        y = self.cy + self.ry * np.cos(rot)
        return shapes.Line.fromPoints(self.cx, self.cy, x, y)

    @staticmethod
    def fromFoci(x1, y1, x2, y2, rx):
        centerLine = shapes.Line.fromPoints(x1, y1, x2, y2)
        cx, cy = centerLine.midpoint()
        rotDeg = np.rad2deg(centerLine.atan2())
        t = (rx**2 - centerLine.length()**2)
        if t <= 1e-14:
            raise ValueError('Degenerate major radius length.')
        ry = t ** 0.5
        return Ellipse(cx, cy, rx, ry, rotDeg)

    @staticmethod
    def _fromCoefficients(a, b, c, d, f, g):
        ''' Returns the ellipse defined by ax2 + 2bxy + cy2 + 2dx + 2fy + g = 0
        '''
        if util.nearZero(b*b - a*c):
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
        rotDeg = np.rad2deg(0.5*np.arctan2(2*b, a-c))
        rotDeg += 180 * (a > c) - 90
        return Ellipse(cx, cy, rx, ry, rotDeg=rotDeg)

    def getBoundingQuad(self):
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
    def fromBoundingQuad(x0, y0, x1, y1, x2, y2, x3, y3):
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

    def drawToPath(self, path, includeM=True, includeL=False, cw=False):
        rot = self.rot
        sx = self.rx * np.cos(rot)
        sy = self.rx * np.sin(rot)
        ex, ey = -sx, -sy
        if includeL:
            path.L(self.cx+sx, self.cy+sy)
        elif includeM:
            path.M(self.cx+sx, self.cy+sy)
        path.A(self.rx, self.ry, -self.rotDeg, False^cw, cw,
               self.cx+ex, self.cy+ey)
        path.A(self.rx, self.ry, -self.rotDeg, True^cw, cw,
               self.cx+sx, self.cy+sy)

    def toDrawables(self, elements, **ellipseArgs):
        trans = 'translate({}, {}) rotate({}) translate({}, {})'.format(
            self.cx, -self.cy, -self.rotDeg, -self.cx, self.cy)
        if 'transform' in ellipseArgs:
            ellipseArgs['transform'] += ' ' + trans
        else:
            ellipseArgs['transform'] = trans
        yield elements.Ellipse(self.cx, self.cy, self.rx, self.ry,
                               **ellipseArgs)
