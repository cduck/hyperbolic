from ..poincare import Line


class Edge:
    def __init__(self, p1, p2, code=None):
        self.p1 = p1
        self.p2 = p2
        self.code = code
    def __eq__(self, other):
        return self.same_as(other) or self.inverse_of(other)
    def inverse_of(self, other):
        return self.p1==other.p2 and self.p2==other.p1
    def same_as(self, other):
        return self.p1==other.p1 and self.p2==other.p2
    def to_drawables(self, draw_verts=False, **kwargs):
        if not draw_verts:
            poly = Line.from_points(*self.p1, *self.p2, segment=True)
            d = poly.to_drawables(**kwargs)
            return d
        elif draw_verts:
            d1 = self.p1.to_drawables(**kwargs)
            d2 = self.p2.to_drawables(**kwargs)
            return (d1, d2)
