import collections
import copy

import pygame

Shape = collections.namedtuple('Shape', ['blocks', 'color'])
SHAPE_I = Shape(blocks=(0x0F00, 0x2222, 0x00F0, 0x4444), color=pygame.Color('cyan'))
SHAPE_J = Shape(blocks=(0x44C0, 0x8E00, 0x6440, 0x0E20), color=pygame.Color('blue'))
SHAPE_L = Shape(blocks=(0x4460, 0x0E80, 0xC440, 0x2E00), color=pygame.Color('orange'))
SHAPE_O = Shape(blocks=(0xCC00, 0xCC00, 0xCC00, 0xCC00), color=pygame.Color('yellow'))
SHAPE_S = Shape(blocks=(0x06C0, 0x8C40, 0x6C00, 0x4620), color=pygame.Color('green'))
SHAPE_T = Shape(blocks=(0x0E40, 0x4C40, 0x4E00, 0x4640), color=pygame.Color('purple'))
SHAPE_Z = Shape(blocks=(0x0C60, 0x4C80, 0xC600, 0x2640), color=pygame.Color('red'))
ALL_SHAPES = (SHAPE_I, SHAPE_J, SHAPE_L, SHAPE_O, SHAPE_S, SHAPE_T, SHAPE_Z)

Direction = collections.namedtuple('Direction', ['delta_row', 'delta_col'])
DIRECTION_DOWN = Direction(delta_row=1, delta_col=0)
DIRECTION_LEFT = Direction(delta_row=0, delta_col=-1)
DIRECTION_RIGHT = Direction(delta_row=0, delta_col=1)
ALL_DIRECTIONS = (DIRECTION_DOWN, DIRECTION_LEFT, DIRECTION_RIGHT)


class Piece(object):
    def __init__(self, shape, row=0, col=0, rot=0):
        self.shape = shape
        self.row = row
        self.col = col
        self.rot = rot

    def blocks(self):
        blocks = []
        b, r, c = 0x8000, 0, 0
        while b > 0:
            if self.shape.blocks[self.rot] & b:
                blocks.append(Block(self.row + r, self.col + c, self.shape.color))
            if c == 3:
                c = 0
                r += 1
            else:
                c += 1
            b >>= 1
        return blocks

    def position(self):
        return self.row, self.col

    def move(self, direction):
        self.row += direction.delta_row
        self.col += direction.delta_col

    def rotate(self, ccw=False):
        d = -1 if ccw else 1
        self.rot = (self.rot + d) % len(self.shape.blocks)


class Block(object):
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __str__(self):
        return '({}, {})'.format(self.row, self.col)


class Board(object):
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.landed = []

    def has_landed(self, piece):
        for b in piece.blocks():
            if b.row == self.rows - 1:
                return True
            if self.block_at(b.row + 1, b.col):
                return True
        return False

    def land(self, piece):
        for b in piece.blocks():
            self.landed.append(b)

    def can_move(self, piece, direction):
        p = copy.deepcopy(piece)
        p.move(direction)
        return self.has_valid_position(p)

    def can_rotate(self, piece, ccw=False):
        p = copy.deepcopy(piece)
        p.rotate(ccw)
        return self.has_valid_position(p)

    def remove_lines(self):
        lines = 0
        row = self.rows - 1
        while row >= 0:
            found = True
            for col in xrange(0, self.cols):
                if not self.block_at(row, col):
                    found = False
                    break
            if found:
                lines += 1
                for col in xrange(0, self.cols):
                    self.del_block_at(row, col)
                for col in xrange(0, self.cols):
                    for r in xrange(row - 1, -1, -1):
                        b = self.block_at(r, col)
                        if b:
                            b.row += 1
                row += 1
            else:
                row -= 1
        return lines

    def has_valid_position(self, piece):
        for b in piece.blocks():
            if b.row < 0 \
                    or b.row >= self.rows \
                    or b.col < 0 \
                    or b.col >= self.cols \
                    or self.block_at(b.row, b.col):
                return False
        return True

    def block_at(self, row, col):
        for b in self.landed:
            if b.row == row and b.col == col:
                return b

    def del_block_at(self, row, col):
        for i in xrange(len(self.landed)):
            b = self.landed[i]
            if b.row == row and b.col == col:
                self.landed.pop(i)
                break
