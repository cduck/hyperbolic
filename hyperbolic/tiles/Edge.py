
from ..poincare.shapes import Line


class Edge:
    def __init__(self, p1, p2, code=None):
        self.p1 = p1
        self.p2 = p2
        self.code = code
    def __eq__(self, other):
        return self.sameAs(other) or self.inverseOf(other)
    def inverseOf(self, other):
        return self.p1==other.p2 and self.p2==other.p1
    def sameAs(self, other):
        return self.p1==other.p1 and self.p2==other.p2
    def toDrawables(self, elements, drawVerts=False, **kwargs):
        if not drawVerts:
            poly = Line.fromPoints(*self.p1, *self.p2, segment=True)
            d = poly.toDrawables(elements, **kwargs)
            return d
        elif drawVerts:
            d1 = self.p1.toDrawables(elements, **kwargs)
            d2 = self.p2.toDrawables(elements, **kwargs)
            return (d1, d2)

