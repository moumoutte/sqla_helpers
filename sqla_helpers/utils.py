#-*- coding: utf-8 -*-
"""
Some tools to help development
==============================

.. autofunction:: call_if_callable

"""

def call_if_callable(maybe_callable, callable_args=None, callable_kwargs=None, else_=lambda x: x):	
    """
    If `maybe_callable` is callable then it's called with `*callable_args` and `**callable_kwargs`.
    Else the function `else_` is called with `maybe_callable` as argument. `else_` default is the
    identity function, so when maybe_callable is not callable, the function returns `maybe_callable.`

    .. code-block:: python

        >>> call_if_callable(u'test')
        u'test'
        >>> def add2(x):
        ...     return x + 2
        >>> call_if_callable(add2, [4])
        6
        >>> def add_something(x, something=2)
        ...     return  x + something
        >>> call_if_callable(add_something, [4], {'something': 8})
        12
        >>> def concat_plop(string):
        ...        return u'{0}.plop'.format(string)
        >>> call_if_callable(u'test', else_=concat_plop)
        u'test.plop'
    
    :param maybe_callable: function to call if callable
    :param callable_args: List of argument to call with `maybe_callable`
    :param callable_kwargs: Dictonary of (key, value) to call with `maybe_callable`
    :param else_: Function to call if maybe_callable is not callable. One parameter supported : `maybe_callable`
    """

    callable_args = callable_args or []
    callable_kwargs = callable_kwargs or {}

    if hasattr(maybe_callable, '__call__'):
        res = maybe_callable(*callable_args, **callable_kwargs)
    else:
        res = else_(maybe_callable)

    return res
