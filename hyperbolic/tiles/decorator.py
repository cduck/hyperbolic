from ..poincare import Transform, Point, Polygon
from ..poincare.util import radial_poincare_to_euclid


class TileDecorator:
    def to_drawables(self, tile=None, **kwargs):
        if tile is None: return ()
        poly = tile.to_polygon()
        ds = poly.to_drawables(**kwargs)
        return ds

class TileDecoratorNull(TileDecorator):
    def to_drawables(self, tile=None, **kwargs):
        return ()

class TileDecoratorOffset(TileDecorator):
    def __init__(self, offset):
        super().__init__()
        self.offset = offset
    def to_drawables(self, tile=None, **kwargs):
        if tile is None: return ()
        poly = tile.to_polygon()
        poly = poly.offset_polygon(self.offset)
        ds = poly.to_drawables(**kwargs)
        return ds

class TileDecoratorPolygons(TileDecorator):
    def __init__(self, *polys, poly_descs=[]):
        self.poly_descs = [p.make_restore_points() for p in polys]
        self.poly_descs.extend(poly_descs)
    def to_drawables(self, tile=None, **kwargs):
        if tile is None:
            trans = Transform.identity()
        else:
            trans = tile.trans
        ds = []
        for poly_desc in self.poly_descs:
            d = self.desc_to_drawables(poly_desc, trans, **kwargs)
            ds.extend(d)
        return ds
    def desc_to_drawables(self, poly_desc, trans, **kwargs):
        poly_desc = trans.apply_to_list(poly_desc)
        poly = Polygon.from_restore_points(poly_desc)
        return poly.to_drawables(**kwargs)

class TileDecoratorLateInit(TileDecorator):
    def __init__(self):
        self.delegate = None
        self.style = dict()
    def setup(self, delegate, **style):
        self.delegate = delegate
        self.style = style
    def to_drawables(self, tile=None, **kwargs):
        if self.delegate is None:
            if tile is not None:
                dec = tile.decorator
                tile.decorator = None
                ds = tile.to_drawables(**self.style, **kwargs)
                tile.decorator = dec
                return ds
        else:
            return self.delegate.to_drawables(tile=tile, **self.style, **kwargs)

class TileDecoratorNumbered(TileDecorator):
    def __init__(self, size=0.1, trans=Transform.identity(), **style):
        self.index = 0
        self.size = size
        self.trans = trans
        self.style = style
    def to_drawables(self, tile=None, layer=1, **kwargs):
        import drawsvg as draw
        ds = []
        if layer == 0 and tile is not None:
            dec = tile.decorator
            tile.decorator = None
            ds = tile.to_drawables(**kwargs)
            tile.decorator = dec
            return ds
        if layer == 1:
            pt = Point(0,0)
            trans = self.trans
            if tile is not None:
                trans = Transform.merge(trans, tile.trans)
            pt = trans.apply_to_point(pt)
            e1 = radial_poincare_to_euclid(pt.hr - self.size/2)
            e2 = radial_poincare_to_euclid(pt.hr + self.size/2)
            e_size = e2 - e1
            text = str(self.index)
            self.index += 1
            return (draw.Text(
                    text, e_size, *pt, center=True, **self.style, **kwargs),)
        return ()
