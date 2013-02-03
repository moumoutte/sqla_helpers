#-*- coding: utf-8 -*-
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm.collections import InstrumentedList

class ClassProperty(property):
    """
    Classe qui a pour but de fournir une alternative à l'utilisation du
    decaroteur property pour un attribut de classe.
    """
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class BaseModel(object):
    """
    Classe d'un modèle de base. Elle fournit du sucre syntaxiques pour faire de
    la récupération d'objets en base.
    """
    operators = {
        'not': '__ne__',
        'lt': '__lt__',
        'le': '__lte__',
        'gt': '__gt__',
        'gte': '__gte__',
        'in': 'in_',
        'like': 'like',
        'ilike': 'ilike',
    }


    @classmethod
    def register_sessionmaker(cls, sessionmaker):
        """
        Enregistrement de la fonction utiliser pour créer une session.
        La fonction enregistrée ne doit prendre aucun paramètre
        """
        cls.sessionmaker = staticmethod(sessionmaker)


    @ClassProperty
    @classmethod
    def session(cls):
        """
        Appelle :attr:`BaseModel.sessionmaker` et renvoie une session
        nouvellement construite.

        Ne pas oubliez de mettre en place :attr:`BaseModel.sessionmaker` dans
        l'initialisation de l'application.
        """
        return cls.sessionmaker()


    @classmethod
    def search(cls, **kwargs):
        """
        Effectue la recherche d'objet suivant les critères passés en arguments.
        Le retour est un objet :class:`sqlachemy.orm.query.Query`

        Ce qui permet d'enchaîner les critères de recherches si besoin.
        """
        query = cls.session.query(cls)
        # On maintient une liste des classes déjà jointes
        joined_class = []
        for k, v in kwargs.iteritems():
            # Si il y a des __ dans le paramètre, on souhaite
            # faire une recherche sur un attribut d'une relation
            params = k.split('__')
            # Le dernier élément peut être un opérateur
            if params[-1] in cls.operators.keys():
                op = params.pop()
                operator = cls.operators[op]
            else:
                operator = '__eq__'
            # On récupère le nom de l'attribut de comparaison
            # qui est systèmatiquement en dernier
            comparator_attr_name = params.pop()
            # On garde la classe à partir de laquelle on récupère l'attribut
            # courant.
            klass = cls
            # La boucle permet de récupérer l'attribut dans la classe la plus
            # loin dans les relations.
            # Exemple = [parameter, task, id_task]
            # comparator_attr_name = "id_task"
            # cls.(classe de l'attribut "parameter").(classe de l'attribut
            # "task").id_task)
            for param in params:
                klass = getattr(klass, param).property.mapper.class_
                if klass not in joined_class:
                    query = query.join(klass)
                    joined_class.append(klass)

            instrumented_attr = getattr(klass, comparator_attr_name)
            comparator = getattr(instrumented_attr, operator)
            query = query.filter(comparator(v))

        return query


    @classmethod
    def get(cls, **kwargs):
        """
        Retourne un objet correspond aux critères donnés.
        """
        query = cls.search(**kwargs)
        return query.one()


    @classmethod
    def all(cls):
        """
        Retourne tous les objets d'une classe contenu en base.
        """
        return cls.search().all()


    @classmethod
    def filter(cls, **kwargs):
        """
        Retourne une liste d'objets d'une classe correspond aux critères donnés.
        """
        query = cls.search(**kwargs)
        return query.all()


    def dump(self, excludes=[], depth=2):
        """
        Retourne l'objet sous forme de dictionnaire python avec ses
        dépendances.

        La profondeur permet de ne pas copier les attributs trop profondéments.
        Par exemple avec une profondeur de 1, on n'ira pas chercher les objets
        en relation.

        Le paramètre d'exclusion sert à exclure les attributs que l'on ne
        veut pas exporter.

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
