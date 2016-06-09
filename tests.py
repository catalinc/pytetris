import unittest
import tetris


class PieceTest(unittest.TestCase):
    def test_has_blocks_for_all_shapes(self):
        for s in tetris.SHAPES:
            p = tetris.Piece(s)
            self.assertTrue(p.blocks())

    def test_move(self):
        test_data = ((tetris.RIGHT, (1, 1), (1, 2)),
                     (tetris.LEFT, (1, 1), (1, 0)),
                     (tetris.DOWN, (1, 1), (2, 1)))
        for t in test_data:
            p = tetris.Piece(tetris.I, *t[1])
            p.move(t[0])
            self.assertEqual(t[2], p.pos())

    def test_rotate(self):
        pass


if __name__ == '__main__':
    unittest.main()
