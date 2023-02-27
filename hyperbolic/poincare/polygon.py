from . import point, line, hypercycle


class Polygon:
    def __init__(self, edges=None, join=False, vertices=None):
        '''A shape made of connected hyperbolic line segments and hypercycle
        segments.

        Assumes adjacent edges are intersecting.
        '''
        if vertices is None:
            vertices = [None]*len(edges)
            for i in range(len(edges)):
                e1, e2 = edges[i-1], edges[i]
                if isinstance(e1, point.Point):
                    vertices[i] = e1
                    continue
                if isinstance(e2, point.Point):
                    vertices[i] = e2
                    continue
                pts = e1.intersections_with_hcycle(e2)
                if len(pts) <= 0:
                    raise ValueError('Polygon edges do not intersect')
                elif len(pts) > 1:
                    raise ValueError('Polygon edge join is ambiguous')
                vertices[i] = pts[0]
        if edges is None:
            edges = [None]*len(vertices)
            for i in range(len(vertices)):
                start_p, end_p = vertices[i], vertices[(i+1)%len(vertices)]
                edges[i] = line.Line.from_points(*start_p, *end_p, segment=True)
        if join:
            edges = list(edges)
            for i, edge in enumerate(edges):
                start_p, end_p = vertices[i], vertices[(i+1)%len(edges)]
                if isinstance(edge, point.Point):
                    edges[i] = edge
                    continue
                edges[i] = edge.trimmed(*start_p, *end_p, choose_shorter=True)
        self.edges = tuple(edges)
        self.vertices = tuple(vertices)
    def offset_polygon(self, offset, reverse_order=False):
        '''If self is a clockwise polygon, return a clockwise polygon that is
        smaller by offset, otherwise larger by offset.
        '''
        edges = self.edges
        if reverse_order:
            edges = reversed(edges)
        off_edges = [  # Maybe outer, maybe inner
            edge.make_offset(offset)
            for edge in edges
            if not isinstance(edge, point.Point) or edge.is_ideal()
        ]
        return Polygon.from_edges(off_edges, join=True)
    @staticmethod
    def from_edges(edges, join=True):
        return Polygon(edges=edges, join=join)
    @staticmethod
    def from_vertices(vertices):
        return Polygon(vertices=vertices)
    def make_restore_points(self):
        '''Return a list of points that can be used to recreate the polygon.

        This can be used to transform the polygon.  Recreate it with
        Polygon.from_restore_points(points).
        '''
        points = []
        for vert, edge in zip(self.vertices, self.edges):
            if isinstance(edge, point.Point):
                continue
            points.append(vert)
            points.append(edge.midpoint_euclid())
        return points
    @staticmethod
    def from_restore_points(points):
        n = len(points)//2
        verts = []
        edges = []
        for i in range(n):
            verts.append(points[i*2])
            edge = hypercycle.Hypercycle.from_points(
                    *points[i*2], *points[(i*2+2)%(n*2)], *points[i*2+1],
                    segment=True, exclude_mid=False)
            edges.append(edge)
        return Polygon(edges=edges, vertices=verts, join=False)
    def to_drawables(self, hwidth=None, transform=None, **kwargs):
        import drawsvg as draw
        if hwidth is None:
            path = draw.Path(**kwargs)
            self.draw_to_path(
                    path, include_m=True, include_l=False, transform=transform,
                    **kwargs)
            path.Z()
            return (path,)
        else:
            try:
                hwidth1, hwidth2 = hwidth
            except TypeError:
                hwidth = float(hwidth)
                hwidth1, hwidth2 = -hwidth/2, hwidth/2
            path = draw.Path(**kwargs)
            outer_poly = self.offset_polygon(hwidth1, reverse_order=False)
            inner_poly = self.offset_polygon(hwidth2, reverse_order=True)
            outer_poly.draw_to_path(
                    path, include_m=True, include_l=False, transform=transform,
                    **kwargs)
            inner_poly.draw_to_path(
                    path, include_m=False, include_l=True, transform=transform,
                    **kwargs)
            path.Z()
            return (path,)
    def draw_to_path(self, path, include_m=True, include_l=False,
                     transform=None, **kwargs):
        for i, edge in enumerate(self.edges):
            if isinstance(edge, point.Point):
                continue
            edge.draw_to_path(
                    path, include_m=include_m and i==0,
                    include_l=include_l and i==0, transform=transform)
