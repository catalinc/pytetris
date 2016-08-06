import unittest

import board


class PieceTest(unittest.TestCase):
    def test_blocks(self):
        for s in board.ALL_SHAPES:
            p = board.Piece(s)
            self.assertTrue(p.blocks())

    def test_move(self):
        test_data = ((board.DIRECTION_RIGHT, (1, 1), (1, 2)),
                     (board.DIRECTION_LEFT, (1, 1), (1, 0)),
                     (board.DIRECTION_DOWN, (1, 1), (2, 1)))
        for s in board.ALL_SHAPES:
            for t in test_data:
                direction, position, expected_position = t
                p = board.Piece(s, *position)
                p.move(direction)
                self.assertEqual(expected_position, p.position(), "failed for {}".format(s))

    def test_rotate_should_change_blocks_except_for_O(self):
        for s in board.ALL_SHAPES:
            p = board.Piece(s)
            initial_blocks = p.blocks()
            p.rotate()
            rotated_blocks = p.blocks()
            if s != board.SHAPE_O:
                self.assertNotEqual(initial_blocks, rotated_blocks, "failed for {}".format(s))
            else:
                self.assertEqual(initial_blocks, rotated_blocks, "failed for O")

    def test_rotate_and_back_should_not_change_blocks(self):
        for s in board.ALL_SHAPES:
            p = board.Piece(s)
            initial_blocks = p.blocks()
            p.rotate()
            p.rotate(ccw=True)
            rotated_blocks = p.blocks()
            self.assertEqual(initial_blocks, rotated_blocks, "failed for {}".format(s))


if __name__ == '__main__':
    unittest.main()
