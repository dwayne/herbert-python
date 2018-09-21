import itertools


def count_bytes(parse_tree):
    assert parse_tree.data == 'h'

    *pdefs, main = parse_tree.children

    return sum(itertools.chain(
        map(_count_pdef, pdefs),
        map(_count_seq, main.children)
    ))


def _count_pdef(pdef):
    assert pdef.data == 'pdef'

    try:
        name, params, body = pdef.children
        params = params.children
    except:
        name, body = pdef.children
        params = []

    return 1 + len(params) + sum(map(_count_seq, body.children))


def _count_seq(x):
    if hasattr(x, 'type'):
        assert x.type == 'COMMAND' or x.type == 'PARAM'
        return 1
    else:
        assert x.data == 'pcall'

        try:
            name, args = x.children
            args = args.children
        except ValueError:
            name = x.children[0]
            args = []

        return 1 + sum(map(_count_arg, args))


def _count_arg(arg):
    if arg.data == 'var':
        return 1

    if arg.data == 'sexpr':
        return sum(map(_count_seq, arg.children))

    assert arg.data == 'expr'

    l = len(arg.children)
    if l % 2 == 1:
        l += 1
    l //= 2

    return l
