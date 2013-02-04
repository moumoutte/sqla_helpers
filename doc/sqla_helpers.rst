Helpers SQLAlchemy - :class:`sqla_helpers.base_model.BaseModel`
===============================================================

Getting Started
----------------

:class:`sqla_helpers.base_model.BaseModel` a pour but d'instrumenter la syntaxe d'SQLAlchemy pour
fournir à l'utiliseur final, des méthodes simplifiées permettant la récupération
d'objets en base.

:class:`sqla_helpers.base_model.BaseModel` est une classe qui est utilisable en tant que Mixin, elle
n'hérite d'aucune classe et elle n'est pas à sous-classer.
Pour avoir accès aux méthodes dans un modèle, il faut alors déclarer une table
comme ceci:

.. code-block:: python

    from somewhere import DeclarativeBase
    from sqla_helpers.base_model import BaseModel

    class MyModel(DeclarativeBase, BaseModel):
        id = ... # Clef primaire , l'identifiant sous forme d'entier
        awesome_attr = ... # Attribut quelconque du modèle
        other_model = relationship('MyOtherModel', backref='mymodel')


    class MyOtherModel(DeclarativeBase, BaseModel):
        id = ... # Clef primaire
        name = ...
        model_id = ... # Clef étrangère sur MyModel


La classe :class:`DeclarativeBase` est la classe générée par la fonction
:func:`declarative_base` d'SQLAlchemy.

Il est également possible d'utiliser :class:`sqla_helpers.base_model.BaseModel` comme paramètre `cls` de la fonction :func:`declarative_base`.
Et ainsi on peut se passer de l'utilisation de la classe comme Mixin.


.. code-block:: python

    from sqlalchemy.ext.declarative import declarative_base
    from sqla_helpers.base_model import BaseModel
    DeclarativeBase = declarative_base(cls=BaseModel)


.. code-block:: python

    class MyModel(DeclarativeBase):
        # ...


:class:`sqla_helpers.base_model.BaseModel` attend une manière de récupérer une session quand une requête est effectuée.
Pour ce faire, elle fait appel à la fonction stockée dans l'attribut :attr:`sqla_helpers.base_model.BaseModel.sessionmaker`.
Ainsi, lors de l'initialisation de l'application, il faut stocker un
sessionmaker dans la classe, grâce à la méthode
`sqla_helpers.base_model.BaseModel.register_sessionmaker`

.. code-block:: python

    # Initialisation de l'application
    def main():
        # ...
        BaseModel.register_sessionmaker(scoped_session(sessionmaker(bind=engine)))
        # ...


Pour passer une session globale, il suffit simplement que la fonction passée à :attr:`sqla_helpers.base_model.BaseModel.sessionmaker`
renvoie la référence sur la session globale

.. code-block:: python

    from somwhere import DBSession

    # Initialisation de l'application
    def main():
        # ...
        BaseModel.register_sessionmaker(lambda: DBSession)
        # ...


Cas d'utilisation simple :

.. code-block:: python

    >>> MyModel.all()
    [<MyModel object at 0x2c19d90>]
    >>> MyModel.get(id=2)
    <MyModel object at 0x2c19d90>
    >>> MyModel.get(id=3)
    *** NoResultFound: No row was found for one()
    >>> MyModel.filter(id=2)
    [<MyModel object at 0x2c19d90>]
    >>> MyModel.filter(id=3)
    []


* :meth:`sqla_helpers.base_model.BaseModel.all` ramène l'ensemble des objets en base.
* :meth:`sqla_helpers.base_model.BaseModel.filter` ramène les objets correspondants aux critères donnés sous forme de liste.
* :meth:`sqla_helpers.base_model.BaseModel.get` ramène un unique élément correspond aux critères données.

On peut bien évidemment enchaîner les critères de recherche qui seront pris en
compte avec un opérateur `&&` (ET) logique.

.. code-block:: python

    >>> MyOtherModel.filter(name='toto')
    [<MyOtherModel object at 0x2c19d90>, <MyOtherModel object at 0x2e27e08>]
    >>> MyOtherModel.filter(name='toto', id=2)
    [<MyOtherModel object at 0x2c19d90>]


Recherche sur critères de relation
----------------------------------

Les critères de recherche valides pour une classe sont définies par ses
attributs (Pour MyOtherModel ça sera `id`, `name`, `model_id`).

Cela est également valable pour le relation SQLAlchemy.

Par exemple, on peut rechercher tous les MyModel dont le MyOtherModel a pour nom
'toto'

.. code-block:: python

    >>> MyModel.filter(awesome_attr__name='toto')
    [<MyModel object at 0x2c19d90>]


On peut même rechercher suivant un objet complet.

.. code-block:: python

    >>> otherModel = MyOtherModel.get(name='toto')
    >>> MyModel.filter(awesome_attr=otherModel)
    [<MyModel object at 0x2c19d90>]


Le séparateur `__` (double underscore) permet de faire la séparation entre les
différentes entités sollicitées.

La recherche par les attributs des relations peut se faire en profondeur.
Imaginons que `MyOtherObject` est un attribut `other_attr` qui est en relation
avec un objet MyOtherOtherObject.

Il est alors possible de rechercher tous les MyModel dont le MyOtherObject a un
MyOtherOtherObject dont le nom est 'toto'.

.. code-block:: python

    >>> MyModel.filter(awesome_attr__other_attr__name='toto')
    [<MyModel object at 0x2c19d90>]



Des opérateurs
--------------

Il est possible de spécifier d'autres critères que ceux d'égalités. En séparant
encore une fois, avec des '__' (doubles underscores) et en mettant le nom de
l'opérateur à la fin du critère.

Par exemple, si l'on veut tous les MyModel qui n'ont PAS pour id la valeur 2.

.. code-block:: python

    >>> MyModel.filter(id__not=2)
    []

Les opérateurs disponibles sont :

* 'not': Non-égal
* 'lt': inférieur
* 'le': Inférieur ou égal
* 'gt': Plus grand
* 'gte': Plus grand ou égal
* 'in': Contenu dans (Le paramètre de recherche doit-être une liste)
* 'like': opérateur SQL LIKE
* 'ilike': opérateur SQL ILIKE

Du JSON
-------

Souvent dans les applications web, le client et le serveur communique par l'intermédiaire du format JSON.
Pour faciliter les opérations de chargement, :mod:`sqla_helpers` fournit des
méthodes permettant de charger des objets modèles depuis un dictionnaire python ou bien de générer un dictionnaire depuis un objet modèle SQLALchemy.

La méthode :meth:`sqla_helpers.base_model.BaseModel.dump` permet la génération d'un dictionnaire qui est transformable en JSON.

.. code-block:: python

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


Et la méthode de classe `sqla_helpers.base_model.Model.load` qui permet d'instancier des objets à partir d'un dictionnaire.
Le passage par dictionnaire est sensé faciliter l'accès aux données en JSON ou bien générer du JSON depuis le
dictionnaire.

Pour le chargement d'un objet, les objets sont récupérés en base si les attributs composant la clef primaire
sont trouvés dans le dictionnaire. Sinon, une nouvelle instance est créée.

.. code-block:: python

        >>> t = Treatment.get(id=7)
        >>> t.name
        'YEAH \\o/'
        >>> t.id
        7
        >>> t.status.name
        'Sacre status !'
        >>> t.status.id
        7
        >>> t = Treatment.load({'id': 7, 'name': 'hello'})
        >>> t.name, t.id
        ('hello', 7)
        >>> session.commit()
        >>> t.dump()
        {
                'id': 7,
                'name': u'hello',
                'status': {'id': 7, 'name': u'Sacre status !'},
                'status_id': 7
        }
        >>> tr = Treatment.load(t.dump())
        >>> tr == t
        True
        >>> tr.status == t.status
        True
        >>> Treatment.load(tr.dump()).dump()
        {
                'id': 7,
                'name': u'hello',
                'status': {'id': 7, 'name': u'Sacre status !'},
                'status_id': 7
        }
        >>> tr = Treatment.load({'name': 'nouveau traitmente', 'status': {'name': 'nouveau status'}})
        >>> tr.id
        None
        >>> tr.status.id
        None
        >>> session.add(tr)
        >>> session.commit()
        >>> tr.id
        10
        >>> tr.status.id
        8


La classe :class:`sqla_helpers.base_model.BaseModel`
====================================================

.. autoclass:: sqla_helpers.base_model.BaseModel
  :members:
