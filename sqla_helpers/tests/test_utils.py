from sqla_helpers.utils import call_if_callable

def test_simple_nocallable():
    assert u'test' == call_if_callable(u'test')


def test_simple_callable():
    def simple():
        return u'test'

    assert u'test' == call_if_callable(simple)


def test_simple_callable_args():
    def add2(x):
        return x + 2

    assert 4 == call_if_callable(add2, [2])


def test_simple_callable_kwargs():
    def add_something(x, something=2):
        return x + something 

    assert 4 == call_if_callable(add_something, [2])
    assert 6 == call_if_callable(add_something, [2], {'something': 4})


def test_callable_multiple_args():
    def add_all(x, y, z):
        return x + y + z

    assert 6 == call_if_callable(add_all, [1, 2, 3])


def test_callable_multiple_kwargs():
    def add_all(x, bonii=2, other=4):
        return x + bonii + other

    kwargs = {'bonii': 4, 'other': 8}
    assert 14 == call_if_callable(add_all, [2], kwargs)


def test_callable_else():
    def concat_plop(x):
        return u'{0}.plop'.format(x)

    assert u'test.plop' == call_if_callable(u'test', else_=concat_plop)
