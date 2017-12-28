
from ..poincare import Transform
from ..poincare.shapes import Point, Polygon
from ..poincare.util import radialPoincareToEuclid


class TileDecorator:
    def toDrawables(self, elements, tile=None, **kwargs):
        if tile is None: return ()
        poly = tile.toPolygon()
        ds = poly.toDrawables(elements, **kwargs)
        return ds

class TileDecoratorNull(TileDecorator):
    def toDrawables(self, elements, tile=None, **kwargs):
        return ()

class TileDecoratorOffset(TileDecorator):
    def __init__(self, offset):
        super().__init__()
        self.offset = offset
    def toDrawables(self, elements, tile=None, **kwargs):
        if tile is None: return ()
        poly = tile.toPolygon()
        poly = poly.offsetPolygon(self.offset)
        ds = poly.toDrawables(elements, **kwargs)
        return ds

class TileDecoratorPolygons(TileDecorator):
    def __init__(self, *polys, polyDescs=[]):
        self.polyDescs = [p.makeRestorePoints() for p in polys]
        self.polyDescs.extend(polyDescs)
    def toDrawables(self, elements, tile=None, **kwargs):
        if tile is None:
            trans = Transform.identity()
        else:
            trans = tile.trans
        ds = []
        for polyDesc in self.polyDescs:
            d = self.descToDrawables(elements, polyDesc, trans, **kwargs)
            ds.extend(d)
        return ds
    def descToDrawables(self, elements, polyDesc, trans, **kwargs):
        polyDesc = trans.applyToList(polyDesc)
        poly = Polygon.fromRestorePoints(polyDesc)
        return poly.toDrawables(elements, **kwargs)

class TileDecoratorLateInit(TileDecorator):
    def __init__(self):
        self.delegate = None
        self.style = dict()
    def setup(self, delegate, **style):
        self.delegate = delegate
        self.style = style
    def toDrawables(self, elements, tile=None, **kwargs):
        if self.delegate is None:
            if tile is not None:
                dec = tile.decorator
                tile.decorator = None
                ds = tile.toDrawables(elements, **self.style, **kwargs)
                tile.decorator = dec
                return ds
        else:
            return self.delegate.toDrawables(elements, tile=tile,
                                             **self.style, **kwargs)

class TileDecoratorNumbered(TileDecorator):
    def __init__(self, size=0.1, trans=Transform.identity(), **style):
        self.index = 0
        self.size = size
        self.trans = trans
        self.style = style
    def toDrawables(self, elements, tile=None, layer=1, **kwargs):
        ds = []
        if layer == 0 and tile is not None:
            dec = tile.decorator
            tile.decorator = None
            ds = tile.toDrawables(elements, **kwargs)
            tile.decorator = dec
            return ds
        if layer == 1:
            pt = Point(0,0)
            trans = self.trans
            if tile is not None:
                trans = Transform.merge(trans, tile.trans)
            pt = trans.applyToPoint(pt)
            e1 = radialPoincareToEuclid(pt.hr - self.size/2)
            e2 = radialPoincareToEuclid(pt.hr + self.size/2)
            eSize = e2 - e1
            text = str(self.index)
            self.index += 1
            return (elements.Text(text, eSize, *pt, center=True,
                                  **self.style, **kwargs),)
        return ()

