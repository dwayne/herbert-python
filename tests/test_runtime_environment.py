import io
import unittest

from herbert.level import Level


class StepTestCase(unittest.TestCase):
    def setUp(self):
        file = self.file = io.StringIO()
        file.write('..........\n')
        file.write('.***......\n')
        file.write('.*r.w.g.w.\n')
        file.write('.***......\n')
        file.write('..........\n')
        file.write('50\n')
        file.write('11')
        file.seek(0)

        level = Level.fromfile(file, nrows=5, ncols=10)

        # N.B. The sequence of commands "sslsrssssrs"
        # can be used to complete the level.
        self.re = level()

    def tearDown(self):
        self.file.close()

    def test_lss(self):
        self.re.step('l')
        self.re.step('s')
        self.re.step('s')

        self.assertEqual(self.re.robot.row, 2)
        self.assertEqual(self.re.robot.col, 2)
        self.assertTrue(self.re.robot.isup())
        self.assertEqual(self.re.npressed, 0)
        self.assertFalse(self.re.white_buttons[(2, 4)].pressed)
        self.assertFalse(self.re.white_buttons[(2, 8)].pressed)
        self.assertEqual(self.re.max_npressed, 0)
        self.assertFalse(self.re.completed)

    def test_ss(self):
        self.re.step('s')
        self.re.step('s')

        self.assertEqual(self.re.robot.row, 2)
        self.assertEqual(self.re.robot.col, 4)
        self.assertTrue(self.re.robot.isright())
        self.assertEqual(self.re.npressed, 1)
        self.assertTrue(self.re.white_buttons[(2, 4)].pressed)
        self.assertFalse(self.re.white_buttons[(2, 8)].pressed)
        self.assertEqual(self.re.max_npressed, 1)
        self.assertFalse(self.re.completed)

    def test_sslsss(self):
        self.re.step('s')
        self.re.step('s')
        self.re.step('l')
        self.re.step('s')
        self.re.step('s')
        self.re.step('s')

        self.assertEqual(self.re.robot.row, 0)
        self.assertEqual(self.re.robot.col, 4)
        self.assertTrue(self.re.robot.isup())
        self.assertEqual(self.re.npressed, 1)
        self.assertTrue(self.re.white_buttons[(2, 4)].pressed)
        self.assertFalse(self.re.white_buttons[(2, 8)].pressed)
        self.assertEqual(self.re.max_npressed, 1)
        self.assertFalse(self.re.completed)

    def test_ssssss(self):
        self.re.step('s')
        self.re.step('s')
        self.re.step('s')
        self.re.step('s')
        self.re.step('s')
        self.re.step('s')

        self.assertEqual(self.re.robot.row, 2)
        self.assertEqual(self.re.robot.col, 8)
        self.assertTrue(self.re.robot.isright())
        self.assertEqual(self.re.npressed, 1)
        self.assertFalse(self.re.white_buttons[(2, 4)].pressed)
        self.assertTrue(self.re.white_buttons[(2, 8)].pressed)
        self.assertEqual(self.re.max_npressed, 1)
        self.assertFalse(self.re.completed)

    def test_sslsrssssrs(self):
        self.re.step('s')
        self.re.step('s')
        self.re.step('l')
        self.re.step('s')
        self.re.step('r')
        self.re.step('s')
        self.re.step('s')
        self.re.step('s')
        self.re.step('s')
        self.re.step('r')
        self.re.step('s')

        self.assertEqual(self.re.robot.row, 2)
        self.assertEqual(self.re.robot.col, 8)
        self.assertTrue(self.re.robot.isdown())
        self.assertEqual(self.re.npressed, 2)
        self.assertTrue(self.re.white_buttons[(2, 4)].pressed)
        self.assertTrue(self.re.white_buttons[(2, 8)].pressed)
        self.assertEqual(self.re.max_npressed, 2)
        self.assertTrue(self.re.completed)

    def test_sslsrssssrsrss(self):
        self.re.step('s')
        self.re.step('s')
        self.re.step('l')
        self.re.step('s')
        self.re.step('r')
        self.re.step('s')
        self.re.step('s')
        self.re.step('s')
        self.re.step('s')
        self.re.step('r')
        self.re.step('s')
        self.re.step('r')
        self.re.step('s')
        self.re.step('s')

        self.assertEqual(self.re.robot.row, 2)
        self.assertEqual(self.re.robot.col, 6)
        self.assertTrue(self.re.robot.isleft())
        self.assertEqual(self.re.npressed, 0)
        self.assertFalse(self.re.white_buttons[(2, 4)].pressed)
        self.assertFalse(self.re.white_buttons[(2, 8)].pressed)
        self.assertEqual(self.re.max_npressed, 2)
        self.assertTrue(self.re.completed)


class ScoreTestCase(unittest.TestCase):
    def test_example1(self):
        file = io.StringIO()
        file.write('.r.wwwwwwwwwwwwwwwwwwww.\n')
        file.write('100\n')
        file.write('10\n')
        file.seek(0)

        level = Level.fromfile(file, nrows=1, ncols=24)
        re = level()

        for _ in range(25):
            re.step('s')

        # points = 100
        # max_bytes = 10
        # total_buttons = 20
        # buttons = 20

        # bytes = 10
        self.assertEqual(re.score(10), 100)

        # bytes = 5
        self.assertEqual(re.score(5), 200)

        # bytes = 15
        self.assertEqual(re.score(15), 20)

        file.close()
