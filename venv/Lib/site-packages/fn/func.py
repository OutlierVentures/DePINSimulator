from functools import partial, update_wrapper, wraps
from sys import version_info


_has_type_hint_support = version_info[:2] >= (3, 5)


def identity(arg):
    return arg


class F(object):
    """Provide simple syntax for functions composition
    (through << and >> operators) and partial function
    application (through simple tuple syntax).

    Usage example:

    >>> func = F() << (_ + 10) << (_ + 5)
    >>> print(func(10))
    25
    >>> func = F() >> (filter, _ < 6) >> sum
    >>> print(func(range(10)))
    15
    """

    __slots__ = "f",

    def __init__(self, f=identity, *args, **kwargs):
        self.f = partial(f, *args, **kwargs) if any([args, kwargs]) else f

    @classmethod
    def __compose(cls, f, g):
        """Produces new class intance that will
        execute given functions one by one. Internal
        method that was added to avoid code duplication
        in other methods.
        """
        return cls(lambda *args, **kwargs: f(g(*args, **kwargs)))

    def __ensure_callable(self, f):
        """Simplify partial execution syntax.
        Rerurn partial function built from tuple
        (func, arg1, arg2, ...)
        """
        return self.__class__(*f) if isinstance(f, tuple) else f

    def __rshift__(self, g):
        """Overload >> operator for F instances"""
        return self.__class__.__compose(self.__ensure_callable(g), self.f)

    def __lshift__(self, g):
        """Overload << operator for F instances"""
        return self.__class__.__compose(self.f, self.__ensure_callable(g))

    def __call__(self, *args, **kwargs):
        """Overload apply operator"""
        return self.f(*args, **kwargs)


def curried(func):
    """A decorator that makes the function curried

    Usage example:

    >>> @curried
    ... def sum5(a, b, c, d, e):
    ...     return a + b + c + d + e
    ...
    >>> sum5(1)(2)(3)(4)(5)
    15
    >>> sum5(1, 2, 3)(4, 5)
    15
    """

    def _args_len(func):
        if _has_type_hint_support:
            from inspect import signature
            args = signature(func).parameters
        else:
            from inspect import getargspec
            args = getargspec(func).args

        return len(args)

    @wraps(func)
    def _curried(*args, **kwargs):
        f = func
        count = 0
        while isinstance(f, partial):
            if f.args:
                count += len(f.args)
            f = f.func

        if count == _args_len(f) - len(args):
            return func(*args, **kwargs)

        para_func = partial(func, *args, **kwargs)
        update_wrapper(para_func, f)
        return curried(para_func)

    return _curried
