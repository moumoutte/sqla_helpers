#-*- coding: utf-8 -*-

from sqlalchemy.orm.state import InstanceState

def instancied(cls):
    """
    Return a class without use on `__init__`.


    Need more assurance about object creation
    """
    instance = cls.__new__(cls)
    instance._sa_instance_state = InstanceState(instance,
                                                  instance._sa_class_manager)
    return instance
