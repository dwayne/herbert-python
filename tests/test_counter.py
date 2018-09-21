import unittest

from herbert.counter import count_bytes
from herbert.parser import parse


def count(program):
    return count_bytes(parse(program))


class CountBytesTestCase(unittest.TestCase):
    def test_example1(self):
        program = 'slr'

        self.assertEqual(count(program), 3)

    def test_example2(self):
        program = 'a:sa\na'

        self.assertEqual(count(program), 4)

    def test_example3(self):
        program = 'a(A):sa(A-1)\na(4)'

        self.assertEqual(count(program), 8)

    def test_example4(self):
        program = 'a(A,B,C):f(B)Ca(A-1,B,C)\nf(A):sf(A-1)\na(4,5,rslsr)'

        self.assertEqual(count(program), 26)

    def test_example5(self):
        program = 'f(A,B,C,D,E,F):sAf(AA,B,F-C+D+2,-D+1,E-1,sFl)\nf(sl,5,-1,100,10,r)'

        self.assertEqual(count(program), 32)
