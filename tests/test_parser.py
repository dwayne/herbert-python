import unittest

from herbert.error import SyntaxError
from herbert.parser import parse


class NoProcedureDefinitionsTestCase(unittest.TestCase):
    def test_command(self):
        tree = parse('slr')

        self.assertEqual(len(tree.children), 1)

        main = tree.children[0]
        self.assertEqual(main.data, 'main')
        self.assertEqual(main.children[0].type, 'COMMAND')
        self.assertEqual(main.children[0], 's')
        self.assertEqual(main.children[1].type, 'COMMAND')
        self.assertEqual(main.children[1], 'l')
        self.assertEqual(main.children[2].type, 'COMMAND')
        self.assertEqual(main.children[2], 'r')

    def test_procedure_call(self):
        tree = parse('a')

        self.assertEqual(len(tree.children), 1)

        main = tree.children[0]
        self.assertEqual(main.data, 'main')

        pcall = main.children[0]
        self.assertEqual(pcall.data, 'pcall')
        self.assertEqual(len(pcall.children), 1)
        self.assertEqual(pcall.children[0].type, 'PNAME')
        self.assertEqual(pcall.children[0], 'a')


class ProcedureDefinitionsTestCase(unittest.TestCase):
    def test_with_no_params(self):
        tree = parse('a:ssra\na')

        self.assertEqual(len(tree.children), 2)

        pdef = tree.children[0]

        self.assertEqual(pdef.data, 'pdef')
        self.assertEqual(len(pdef.children), 2)

        pname = pdef.children[0]
        self.assertEqual(pname.type, 'PNAME')
        self.assertEqual(pname, 'a')

        body = pdef.children[1]
        self.assertEqual(body.data, 'body')
        self.assertEqual(len(body.children), 4)
        self.assertEqual(body.children[0].type, 'COMMAND')
        self.assertEqual(body.children[0], 's')
        self.assertEqual(body.children[1].type, 'COMMAND')
        self.assertEqual(body.children[1], 's')
        self.assertEqual(body.children[2].type, 'COMMAND')
        self.assertEqual(body.children[2], 'r')
        self.assertEqual(body.children[3].data, 'pcall')
        self.assertEqual(body.children[3].children[0].type, 'PNAME')
        self.assertEqual(body.children[3].children[0], 'a')

    def test_with_params(self):
        tree = parse('f(A,B,C,D,E,F):sAf(AA,B,F-C+D+2,-D+1,E-1,sFl)\nf(sl,5,-1,100,10,r)')

        self.assertEqual(len(tree.children), 2)

        pdef = tree.children[0]

        self.assertEqual(pdef.data, 'pdef')
        self.assertEqual(len(pdef.children), 3)

        pname = pdef.children[0]
        self.assertEqual(pname.type, 'PNAME')
        self.assertEqual(pname, 'f')

        params = pdef.children[1]
        self.assertEqual(params.data, 'params')
        self.assertEqual(len(params.children), 6)
        self.assertEqual(params.children[0].type, 'PARAM')
        self.assertEqual(params.children[0], 'A')
        self.assertEqual(params.children[1].type, 'PARAM')
        self.assertEqual(params.children[1], 'B')
        self.assertEqual(params.children[2].type, 'PARAM')
        self.assertEqual(params.children[2], 'C')
        self.assertEqual(params.children[3].type, 'PARAM')
        self.assertEqual(params.children[3], 'D')
        self.assertEqual(params.children[4].type, 'PARAM')
        self.assertEqual(params.children[4], 'E')
        self.assertEqual(params.children[5].type, 'PARAM')
        self.assertEqual(params.children[5], 'F')

        body = pdef.children[2]
        self.assertEqual(body.data, 'body')
        self.assertEqual(len(body.children), 3)
        self.assertEqual(body.children[0].type, 'COMMAND')
        self.assertEqual(body.children[0], 's')
        self.assertEqual(body.children[1].type, 'PARAM')
        self.assertEqual(body.children[1], 'A')

        pcall = body.children[2]
        self.assertEqual(pcall.data, 'pcall')
        self.assertEqual(pcall.children[0].type, 'PNAME')
        self.assertEqual(pcall.children[0], 'f')

        args = pcall.children[1]
        self.assertEqual(args.data, 'args')
        self.assertEqual(len(args.children), 6)
        self.assertEqual(args.children[0].data, 'sexpr')
        self.assertEqual(args.children[1].data, 'sexpr')
        self.assertEqual(args.children[2].data, 'expr')
        self.assertEqual(args.children[3].data, 'expr')
        self.assertEqual(args.children[4].data, 'expr')
        self.assertEqual(args.children[5].data, 'sexpr')


class SyntaxErrorTestCase(unittest.TestCase):
    def test_missing_procedure_name(self):
        with self.assertRaises(SyntaxError) as ctx:
            parse(':ssra\na')

    def test_missing_procedure_body(self):
        with self.assertRaises(SyntaxError) as ctx:
            parse('a:\na')

    def test_missing_main(self):
        with self.assertRaises(SyntaxError) as ctx:
            parse('a:ssra\n')
