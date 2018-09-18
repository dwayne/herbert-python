import itertools
import unittest

from herbert.error import LookupError, TypeError
from herbert.interpreter import interp
from herbert.parser import parse


def run(program, upper_bound=None):
    commands = interp(parse(program))

    if upper_bound:
        commands = itertools.islice(commands, upper_bound)

    return ''.join(commands)


class ExamplesTestCase(unittest.TestCase):
    def test_example1(self):
        program = 'sssssrsssssrsssssrsssssr'

        self.assertEqual(run(program), 'sssssrsssssrsssssrsssssr')

    def test_example2(self):
        program = 'a:sssssr\naaaa'

        self.assertEqual(run(program), 'sssssrsssssrsssssrsssssr')

    def test_example3(self):
        program = 'a:sssssra\na'

        self.assertEqual(run(program, 24), 'sssssrsssssrsssssrsssssr')

    def test_example4(self):
        program = 'a(A):sssssra(A-1)\na(4)'

        self.assertEqual(run(program), 'sssssrsssssrsssssrsssssr')

    def test_example5(self):
        program = 'a(A,B):f(B)ra(A-1,B)\nf(A):sf(A-1)\na(4,5)'

        self.assertEqual(run(program), 'sssssrsssssrsssssrsssssr')

    def test_example6(self):
        program = 'a(A,B,C):f(B)Ca(A-1,B,C)\nf(A):sf(A-1)\na(4,5,r)'

        self.assertEqual(run(program), 'sssssrsssssrsssssrsssssr')

    def test_example7(self):
        program = 'a(A):ArAa(AA)\na(s)'

        self.assertEqual(run(program, 17), 'srsssrssssssrssss')

    def test_example8(self):
        program = 'a(A,B,C):f(B)Ca(A-1,B,C)\nb(A):a(4,5,r)lb(A-1)\nf(A):sf(A-1)\nb(4)'

        self.assertEqual(
            run(program, 100),
            'sssssrsssssrsssssrsssssrl'
            'sssssrsssssrsssssrsssssrl'
            'sssssrsssssrsssssrsssssrl'
            'sssssrsssssrsssssrsssssrl'
        )

    def test_example9(self):
        program = 'a(A,B,C):f(B)Ca(A-1,B,C)\nb(A):a(4,A,r)b(A-1)\nf(A):sf(A-1)\nb(10)'

        self.assertEqual(
            run(program, 260),
            'ssssssssssrssssssssssrssssssssssrssssssssssr'  # 40 + 4 = 44
            'sssssssssrsssssssssrsssssssssrsssssssssr'      # 40
            'ssssssssrssssssssrssssssssrssssssssr'          # 36
            'sssssssrsssssssrsssssssrsssssssr'              # 32
            'ssssssrssssssrssssssrssssssr'                  # 28
            'sssssrsssssrsssssrsssssr'                      # 24
            'ssssrssssrssssrssssr'                          # 20
            'sssrsssrsssrsssr'                              # 16
            'ssrssrssrssr'                                  # 12
            'srsrsrsr'                                      # 8
        )

    def test_example10(self):
        program = 'a(A,B,C):f(B)Ca(A-1,B,C)\nb(A):a(2,11-A,r)b(A-1)\nf(A):sf(A-1)\nb(10)'

        self.assertEqual(
            run(program, 130),
            'srsr'                   # 4
            'ssrssr'                 # 6
            'sssrsssr'               # 8
            'ssssrssssr'             # 10
            'sssssrsssssr'           # 12
            'ssssssrssssssr'         # 14
            'sssssssrsssssssr'       # 16
            'ssssssssrssssssssr'     # 18
            'sssssssssrsssssssssr'   # 20
            'ssssssssssrssssssssssr' # 22
        )

    def test_example11(self):
        program = 'a(A,B,C):f(B)Ca(A-1,B,C)\nf(A):sf(A-1)\na(4,5,rslsr)'

        self.assertEqual(run(program, 40), 'sssssrslsrsssssrslsrsssssrslsrsssssrslsr')


class InfiniteRecursionTestCase(unittest.TestCase):
    """These test cases illustrate that some programs that should be able to run
    infinitely long aren't able to do so and cause the Python runtime to raise
    a RecursionError exception. This points to a need to improve my
    implementation of the interpreter.

    Would tail-call optimization help?

    Notice how the program in test_example3 has the same runtime effect as that
    of the program in test_example1 but the one in test_example1 raises a
    RecursionError.
    """
    def test_example1(self):
        program = 'a:sa\na'

        with self.assertRaises(RecursionError):
            run(program, 10000)

    def test_example2(self):
        program = 'a(A):ArAa(AA)\na(s)'

        run(program, 10000)

    def test_example3(self):
        program = 'a(A):Aa(AA)\na(s)'

        run(program, 10000)


class RuntimeErrorTestCase(unittest.TestCase):
    def test_missing_procedure(self):
        program = 'f'

        with self.assertRaisesRegex(LookupError, 'missing procedure: f'):
            run(program)

    def test_unbound_parameter(self):
        program = 'a:Aa\na'

        with self.assertRaisesRegex(LookupError, 'unbound parameter: A'):
            run(program)

    def test_too_few_arguments(self):
        program = 'a(A):Aa\na(s)'

        with self.assertRaisesRegex(TypeError, 'a takes 1 argument but 0 were given'):
            run(program)

    def test_too_many_arguments(self):
        program = 'a(A,B):ABa(A,B,B)\na(s,r)'

        with self.assertRaisesRegex(TypeError, 'a takes 2 arguments but 3 were given'):
            run(program)

    def test_expected_command_or_procedure_call(self):
        program = 'a(A):Aa(A)\na(1)'

        with self.assertRaisesRegex(TypeError, 'parameter A does not evaluate to a command .* or a procedure call: 1'):
            run(program)

    def test_expected_number(self):
        program = 'a(A):sa(A-1)\na(r)'

        with self.assertRaisesRegex(TypeError, 'parameter A does not evaluate to a number'):
            run(program)
