from nose.tools import raises
from sqla_helpers.tests.class_test import  Treatment, Status

from sqla_helpers.process import process_params

def test_simple():
    res = process_params(Treatment, [], id=0)
    assert len(res) == 1
    assert str(Treatment.id == 0) == str(res[0])
    res = process_params(Treatment, [], name=0)
    assert len(res) == 1
    assert str(Treatment.name == 0) == str(res[0])

def test_multiple_key():
    res = process_params(Treatment, [], id=0, name='toto')
    assert len(res) == 2

@raises(AttributeError)
def test_unknow_attr():
    process_params(Treatment, [], test='toto')

def test_simple_relation():
    joined_class = []
    res = process_params(Treatment, joined_class, status__name='test')
    assert len(joined_class)
    assert Status in joined_class
    assert str(Status.name == 'test') == str(res[0])

def test_multiple_relation():
    joined_class = []
    process_params(Treatment, joined_class, status__name='test',
                         status__id=0)
    assert len(joined_class) == 1
    assert Status in joined_class
