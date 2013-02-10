#-*- coding: utf-8 -*-
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm.collections import InstrumentedList

from sqla_helpers import loading
from sqla_helpers.process import process_params

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

    process_params = classmethod(process_params)


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
    def search(cls, *operator, **criterion):
        """
        Effectue la recherche d'objet suivant les critères passés en arguments.
        Le retour est un objet :class:`sqlachemy.orm.query.Query`

        Ce qui permet d'enchaîner les critères de recherches si besoin.
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


    @classmethod
    def get(cls, *operators, **criterions):
        """
        Retourne un objet correspond aux critères donnés.
        """
        query = cls.search(*operators, **criterions)
        return query.one()


    @classmethod
    def all(cls):
        """
        Retourne tous les objets d'une classe contenu en base.
        """
        return cls.search().all()


    @classmethod
    def filter(cls, *operators, **criterions):
        """
        Retourne une liste d'objets d'une classe correspond aux critères donnés.
        """
        query = cls.search(*operators, **criterions)
        return query.all()


    @classmethod
    def load(cls, d, hard=False):
        """
        Instancie un objet de la classe à partir d'attribut récupérer dans le
        dictionnaire fournit.

        Si le dictionnaire fournit toutes les valeurs qui constituent la clef
        primaire de l'objet, alors l'objet est chargé depuis la base. Puis
        les valeurs indiquées dans le dictionnaire sont rentrées dans l'objet
        chargée.

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

        Si l'option `hard` est à True , une exception est levée si une valeur
        n'est pas trouvée dans le dictionnaire fournit.
        """

        # On détermine si on doit charger l'instance depuis la base ou non.
        # La décision est prise si tous les attributs qui constitue la clef
        # primaire de l'objet sont trouvés dans le dico. Si oui, on charge
        # depuis la base, sinon on crée une nouvelle instance
        from_db = False
        loading_key = {}
        for attr in cls.__mapper__.primary_key:
            if not attr.key in d:
                from_db = False
                break

            loading_key[attr.key] = d[attr.key]
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
                attr_value = d[attr_key]
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
                        for d in attr_value:
                            instance_attr.append(attr_class.load(d))
                    else:
                        instance_attr = attr_class.load(attr_value)

                else:
                    instance_attr = attr_value

                setattr(instance, attr_key, instance_attr)

        return instance




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
