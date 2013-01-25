#-*- coding: utf-8 -*-
"""
Helpers SQLAlchemy - :class:`base_model.BaseModel`
==================================================

Getting Started
----------------

:class:`base_model.BaseModel` a pour but d'instrumenter la syntaxe d'SQLAlchemy pour
fournir à l'utiliseur final, des méthodes simplifiées permettant la récupération
d'objets en base.

:class:`base_model.BaseModel` est une classe qui est utilisable en tant que Mixin, elle
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

Ainsi pour une session SQLAlchemy donnée, le modèle possède des méthodes de
recherche.


Cas d'utilisation simple :

.. code-block:: python

    >>> MyModel.all(session)
    [<MyModel object at 0x2c19d90>]
    >>> MyModel.get(session, id=2)
    <MyModel object at 0x2c19d90>
    >>> MyModel.get(session, id=3)
    *** NoResultFound: No row was found for one()
    >>> MyModel.filter(session, id=2)
    [<MyModel object at 0x2c19d90>]
    >>> MyModel.filter(session, id=3)
    []


* :meth:`base_model.BaseModel.all` ramène l'ensemble des objets en base.
* :meth:`base_model.BaseModel.filter` ramène les objets correspondants aux critères donnés sous forme de liste.
* :meth:`base_model.BaseModel.get` ramène un unique élément correspond aux critères données.

On peut bien évidemment enchaîner les critères de recherche qui seront pris en
compte avec un opérateur `&&` (ET) logique.

.. code-block:: python

    >>> MyOtherModel.filter(session, name='toto')
    [<MyOtherModel object at 0x2c19d90>, <MyOtherModel object at 0x2e27e08>]
    >>> MyOtherModel.filter(session, name='toto', id=2)
    [<MyOtherModel object at 0x2c19d90>]


Recherche sur critères de relation
----------------------------------

Les critères de recherche valides pour une classe sont définies par ses
attributs (Pour MyOtherModel ça sera `id`, `name`, `model_id`).

Cela est également valable pour le relation SQLAlchemy.

Par exemple, on peut rechercher tous les MyModel dont le MyOtherModel a pour nom
'toto'

.. code-block:: python

    >>> MyModel.filter(session, awesome_attr__name='toto')
    [<MyModel object at 0x2c19d90>]

.. warning::

    On ne peut pas rechercher une relation par un objet en entier. L'idée, c'est
    de fournir une surcouche à SQLAlchemy, pas d'ajouter des fonctionnalités.

Le séparateur `__` (double underscore) permet de faire la séparation entre les
différentes entités sollicitées.

La recherche par les attributs des relations peut se faire en profondeur.
Imaginons que `MyOtherObject` est un attribut `other_attr` qui est en relation
avec un objet MyOtherOtherObject.

Il est alors possible de rechercher tous les MyModel dont le MyOtherObject a un
MyOtherOtherObject dont le nom est 'toto'.

.. code-block:: python

    >>> MyModel.filter(session, awesome_attr__other_attr__name='toto')
    [<MyModel object at 0x2c19d90>]



Des opérateurs
--------------

Il est possible de spécifier d'autres critères que ceux d'égalités. En séparant
encore une fois, avec des '__' (doubles underscores) et en mettant le nom de
l'opérateur à la fin du critère.

Par exemple, si l'on veut tous les MyModel qui n'ont PAS pour id la valeur 2.

.. code-block:: python

    >>> MyModel.filter(session, id__not=2)
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


"""