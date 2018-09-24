import io
import unittest

from herbert.level import Level


class GoodLevelsTestCase(unittest.TestCase):
    def setUp(self):
        file = self.file = io.StringIO()
        file.write('.......\n')
        file.write('...w...\n')
        file.write('.......\n')
        file.write('...w...\n')
        file.write('.......\n')
        file.write('...g...\n')
        file.write('.......\n')
        file.write('...w...\n')
        file.write('.......\n')
        file.write('..*w*..\n')
        file.write('..*u*..\n')
        file.write('..***..\n')
        file.write('.......\n')
        file.write('1000\n')

    def tearDown(self):
        self.file.close()

    def test_when_file_ends_with_a_newline(self):
        self.file.write('10\n')
        self.file.seek(0)

        level = Level.fromfile(self.file, nrows=13, ncols=7)

        self.assertEqual(level.nrows, 13)
        self.assertEqual(level.ncols, 7)
        self.assertEqual(level.points, 1000)
        self.assertEqual(level.max_bytes, 10)
        self.assertEqual(level.robot, (10, 3, 'u'))

        self.assertEqual(len(level.gray_buttons), 1)
        self.assertTrue((5, 3) in level.gray_buttons)

        self.assertEqual(len(level.white_buttons), 4)
        self.assertTrue((1, 3) in level.white_buttons)
        self.assertTrue((3, 3) in level.white_buttons)
        self.assertTrue((7, 3) in level.white_buttons)
        self.assertTrue((9, 3) in level.white_buttons)

        self.assertEqual(len(level.walls), 3)

        self.assertEqual(len(level.inaccessible_spots), 7)
        self.assertTrue((9, 2) in level.inaccessible_spots)
        self.assertTrue((9, 4) in level.inaccessible_spots)
        self.assertTrue((10, 2) in level.inaccessible_spots)
        self.assertTrue((10, 4) in level.inaccessible_spots)
        self.assertTrue((11, 2) in level.inaccessible_spots)
        self.assertTrue((11, 3) in level.inaccessible_spots)
        self.assertTrue((11, 4) in level.inaccessible_spots)

    def test_when_file_does_not_end_with_a_newline(self):
        self.file.write('10')
        self.file.seek(0)

        level = Level.fromfile(self.file, nrows=13, ncols=7)

        self.assertEqual(level.points, 1000)
        self.assertEqual(level.max_bytes, 10)


class BadLevelsTestCase(unittest.TestCase):
    def setUp(self):
        self.file = io.StringIO()

    def tearDown(self):
        self.file.close()

    def test_when_nrows_non_positive(self):
        with self.assertRaisesRegex(ValueError, 'rows .* greater than or equal to 1'):
            Level.fromfile(self.file, nrows=0)

    def test_when_ncols_non_positive(self):
        with self.assertRaisesRegex(ValueError, 'columns .* greater than or equal to 1'):
            Level.fromfile(self.file, ncols=0)

    def test_when_less_lines(self):
        self.file.write('.\n.\n')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'expected 3 lines but got 2'):
            Level.fromfile(self.file, nrows=3, ncols=1)

    def test_when_empty_line(self):
        self.file.write('.\n\n.')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'line 2 is an empty line'):
            Level.fromfile(self.file, nrows=3, ncols=1)

    def test_when_illegal_character(self):
        self.file.write('.\n.\nS')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'illegal character found at line 3'):
            Level.fromfile(self.file, nrows=3, ncols=1)

    def test_when_line_too_short(self):
        self.file.write('.\n..')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'line 1 is not 2 characters long'):
            Level.fromfile(self.file, nrows=2, ncols=2)

    def test_when_line_too_long(self):
        self.file.write('.\n..\n.')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'line 2 is not 1 character long'):
            Level.fromfile(self.file, nrows=3, ncols=1)

    def test_when_points_non_positive(self):
        self.file.write('.\n0\n1')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'expected a positive integer .* at line 2: 0'):
            Level.fromfile(self.file, nrows=1, ncols=1)

    def test_when_points_too_large(self):
        self.file.write('.\n1000000\n1')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'expected a positive integer in the range \[1, 1000000\) at line 2: 1000000'):
            Level.fromfile(self.file, nrows=1, ncols=1)

    def test_when_points_not_a_number(self):
        self.file.write('.\na\n1')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'expected a positive integer .* at line 2: a'):
            Level.fromfile(self.file, nrows=1, ncols=1)

    def test_when_max_bytes_non_positive(self):
        self.file.write('.\n1\n0')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'expected a positive integer .* at line 3: 0'):
            Level.fromfile(self.file, nrows=1, ncols=1)

    def test_when_max_bytes_too_large(self):
        self.file.write('.\n1\n1000')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'expected a positive integer in the range \[1, 1000\) at line 3: 1000'):
            Level.fromfile(self.file, nrows=1, ncols=1)

    def test_when_max_bytes_not_a_number(self):
        self.file.write('.\n1\na')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'expected a positive integer .* at line 3: a'):
            Level.fromfile(self.file, nrows=1, ncols=1)

    def test_when_too_many_robots(self):
        self.file.write('.u.\n..d\n1\n1')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'too many robots, .* \(2, 3\)'):
            Level.fromfile(self.file, nrows=2, ncols=3)

    def test_when_improper_wall(self):
        self.file.write('..**.*.\n1\n1')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'improper wall at \(1, 6\)'):
            Level.fromfile(self.file, nrows=1, ncols=7)

    def test_when_no_robot(self):
        self.file.write('..****.\n1\n1')
        self.file.seek(0)

        with self.assertRaisesRegex(ValueError, 'no robot found'):
            Level.fromfile(self.file, nrows=1, ncols=7)
