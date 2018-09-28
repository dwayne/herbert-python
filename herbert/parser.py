from lark import Lark, LexError, ParseError

from .error import SyntaxError


GRAMMAR = """
    // Rules

    h      : pdef* main
    main   : stmt+

    pdef   : PNAME [params] ":" body _EOL
    params : "(" PARAM ("," PARAM)* ")"
    body   : (stmt | PARAM)+

    ?stmt  : COMMAND
           | PNAME [args] -> pcall

    args   : "(" arg ("," arg)* ")"
    ?arg   : PARAM -> var
           | PARAM (stmt | PARAM)+ -> sexpr
           | stmt (stmt | PARAM)* -> sexpr
           | expr

    expr   : NEG PARAM
           | NEG? NUM
           | NEG? (NUM | PARAM) ((PLUS | MINUS) (NUM | PARAM))+

    // Tokens

    _EOL    : /\\n/
    COMMAND : /[slr]/
    NEG     : /[-]/
    MINUS   : /[-]/
    NUM     : /[0-9]+/
    PARAM   : /[A-Z]/
    PLUS    : /[+]/
    PNAME   : /[abcdefghijkmnopqtuvwxyz]/
"""


parser = Lark(GRAMMAR, parser='lalr', start='h')


def parse(text):
    try:
        return parser.parse(text.strip())
    except (LexError, ParseError) as e:
        raise SyntaxError from e
