class TileLayout:
    '''
    Override this class and implement the calc* methods to create a custom
    layout.
    '''
    def __init__(self, gen_list=None):
        self.gen_list = [] if gen_list is None else gen_list
    def add_generator(self, tile_gen, side_codes, decorator=None):
        self.gen_list.append([tile_gen, side_codes, decorator])
    def set_decorator(self, decorator, gen_index):
        self.gen_list[gen_index][2] = decorator
    def tile_plane(self, start_tile, depth=2):
        tiles = [start_tile]
        boundary = list(start_tile.sides)
        for j in range(depth):
            boundary2 = []
            i = 0
            while i < len(boundary):
                tile = self.place_tile(boundary[i])
                tiles.append(tile)
                sides = tile.permuted_sides()
                o = 1
                p = len(sides)
                if i == 0:
                    if sides[o] == boundary[-1]:
                        o += 1
                        boundary.pop()
                else:
                    if sides[o] == boundary2[-1]:
                        o += 1
                        boundary2.pop()
                    if sides[p-1] == boundary[(i + 1) % len(boundary)]:
                        p -= 1
                        i += 1
                    if sides[p-1] == boundary2[0]:
                        p -= 1
                        boundary2.pop(0)
                boundary2.extend(sides[o:p])
                i += 1
            boundary = boundary2
        return tiles
    def place_tile(self, edge):
        '''Return a tile placed against edge according to the placement rules.
        '''
        code = edge.code
        gen_index = self.calc_gen_index(code)
        tile_gen, default_codes, decorator = self.gen_list[gen_index][0:3]
        touch_side_index = self.calc_tile_touch_side(code, gen_index)
        side_codes = self.calc_side_codes(
                code, gen_index, touch_side_index, default_codes)
        tile = tile_gen.placed_against_edge(
                edge, touching_side=touch_side_index)
        tile.set_side_codes(side_codes)
        tile.decorator = decorator
        return tile
    def start_tile(self, code=0, gen_index=None, side_codes=None, rotate_deg=0,
                   center_corner=False):
        if gen_index is None:
            gen_index = self.calc_gen_index(code)
        tile_gen, default_codes, decorator = self.gen_list[gen_index][0:3]
        if side_codes is None:
            touch_side_index = self.calc_tile_touch_side(code, gen_index)
            side_codes = self.calc_side_codes(
                    code, gen_index, touch_side_index, default_codes)
        if center_corner:
            tile = tile_gen.corner_centered_tile(rotate_deg=rotate_deg)
        else:
            tile = tile_gen.centered_tile(rotate_deg=rotate_deg)
        tile.set_side_codes(side_codes)
        tile.decorator = decorator
        return tile
    def default_start_tile(self, rotate_deg=0, center_corner=False):
        return self.start_tile(
                rotate_deg=rotate_deg, center_corner=center_corner)
    def calc_gen_index(self, code):
        '''
        Override in subclass to control which type of tile to place.
        '''
        return code
    def calc_tile_touch_side(self, code, gen_index):
        '''
        Override in subclass to control tile orientation.
        '''
        return 0
    def calc_side_codes(self, code, gen_index, touch_side, default_codes):
        '''
        Override in subclass to control tile side codes.
        '''
        return default_codes
