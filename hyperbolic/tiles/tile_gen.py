from ..poincare import Transform
from . import Tile


class TileGen:
    def __init__(self, center_tile, corner_tile):
        self.center_tile = center_tile
        self.corner_tile = corner_tile
    @staticmethod
    def from_center_tile(center_tile):
        trans_to_origin = Transform.shift_origin(
                center_tile.vertices[0], center_tile.vertices[1])
        corner_tile = center_tile.make_transformed(trans_to_origin)
        return TileGen(center_tile, corner_tile)
    def centered_tile_with_transform(self, trans):
        return self.center_tile.make_transformed(trans)
    def tile_with_transform(self, trans):
        return self.corner_tile.make_transformed(trans)
    def centered_tile(self, rotate_deg=0):
        if rotate_deg != 0:
            trans = Transform.rotation(deg=rotate_deg)
            return self.centered_tile_with_transform(trans)
        else:
            return self.center_tile
    def corner_centered_tile(self, rotate_deg=0):
        if rotate_deg != 0:
            trans = Transform.rotation(deg=rotate_deg)
            return self.tile_with_transform(trans)
        else:
            return self.corner_tile
    def placed_against_tile(self, tile, side, touching_side=0):
        return self.placed_against_edge(
                tile.sides[side], touching_side=touching_side)
    def placed_against_edge(self, edge, touching_side=0):
        trans = Transform.translation(edge.p2, edge.p1)
        if touching_side != 0:
            trans_to_side = Transform.shift_origin(
                self.corner_tile.vertices[touching_side],
                self.corner_tile.vertices[
                    (touching_side+1)%len(self.corner_tile.vertices)])
            trans = Transform.merge(trans_to_side, trans)
        tile = self.tile_with_transform(trans)
        tile.touching_side = touching_side
        return tile
    def make_gen_with_permuted_edges(self, new_base_side_index):
        center_tile = self.center_tile.make_permuted(new_base_side_index)
        corner_tile = self.corner_tile.make_permuted(new_base_side_index)
        return TileGen(center_tile, corner_tile)
    @staticmethod
    def make_regular(p, q=None, inner_deg=None, er=None, hr=None, skip=1):
        center_tile = Tile.make_regular(
                p, q=q, inner_deg=inner_deg, er=er, hr=hr, skip=skip)
        return TileGen.from_center_tile(center_tile)
