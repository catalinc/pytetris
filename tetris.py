import sys
import collections
import random
import copy
import pygame

Shape = collections.namedtuple('Shape', ['blocks', 'color'])
I = Shape(blocks=(0x0F00, 0x2222, 0x00F0, 0x4444), color=pygame.Color('cyan'))
J = Shape(blocks=(0x44C0, 0x8E00, 0x6440, 0x0E20), color=pygame.Color('blue'))
L = Shape(blocks=(0x4460, 0x0E80, 0xC440, 0x2E00), color=pygame.Color('orange'))
O = Shape(blocks=(0xCC00, 0xCC00, 0xCC00, 0xCC00), color=pygame.Color('yellow'))
S = Shape(blocks=(0x06C0, 0x8C40, 0x6C00, 0x4620), color=pygame.Color('green'))
T = Shape(blocks=(0x0E40, 0x4C40, 0x4E00, 0x4640), color=pygame.Color('purple'))
Z = Shape(blocks=(0x0C60, 0x4C80, 0xC600, 0x2640), color=pygame.Color('red'))
SHAPES = (I, J, L, O, S, T, Z)

Direction = collections.namedtuple('Direction', ['delta_row', 'delta_col'])
DOWN = Direction(delta_row=1, delta_col=0)
LEFT = Direction(delta_row=0, delta_col=-1)
RIGHT = Direction(delta_row=0, delta_col=1)
DIRECTIONS = (DOWN, LEFT, RIGHT)


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
        self.background = pygame.Color('black')

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
                    self.remove_block(row, col)
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

    def remove_block(self, row, col):
        for i in xrange(len(self.landed)):
            b = self.landed[i]
            if b.row == row and b.col == col:
                self.landed.pop(i)
                break


class GameState(object):
    def __init__(self, rows, cols):
        self.board = Board(rows, cols)
        self.score = 0
        self.piece = None
        self.next_shapes = []
        self.elapsed = 0
        self.next_piece()

    def next_piece(self):
        if not self.next_shapes:
            self.next_shapes = [I, J, L, O, S, T, Z]
            random.shuffle(self.next_shapes)
        shape = self.next_shapes.pop(0)
        row = col = 0
        if shape in (I, O):
            col = self.board.cols / 2
        self.piece = Piece(shape, row, col)

    def move_piece(self, direction):
        if self.board.can_move(self.piece, direction):
            self.piece.move(direction)

    def drop_piece(self):
        while not self.board.has_landed(self.piece):
            self.move_piece(DOWN)

    def rotate_piece(self, ccw=False):
        if self.board.can_rotate(self.piece, ccw):
            self.piece.rotate(ccw)

    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= 1000:
            if not self.board.has_landed(self.piece):
                self.move_piece(DOWN)
                self.elapsed = 0
        if self.board.has_landed(self.piece):
            self.board.land(self.piece)
            self.next_piece()
        self.board.remove_lines()


class Game(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = GameState(20, 10)
        self.block_size = height / self.state.board.rows
        self.board_width = self.block_size * self.state.board.cols
        self.board_height = self.block_size * self.state.board.rows
        pygame.init()
        pygame.display.set_caption('Tetris')
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('monospace', 12, bold=True)
        self.text_color = pygame.Color('green')
        self.background_color = pygame.Color('black')

    def draw_block(self, block):
        x = block.col * self.block_size
        y = block.row * self.block_size
        pygame.draw.rect(self.screen, block.color, (x, y, self.block_size, self.block_size))

    def draw_text(self, text, y):
        w, h = self.font.size(text)
        text_surface = self.font.render(text, 1, self.text_color)
        self.screen.blit(text_surface,
                         (self.board_width + (self.width - self.board_width - w) / 2, y))

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.state.move_piece(DOWN)
                if event.key == pygame.K_LEFT:
                    self.state.move_piece(LEFT)
                if event.key == pygame.K_RIGHT:
                    self.state.move_piece(RIGHT)
                if event.key == pygame.K_x:
                    self.state.rotate_piece()
                if event.key == pygame.K_z:
                    self.state.rotate_piece(True)
                if event.key == pygame.K_SPACE:
                    self.state.drop_piece()

    def update_state(self):
        self.state.update(self.clock.get_time())

    def render(self):
        self.screen.fill(self.background_color)
        pygame.draw.rect(self.screen, self.text_color, (0, 0, self.board_width, self.board_height), 1)
        for b in self.state.board.landed:
            self.draw_block(b)
        for b in self.state.piece.blocks():
            self.draw_block(b)
        self.draw_text('Next', self.block_size)
        self.draw_text('Score', self.block_size * 2)
        self.draw_text('%d' % self.state.score, self.block_size * 3)
        pygame.display.flip()
        self.clock.tick(60)

    def loop(self):
        while True:
            self.process_input()
            self.update_state()
            self.render()


if __name__ == '__main__':
    game = Game(380, 480)
    game.loop()
