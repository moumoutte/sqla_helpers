#-*- coding: utf-8 -*-
"""
.. autoclass:: SessionMakerExists
    :members:

.. autoclass:: BaseModel
    :members:
"""
from functools import wraps
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm.collections import InstrumentedList

from sqla_helpers import loading
from sqla_helpers.process import process_params
from sqla_helpers.utils import call_if_callable

class SessionMakerExists(Exception):
    """
    Exception raised when a session maker is already registered in :class:`sqla_helpers.base_model.BaseModel`
    """
    def __unicode__(self):
        return u'A session maker is already registered.'

    def __str__(self):
        return 'A session maker is already registered'


class ClassProperty(property):
    """
    Provide a decorator `property` to classemethod
    """
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


def query_operation(decorated_method=None, operation_name=None):
    """
    query_operation process a search on a query with criterion and operators.
    Then, the operation_name operation is called on the query. If operation_name is not set
    the operation_name is taken from the decorated method

    .. code-block:: python

        @query_operation
        def count(cls, *operators, **criterions):
            # This method will call the cls.search(*operators, **criterions)
            # Then , it will call count operation on the result of previous search
            # I.E. : the generated code will be "return cls.search(*operators, **criterions).count()"

        @query_operation(operation_name='one')
        def get(cls, *operators, **criterions):
            # It will process the same thing above, except the function compute on the query will be 'one'
            # I.E. : return cls.search(*operators, **criterions).one()
 
    .. warning:

        This decorataror defines the decorated_method as a classmethod.

    """

    if  decorated_method and operation_name is None:
        operation_name = decorated_method.__name__

    def _wrapper(decorated_method):

        @classmethod
        @wraps(decorated_method)
        def _decorator(querying_class, *operators, **criterions):

            query = querying_class.search(*operators, **criterions)
            method = query.__getattribute__(operation_name)
            return method()

        return _decorator

    if decorated_method is not None:
        return _wrapper(decorated_method)
    else:
        return _wrapper


class BaseModel(object):
    """
    Base Model Class.
    Provide syntactic sugar for getting object from database.
    """

    sessionmaker = None
    process_params = classmethod(process_params)


    @classmethod
    def register_sessionmaker(cls, sessionmaker, force=False):
        """
        Register the function for making session.
        This registered function mustn't have any parameters.
        For a globale session, just put the session as parameter.
        If a session maker is already registered, an exception is raised to avoid conflict.
        But, if you are sure about what your are doing, you can set `force` parameter to True.
        It's not advice.
        """
        if cls.sessionmaker is None or force:
            cls.sessionmaker = staticmethod(sessionmaker)
        else:
            raise SessionMakerExists()	


    @ClassProperty
    @classmethod
    def session(cls):
        """
        Call :attr:`BaseModel.sessionmaker` and returns a new session.

        Don't forget to call  :attr:`BaseModel.sessionmaker_maker` in application's initialization.
        """
        return call_if_callable(cls.sessionmaker)


    @classmethod
    def search(cls, *operator, **criterion):
        """
        Object search with criterions given in arguments.
        Returns a :class:`sqlachemy.orm.query.Query` object.

        Filters can be chained.
        """
        query = cls.session.query(cls)
        # On maintient une liste des classes déjà jointes
        joined_class = []
        clauses = []

        # On itère sur tous les objets operator qu'on a reçu et on process les
        # objets
        for operator in list(operator):
            clauses.append(operator(cls, joined_class))

        # On process les critéres qu'on nous passe directement
        clauses.extend(cls.process_params(joined_class, **criterion))
        query = query.join(*joined_class)
        return query.filter(*clauses)


    @query_operation(operation_name='one')
    def get(cls, *operators, **criterions):
        """
        Returns an object with criterions given in parameters.
        """

    @query_operation
    def all(cls):
        """
        Returns all objects from the same class contained in database.
        """

    @query_operation(operation_name='all')
    def filter(cls, *operators, **criterions):
        """
        Returns a list of objects from a class matching criterions given in parameters.
        """

    @query_operation
    def count(cls, *operators, **criterions):
        """
        Returns the number of objects matched by criterions

        .. code-block:: python

           >>> Treatment.count(status=u'OK')
           8
        """


    @classmethod
    def load(cls, dictionary, hard=False):
        """
        Returns an object from class with attributes got in dictionary's parameters.

        If all the primary keys are found in the dictionary, the object is
        loaded from database. Otherwise, values are set in the loading object.

        .. code-block:: python

            >>> t = Treatment.get(id=1)
            >>> t.name
            'Great Treatment'
            >>> t = Treatment.load({'id': 1, 'name': 'Awesome Treatment'})
            >>> t.name
            'Awesome Treatment'
            >>> session.commit()
            >>> Treatment.get(id=1).name
            'Awesome Treatment'

        If `hard` parameter is True, an exception is raised if a value isn't found
        in parameter's dictionary.
        """

        # On détermine si on doit charger l'instance depuis la base ou non.
        # La décision est prise si tous les attributs qui constitue la clef
        # primaire de l'objet sont trouvés dans le dico. Si oui, on charge
        # depuis la base, sinon on crée une nouvelle instance
        from_db = False
        loading_key = {}
        for attr in cls.__mapper__.primary_key:
            if not attr.key in dictionary:
                from_db = False
                break

            loading_key[attr.key] = dictionary[attr.key]
            from_db = True

        if from_db:
            instance = cls.get(**loading_key)
        else:
            instance = loading.instancied(cls)

        # Une fois l'instance crée , on itère sur toutes les propriétés de
        # la classe à laquelle elle appartient.
        # Et on cherche dans le dictionnaire si elles apparaissent.
        # En mode `hard`, si un clef n'est pas spécifiée on léve une
        # exception, sinon on ignore l'erreur.
        for attr_key, attr_type in cls.__mapper__._props.iteritems():
            try:
                attr_value = dictionary[attr_key]
            except KeyError:
                # En mode soft, on ne relache pas l'erreur
                # En mode hard, oui.
                if hard:
                    raise
            else:
                instance_attr = getattr(instance, attr_key)
                # Si l'attribut sur lequel nous sommes, est une relation,
                # On délégue son chargement à la classe à laquelle l'attrbut
                # appartient.
                # Sinon on se contente de mettre la valeur trouvée dans le
                # dictionnaire, dans l'attribut de la nouvelle instance.
                if isinstance(attr_type, RelationshipProperty):
                    attr_class = attr_type.mapper.class_
                    if isinstance(instance_attr, InstrumentedList):
                        # Si on est sur une liste, on s'attend à avoir une
                        # liste de dico
                        for obj_to_load in attr_value:
                            instance_attr.append(attr_class.load(obj_to_load))
                    else:
                        instance_attr = attr_class.load(attr_value)

                else:
                    instance_attr = attr_value

                setattr(instance, attr_key, instance_attr)

        return instance




    def dump(self, excludes=[], depth=2):
        """
        Returns object as dictionary with dependencies.

        `Depth` limits the recursion.

        IE : With depth set as 1, objects in relations aren't search.

        `excludes` use to exclude unwanted attributes.

        .. code-block:: python

            >>> t = Treatment.get(id=1)
            >>> print json.dumps(t.dump(), indent=4)
            {
                "status": {
                    "id": 1,
                    "name": "Ok"
                },
                "status_id": 1,
                "id": 1,
                "name": "Great Treatment"
            }

            >>> print json.dumps(t.dump(depth=1), indent=4)
            {
                "status_id": 1,
                "id": 1,
                "name": "Great Treatment"
            }
            >>> print json.dumps(t.dump(excludes=['status_id']), indent=4)
            {
                "status": {
                    "id": 1,
                    "name": "Ok"
                },
                "id": 1,
                "name": "Great Treatment"
            }

        """
        res = {}

        # On itére sur les propriétés de classes pour récupérer seulement
        # les attributs déclarer en base pour ne pas exporter les autres attributs
        # Mais on récupère bien la valeur dans l'instance d'objet.
        for attr, attr_type in self.__mapper__._props.iteritems():

            # Si le champ est à exclure on passe au champ suivant
            if attr in excludes:
                continue

            # Récupération de la valeur effective de l'attribut
            instance_attr = getattr(self, attr)
            if isinstance(attr_type, RelationshipProperty):

                # Si on est à la profondeur on ne fait rien
                if depth - 1 <= 0:
                    continue

                if isinstance(instance_attr, InstrumentedList):
                    res[attr] = [ a.dump(depth=depth-1) for a in instance_attr]
                else:
                    res[attr] = instance_attr.dump(depth=depth-1)

            else:
                res[attr] = instance_attr

        return res
