#-*- coding: utf-8 -*-

from sqlalchemy.orm.state import InstanceState

def instancied(cls):
    """
    Instancie une classe sans passer par le __init__.
    Il faudrait être un peu plus sur de la création de l'objet..
    """
    instance = cls.__new__(cls)
    instance._sa_instance_state = InstanceState(instance,
                                                  instance._sa_class_manager)
    return instance
