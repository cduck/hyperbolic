import math

from ..poincare import Transform, Point, Polygon
from ..poincare.util import radial_euclid_to_poincare
from . import Edge


def hyp_poly_edge_construct(p, q):
    pi, pi2 = math.pi, math.pi*2
    th = pi2/q
    phi = pi2/p
    ang1 = pi-phi/2-th/2-pi/2
    ang2 = th/2 + pi/2
    a = math.sin(ang2)/math.sin(ang1)
    b = math.sin(phi/2)/math.sin(ang1)
    r_p = math.sqrt(1/(a**2-b**2))
    r_c = a*r_p
    r_from_c = b*r_p
    t1 = pi - math.asin(r_c / (r_from_c / math.sin(phi/2)))
    t2 = pi - t1 - phi/2
    r = math.sin(t2) * (r_from_c / math.sin(phi/2))
    return r


class Tile:
    def __init__(self, vertices, touching_side=None, trans=Transform.identity(),
                 decorator=None):
        self.vertices = vertices
        self.sides = [Edge(vertices[i],vertices[(i+1)%len(self.vertices)])
                      for i in range(len(self.vertices))]
        self.touching_side = touching_side
        self.trans = trans
        self.decorator = decorator
    def set_side_codes(self, side_codes):
        for side, code in zip(self.sides, side_codes):
            side.code = code
    def copy_side_codes(self, sides):
        for side, other in zip(self.sides, sides):
            side.code = other.code
    def to_polygon(self):
        return Polygon.from_vertices(self.vertices)
    def to_drawables(self, **kwargs):
        if self.decorator is None:
            draw_verts = kwargs.get('draw_verts', False)
            if not draw_verts:
                poly = self.to_polygon()
                d = poly.to_drawables(**kwargs)
                return d
            elif draw_verts:
                lst = []
                for v in self.vertices:
                    ds = v.to_drawables(**kwargs)
                    lst.extend(ds)
                return lst
        else:
            return self.decorator.to_drawables(tile=self, **kwargs)
    def get_side(self, side_index):
        return self.sides[side_index]
    def permuted_sides(self, touching_side=None):
        if touching_side is None:
            touching_side = self.touching_side
        if touching_side is None:
            return self.sides
        sides = self.sides
        return [sides[(i+touching_side)%len(sides)]
                for i in range(len(sides))]
    def permuted_vertices(self, touching_side=None):
        if touching_side is None:
            touching_side = self.touching_side
        if touching_side is None:
            return self.sides
        vertices = self.vertices
        return [vertices[(i+touching_side)%len(vertices)]
                for i in range(len(vertices))]
    def __len__(self):
        return len(self.vertices)
    def __contains__(self, edge_or_vertex):
        if edge_or_vertex in self.vertices:
            return True
        if edge_or_vertex in self.sides:
            return True
        return False
    def uses_edge(self, edge):
        return edge in self.sides
    def make_new(self, vertices, touching_side, trans):
        '''
        Override this in subclass if __init__ has a different signature.
        '''
        tile = type(self)(
                vertices, touching_side=touching_side, trans=trans,
                decorator=self.decorator)
        tile.copy_side_codes(self.sides)
        return tile
    def make_transformed(self, trans):
        new_verts = trans.apply_to_list(self.vertices)
        total_trans = Transform.merge(self.trans, trans)
        return self.make_new(
                new_verts, touching_side=self.touching_side, trans=total_trans)
    def make_permuted(self, first_side_index):
        p = len(self.vertices)
        vertices = [self.vertices[(i+first_side_index)%p] for i in range(p)]
        if self.touching_side is None:
            touching_side = None
        else:
            touching_side = self.touching_side - first_side_index
        trans_to_origin = Transform.shift_origin(
                self.vertices[0], self.vertices[1])
        cornered_verts = trans_to_origin.apply_to_list(self.vertices)
        trans_permute_origin = Transform.shift_origin(
                cornered_verts[first_side_index],
                cornered_verts[(first_side_index+1)%p])
        trans_permute = Transform.merge(
                trans_to_origin, trans_permute_origin,
                trans_to_origin.inverted())
        trans = Transform.merge(self.trans, trans_permute)
        return self.make_new(vertices, touching_side=touching_side, trans=trans)
    @staticmethod
    def make_regular(p, q=None, inner_deg=None, er=None, hr=None, skip=1):
        assert ((q is not None) + (inner_deg is not None) + (er is not None)
                + (hr is not None) == 1), (
                'Specify exactly one of q, inner_deg, er, or hr')
        # Calculate inner_rad
        if inner_deg is not None:
            q = 360/inner_deg
            inner_rad = math.radians(inner_deg)
        elif q is not None:
            inner_rad = math.pi*2/q
        else:
            if hr is None:
                hr = radial_euclid_to_poincare(er)
            th_div2 = math.pi / p
            inner_rad = 2 * math.atan(1 / (math.tan(th_div2) * math.cosh(hr)))
        # Calculate r
        if q is None:
            if er is None:
                point_construct = Point.from_h_polar
                r = hr
            else:
                point_construct = Point.from_polar_euclid
                r = er
        else:
            r = hyp_poly_edge_construct(p, q)
            point_construct = Point.from_polar_euclid
        # Calculate polygon vertices
        verts = [
            point_construct(r, deg=-skip*i*360/p)
            for i in range(p)
        ]
        return Tile(verts)
