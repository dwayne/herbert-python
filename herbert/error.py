class HerbertError(Exception):
    pass


class LevelError(HerbertError):
    pass


class ProgramError(HerbertError):
    pass


class SyntaxError(HerbertError):
    pass


class RuntimeError(HerbertError):
    pass


class LookupError(RuntimeError):
    pass


class TypeError(RuntimeError):
    pass
