class HerbertError(Exception):
    pass


class SyntaxError(HerbertError):
    pass


class RuntimeError(HerbertError):
    pass


class LookupError(RuntimeError):
    pass


class TypeError(RuntimeError):
    pass
