
from .shapes import Point, Line, Hypercycle


class Polygon:
    def __init__(self, edges=None, join=False, vertices=None):
        ''' Assumes edges are hyperbolic lines or hypercycles of intersecting
            lines '''
        if vertices is None:
            vertices = [None]*len(edges)
            for i in range(len(edges)):
                e1, e2 = edges[i-1], edges[i]
                if isinstance(e1, Point):
                    vertices[i] = e1
                    continue
                if isinstance(e2, Point):
                    vertices[i] = e2
                    continue
                pts = e1.intersectionsWithHcycle(e2)
                if len(pts) <= 0:
                    raise ValueError('Polygon edges do not intersect')
                elif len(pts) > 1:
                    raise ValueError('Polygon edge join is ambiguous')
                vertices[i] = pts[0]
        if edges is None:
            edges = [None]*len(vertices)
            for i in range(len(vertices)):
                startP, endP = vertices[i], vertices[(i+1)%len(vertices)]
                edges[i] = Line.fromPoints(*startP, *endP, segment=True)
        if join:
            edges = list(edges)
            for i, edge in enumerate(edges):
                startP, endP = vertices[i], vertices[(i+1)%len(edges)]
                if isinstance(edge, Point):
                    edges[i] = edge
                    continue
                edges[i] = edge.trimmed(*startP, *endP, chooseShorter=True)
        self.edges = tuple(edges)
        self.vertices = tuple(vertices)
    def offsetPolygon(self, offset, reverseOrder=False):
        ''' If self is a CCW polygon, returns a CCW polygon that is smaller by
            offset. '''
        edges = self.edges
        if reverseOrder:
            edges = reversed(edges)
        offEdges = [  # Maybe outer, maybe inner
            edge.makeOffset(offset)
            for edge in edges
            if not isinstance(edge, Point) or edge.isIdeal()
        ]
        return Polygon.fromEdges(offEdges, join=True)
    @staticmethod
    def fromEdges(edges, join=True):
        return Polygon(edges=edges, join=join)
    @staticmethod
    def fromVertices(vertices):
        return Polygon(vertices=vertices)
    def makeRestorePoints(self):
        ''' Returns a list of points that can be used to recreate the polygon.
            This can be used to transform the polygon.  Recreate it with
            Polygon.fromRestorePoints(points). '''
        points = []
        for vert, edge in zip(self.vertices, self.edges):
            if isinstance(edge, Point):
                continue
            points.append(vert)
            points.append(edge.midpointEuclid())
        return points
    @staticmethod
    def fromRestorePoints(points):
        n = len(points)//2
        verts = []
        edges = []
        for i in range(n):
            verts.append(points[i*2])
            edge = Hypercycle.fromPoints(*points[i*2], *points[(i*2+2)%(n*2)],
                                         *points[i*2+1], segment=True,
                                         excludeMid=False)
            edges.append(edge)
        return Polygon(edges=edges, vertices=verts, join=False)
    def toDrawables(self, elements, hwidth=None, transform=None, **kwargs):
        if hwidth is None:
            path = elements.Path(**kwargs)
            self.drawToPath(path, includeM=True, includeL=False,
                            transform=transform, **kwargs)
            path.Z()
            return (path,)
        else:
            try:
                hwidth1, hwidth2 = hwidth
            except TypeError:
                hwidth = float(hwidth)
                hwidth1, hwidth2 = -hwidth/2, hwidth/2
            path = elements.Path(**kwargs)
            outerPoly = self.offsetPolygon(hwidth1, reverseOrder=False)
            innerPoly = self.offsetPolygon(hwidth2, reverseOrder=True)
            outerPoly.drawToPath(path, includeM=True, includeL=False,
                                 transform=transform, **kwargs)
            innerPoly.drawToPath(path, includeM=False, includeL=True,
                                 transform=transform, **kwargs)
            path.Z()
            return (path,)
    def drawToPath(self, path, includeM=True, includeL=False, transform=None,
                   **kwargs):
        for i, edge in enumerate(self.edges):
            if isinstance(edge, Point):
                continue
            edge.drawToPath(path, includeM=includeM and i==0,
                            includeL=includeL and i==0, transform=transform)

