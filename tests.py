import unittest
import tetris


class PieceTest(unittest.TestCase):
    def test_blocks(self):
        for s in tetris.SHAPES:
            p = tetris.Piece(s)
            self.assertTrue(p.blocks())

    def test_move(self):
        test_data = ((tetris.RIGHT, (1, 1), (1, 2)),
                     (tetris.LEFT, (1, 1), (1, 0)),
                     (tetris.DOWN, (1, 1), (2, 1)))
        for s in tetris.SHAPES:
            for t in test_data:
                direction, position, expected_position = t
                p = tetris.Piece(s, *position)
                p.move(direction)
                self.assertEqual(expected_position, p.position(), "failed for {}".format(s))

    def test_rotate_should_change_blocks_except_for_O(self):
        for s in tetris.SHAPES:
            p = tetris.Piece(s)
            initial_blocks = p.blocks()
            p.rotate()
            rotated_blocks = p.blocks()
            if s != tetris.O:
                self.assertNotEqual(initial_blocks, rotated_blocks, "failed for {}".format(s))
            else:
                self.assertEqual(initial_blocks, rotated_blocks, "failed for O")

    def test_rotate_and_back_should_not_change_blocks(self):
        for s in tetris.SHAPES:
            p = tetris.Piece(s)
            initial_blocks = p.blocks()
            p.rotate()
            p.rotate(ccw=True)
            rotated_blocks = p.blocks()
            self.assertEqual(initial_blocks, rotated_blocks, "failed for {}".format(s))


if __name__ == '__main__':
    unittest.main()
