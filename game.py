import random
import sys

import pygame

import board


class State(object):
    def __init__(self, rows, cols):
        self.board = board.Board(rows, cols)
        self.score = 0
        self.piece = None
        self.shapes = []
        self.elapsed = 0
        self.level = -1
        self.speed = 0
        self.paused = False
        self.game_over = False
        self.next_level()
        self.next_piece()

    def next_piece(self):
        shape = self.next_shape()
        self.shapes.remove(shape)
        row = col = 0
        if shape in (board.SHAPE_I, board.SHAPE_O):
            col = self.board.cols / 2
        self.piece = board.Piece(shape, row, col)

    def next_shape(self):
        if not self.shapes:
            self.shapes = list(board.ALL_SHAPES)
            random.shuffle(self.shapes)
        return self.shapes[0]

    def move_piece(self, direction):
        if self.board.can_move(self.piece, direction):
            self.piece.move(direction)

    def drop_piece(self):
        while not self.board.has_landed(self.piece):
            self.move_piece(board.DIRECTION_DOWN)

    def rotate_piece(self, ccw=False):
        if self.board.can_rotate(self.piece, ccw):
            self.piece.rotate(ccw)

    def update(self, dt):
        if self.game_over or self.paused:
            return
        self.elapsed += dt
        if self.elapsed >= self.speed:
            if not self.board.has_landed(self.piece):
                self.move_piece(board.DIRECTION_DOWN)
                self.elapsed = 0
        if self.board.has_landed(self.piece):
            self.board.land(self.piece)
            self.next_piece()
        lines = self.board.remove_lines()
        if lines:
            self.update_score(lines)
            if self.score % 1000 == 0 and self.level < 9:
                self.next_level()
        for c in range(self.board.cols):
            if self.board.block_at(0, c):
                self.game_over = True

    POINTS_PER_LINES = {1: 40, 2: 100, 3: 300, 4: 1200}

    def update_score(self, lines):
        self.score += self.POINTS_PER_LINES.get(lines) * (self.level + 1)

    def next_level(self):
        self.level += 1
        self.speed = 1000 - self.level * 100

    @property
    def running(self):
        return not (self.paused or self.game_over)


class Game(object):
    ROWS = 20
    COLS = 10

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = State(self.ROWS, self.COLS)
        self.block_size = height / self.state.board.rows
        self.board_width = self.block_size * self.state.board.cols
        self.board_height = self.block_size * self.state.board.rows
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 16)
        self.font.set_bold(True)
        self.text_color = pygame.Color('yellow')
        self.background_color = pygame.Color('black')

    def draw_block(self, block):
        x = block.col * self.block_size
        y = block.row * self.block_size
        pygame.draw.rect(self.screen, block.color,
                         (x, y, self.block_size, self.block_size))

    def draw_text(self, text, y):
        w, h = self.font.size(text)
        x = self.board_width + (self.width - self.board_width - w) / 2
        text_surface = self.font.render(text, 1, self.text_color)
        self.screen.blit(text_surface, (x, y))

    def draw_piece(self, piece):
        for b in piece.blocks():
            self.draw_block(b)

    def draw_next_piece(self, y):
        x = self.board_width + \
            (self.width - self.board_width - self.block_size) / 2
        row = y / self.block_size
        col = x / self.block_size - 1
        piece = board.Piece(self.state.next_shape(), row, col)
        pygame.draw.rect(self.screen, piece.shape.color,
                         (x - self.block_size * 2, y - self.block_size / 2,
                          self.block_size * 5, self.block_size * 4), 1)
        self.draw_piece(piece)

    def draw_background(self):
        self.screen.fill(self.background_color)
        pygame.draw.rect(self.screen, self.text_color,
                         (0, 0, self.board_width, self.board_height), 1)
        for b in self.state.board.landed:
            self.draw_block(b)

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state.paused:
                    if event.key == pygame.K_r:
                        self.state.paused = False
                if self.state.game_over:
                    if event.key == pygame.K_r:
                        self.state = State(self.ROWS, self.COLS)
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                if self.state.running:
                    if event.key == pygame.K_DOWN:
                        self.state.move_piece(board.DIRECTION_DOWN)
                    if event.key == pygame.K_LEFT:
                        self.state.move_piece(board.DIRECTION_LEFT)
                    if event.key == pygame.K_RIGHT:
                        self.state.move_piece(board.DIRECTION_RIGHT)
                    if event.key == pygame.K_x:
                        self.state.rotate_piece()
                    if event.key == pygame.K_z:
                        self.state.rotate_piece(True)
                    if event.key == pygame.K_SPACE:
                        self.state.drop_piece()
                    if event.key == pygame.K_p:
                        self.state.paused = True

    def update_state(self):
        if self.state.running:
            self.state.update(self.clock.get_time())

    def render(self):
        self.draw_background()
        self.draw_piece(self.state.piece)
        self.draw_text('Level', self.block_size)
        self.draw_text('%d' % (self.state.level + 1), self.block_size * 2)
        self.draw_text('Score', self.block_size * 3)
        self.draw_text('%d' % self.state.score, self.block_size * 4)
        self.draw_text('Next', self.block_size * 5)
        self.draw_next_piece(self.block_size * 6)
        if self.state.paused:
            self.draw_text('Game paused', self.block_size * 10)
            self.draw_text('Press R to resume', self.block_size * 11)
        if self.state.game_over:
            self.draw_text('Game over', self.block_size * 10)
            self.draw_text('Press R to restart', self.block_size * 11)
        pygame.display.flip()
        self.clock.tick(60)

    def loop(self):
        while True:
            self.process_input()
            self.update_state()
            self.render()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('PyTetris')
    game = Game(380, 480)
    game.loop()
