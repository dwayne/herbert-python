import numbers

from .error import LookupError, TypeError
from .util import pluralize


class Interpreter:
    def __call__(self, parse_tree):
        assert parse_tree.data == 'h'

        self._env = Env()
        *self._pdefs, main = parse_tree.children

        assert main.data == 'main'

        return self._interp_seq(main.children)

    def _interp_seq(self, seq):
        allow_number = len(seq) == 1

        for x in seq:
            if hasattr(x, 'type') and x.type == 'PARAM':
                yield from self._interp_param(x, allow_number)
            else:
                yield from self._interp_stmt(x)

    def _interp_stmt(self, stmt):
        if hasattr(stmt, 'type'):
            assert stmt.type == 'COMMAND'
            yield str(stmt)
        else:
            assert stmt.data == 'pcall'

            try:
                name, args = stmt.children
            except ValueError:
                name = stmt.children[0]
                args = []
            else:
                assert name.type == 'PNAME'
                assert args.data == 'args'
                args = args.children
            nargs = len(args)

            pdef = self._lookup_pdef(str(name))
            try:
                params, body = pdef.children[1:]
            except ValueError:
                params = []
                body = pdef.children[1]
            else:
                assert params.data == 'params'
                assert body.data == 'body'
                params = params.children
            nparams = len(params)

            if nargs == nparams:
                try:
                    bindings = self._bind(str(name), params, args)
                except IgnoreCall:
                    pass
                else:
                    self._env = Env(bindings=bindings, outer=self._env)
                    try:
                        yield from self._interp_seq(body.children)
                    finally:
                        self._env = self._env.outer
            else:
                argument = pluralize(nparams, 'argument', 'arguments')
                was = pluralize(nargs, 'was', 'were')

                raise TypeError('%s takes %d %s but %d %s given' % (name, nparams, argument, nargs, was))

    def _interp_param(self, param, allow_number):
        value = self._lookup(str(param))

        if isinstance(value, Deferred):
            prev_env, self._env = self._env, value.env
            try:
                yield from self._interp_seq(value.seq)
            finally:
                self._env = prev_env
        else:
            assert isinstance(value, numbers.Integral)
            if allow_number:
                yield value
            else:
                raise TypeError('parameter %s does not evaluate to a command s, l or r or a procedure call: %d' % (param, value))

    def _interp_arg(self, arg, name, index):
        if arg.data == 'var':
            assert len(arg.children) == 1 and arg.children[0].type == 'PARAM'
            return self._lookup(str(arg.children[0]))

        if arg.data == 'sexpr':
            return Deferred(self._env, arg.children)

        assert arg.data == 'expr'
        return self._interp_expr(arg.children)

    def _interp_expr(self, expr):
        assert expr

        if expr[0].type == 'NEG':
            sign = -1
            terms = expr[1:]
        else:
            sign = 1
            terms = expr

        sum = 0
        for term in expr:
            if term.type == 'PLUS':
                sign = 1
            elif term.type == 'MINUS':
                sign = -1
            elif term.type == 'NUM':
                sum += sign * int(str(term))
            else:
                assert term.type == 'PARAM'
                value = self._lookup(str(term))

                if isinstance(value, numbers.Integral):
                    sum += sign * value
                else:
                    raise TypeError('parameter %s does not evaluate to a number: %s' % (term, value))

        return sum

    def _bind(self, name, params, args):
        bindings = {}

        for index, (param, arg) in enumerate(zip(params, args)):
            value = self._interp_arg(arg, name, index)

            if value == 0:
                raise IgnoreCall

            bindings[str(param)] = value

        return bindings

    def _lookup_pdef(self, name):
        for pdef in self._pdefs:
            pname = pdef.children[0]
            assert pname.type == 'PNAME'

            if name == pname:
                return pdef

        raise LookupError('missing procedure: %s' % name)

    def _lookup(self, name):
        return self._env.lookup(name)


class Env:
    def __init__(self, bindings=None, outer=None):
        self.outer = outer
        self.bindings = {} if bindings is None else bindings

    def lookup(self, name):
        try:
            return self.bindings[name]
        except KeyError:
            raise LookupError('unbound parameter: %s' % name)


class Deferred:
    def __init__(self, env, seq):
        self.env = env
        self.seq = seq


class IgnoreCall(Exception):
    pass


interp = Interpreter()
