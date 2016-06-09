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

    def move(self, direction):
        self.row += direction.delta_row
        self.col += direction.delta_col

    def rotate(self, ccw=False):
        d = -1 if ccw else 1
        self.rot = (self.rot + d) % len(self.shape.blocks)

    def pos(self):
        return self.row, self.col


class Block(object):
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color


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
            if self._block(b.row + 1, b.col):
                return True
        return False

    def land(self, piece):
        for b in piece.blocks():
            self.landed.append(b)

    def can_move(self, piece, direction):
        p = copy.deepcopy(piece)
        p.move(direction)
        return self._valid_pos(p)

    def can_rotate(self, piece, ccw=False):
        p = copy.deepcopy(piece)
        p.rotate(ccw)
        return self._valid_pos(p)

    def remove_lines(self):
        lines = 0
        row = self.rows - 1
        while row >= 0:
            found = True
            for col in xrange(0, self.cols):
                if not self._block(row, col):
                    found = False
                    break
            if found:
                lines += 1
                for col in xrange(0, self.cols):
                    self._remove_block(row, col)
                for col in xrange(0, self.cols):
                    for r in xrange(row - 1, -1, -1):
                        b = self._block(r, col)
                        if b:
                            b.row -= 1
                row += 1
            else:
                row -= 1
        return lines

    def _valid_pos(self, piece):
        for b in piece.blocks():
            if b.row < 0 \
                    or b.row >= self.rows \
                    or b.col < 0 \
                    or b.col >= self.cols \
                    or self._block(b.row, b.col):
                return False
        return True

    def _block(self, row, col):
        for b in self.landed:
            if b.row == row and b.col == col:
                return b

    def _remove_block(self, row, col):
        for i in xrange(len(self.landed)):
            b = self.landed[i]
            if b.row == row and b.col == col:
                self.landed.pop(i)
                break

class Game(object):
    def __init__(self, width, height, rows, cols):
        self.board = Board(rows, cols)
        self.size = width, height
        self.score = 0
        self.piece = None
        self._random_shapes = []

    def loop(self):
        pygame.init()
        pygame.display.set_caption('Tetris')
        screen = pygame.display.set_mode(self.size)
        clock = pygame.time.Clock()
        elapsed = [0]
        screen_width, screen_height = self.size
        block_size = screen_height / self.board.rows
        board_width = block_size * self.board.cols
        board_height = block_size * self.board.rows
        text_color = pygame.Color('green')
        font = pygame.font.SysFont('monospace', 12, bold=True)

        def draw_block(block):
            x = block.col * block_size
            y = block.row * block_size
            pygame.draw.rect(screen, block.color, (x, y, block_size, block_size))

        def draw_text(text, y):
            w, h = font.size(text)
            text_surface = font.render(text, 1, text_color)
            screen.blit(text_surface,
                        (board_width + (screen_width - board_width - w) / 2, y))

        def next_piece():
            if not self._random_shapes:
                self._random_shapes = [I, J, L, O, S, T, Z]
                random.shuffle(self._random_shapes)
            shape = self._random_shapes.pop(0)
            row = col = 0
            if shape in (I, O):
                col = self.board.cols / 2
            self.piece = Piece(shape, row, col)

        def move_piece(direction):
            if self.board.can_move(self.piece, direction):
                self.piece.move(direction)

        def drop_piece():
            while not self.board.has_landed(self.piece):
                move_piece(DOWN)

        def rotate_piece(ccw=False):
            if self.board.can_rotate(self.piece, ccw):
                self.piece.rotate(ccw)

        def process_input():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        move_piece(DOWN)
                    if event.key == pygame.K_LEFT:
                        move_piece(LEFT)
                    if event.key == pygame.K_RIGHT:
                        move_piece(RIGHT)
                    if event.key == pygame.K_x:
                        rotate_piece()
                    if event.key == pygame.K_z:
                        rotate_piece(True)
                    if event.key == pygame.K_SPACE:
                        drop_piece()

        def update_state():
            elapsed[0] += clock.get_time()
            if elapsed[0] >= 1000:
                if not self.board.has_landed(self.piece):
                    move_piece(DOWN)
                    elapsed[0] = 0
            if self.board.has_landed(self.piece):
                self.board.land(self.piece)
                next_piece()
            self.board.remove_lines()

        def render():
            screen.fill(self.board.background)
            pygame.draw.rect(screen, text_color, (0, 0, board_width, board_height), 1)
            for b in self.board.landed:
                draw_block(b)
            for b in self.piece.blocks():
                draw_block(b)
            draw_text('Next', block_size)
            draw_text('Score', block_size * 2)
            draw_text('%d' % self.score, block_size * 3)
            pygame.display.flip()
            clock.tick(60)

        next_piece()

        while True:
            process_input()
            update_state()
            render()


if __name__ == '__main__':
    game = Game(380, 480, 20, 10)
    game.loop()
