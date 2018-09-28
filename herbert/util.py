from functools import wraps


def pluralize(n, singular, plural):
    assert n >= 0
    return singular if n == 1 else plural


_SENTINEL = object()

def cachedmethod(method):
    cached_result = _SENTINEL

    @wraps(method)
    def wrapper(*args, **kwargs):
        nonlocal cached_result

        if cached_result is _SENTINEL:
            cached_result = method(*args, **kwargs)

        return cached_result

    return wrapper
