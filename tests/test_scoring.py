import unittest

from herbert.level import calculate_score


class ScoringTestCase(unittest.TestCase):
    def setUp(self):
        self.points = 1000
        self.max_bytes = 20
        self.total_buttons = 50

    def test_example1(self):
        buttons = 50
        bytes = 20

        self.assertEqual(calculate_score(self.points, self.max_bytes, self.total_buttons, buttons, bytes), 1000)

    def test_example2(self):
        buttons = 25
        bytes = 20

        self.assertEqual(calculate_score(self.points, self.max_bytes, self.total_buttons, buttons, bytes), 250)

    def test_example3(self):
        buttons = 50
        bytes = 30

        self.assertEqual(calculate_score(self.points, self.max_bytes, self.total_buttons, buttons, bytes), 250)

    def test_example4(self):
        buttons = 50
        bytes = 10

        self.assertEqual(calculate_score(self.points, self.max_bytes, self.total_buttons, buttons, bytes), 2000)
