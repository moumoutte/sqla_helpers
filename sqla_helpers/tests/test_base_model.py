from functools import wraps

from mock import Mock
from nose.tools import raises

from sqla_helpers.base_model import BaseModel, SessionMakerExists


def save_sessionmaker(fun):
    """
    Guarantee to restore sessionmaker in BaseModel at the end of function called
    """
    @wraps(fun)
    def wrapper(*args, **kwargs):
        old_sessionmaker = BaseModel.sessionmaker
        try:
            res = fun(*args, **kwargs)
        finally:
            BaseModel.sessionmaker = old_sessionmaker    

    return wrapper


@save_sessionmaker
def test_register_simple_session():
    Session = u'session'
    BaseModel.register_sessionmaker(Session)
    assert BaseModel.session == Session


@save_sessionmaker
def test_register_function_session():
    def build_session():
        return u'built_session'

    BaseModel.register_sessionmaker(build_session)
    assert BaseModel.session == u'built_session'


@save_sessionmaker
@raises(SessionMakerExists)
def test_register_session_maker_already_registered():
    BaseModel.register_sessionmaker(u'test')
    BaseModel.register_sessionmaker(u'plop') 


@save_sessionmaker
def test_force_sessionmaker():
    BaseModel.register_sessionmaker(u'test')
    BaseModel.register_sessionmaker(u'plop', force=True) 
