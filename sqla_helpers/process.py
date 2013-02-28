# -*- coding: utf-8 -*-
operators = {
    'not': '__ne__',
    'lt': '__lt__',
    'le': '__le__',
    'gt': '__gt__',
    'ge': '__ge__',
    'in': 'in_',
    'like': 'like',
    'ilike': 'ilike',
}
"""
Dictionnaire des opérateurs applicables à un InstrumentedAttribut
La clef représente l'opérateur dans la syntaxe :mod:`sqla_helpers` et la valeur
est le nom de la méthode a appellé sur un objet de type. InstrumentAttribut
"""

def process_params(cls, class_found, **kwargs):
    """
    Retourne une liste de critères SQLAlchemy suivant la syntaxe sqla_helpers.

    :param:`cls` est la classe racine à partir de laquelle les attributs seront
    récupérer.

    Au fur et à mesure du traitement, on stock les classes des attributs
    rencontrées dans le paramètre :param:`class_found`. Elles ne sont ajoutées
    que lorsqu'elles n'apparaissent pas dans la liste (i.e. pas de doublon dans
    la liste.)

    L'attribut est donc modifié au fur et à mesure du traitement (Effet de bord).

    .. rubric:: Exemple

    Si l'on souhaite faire une recherche sur l'attribut `name` d'un objet de la
    classe Treatment, la fonction sera appellée:

    .. code-block:: python

        >>> class_found = []
        >>> process_params(Treatment, class_found, name='test')
        [<sqlalchemy.sql.expression.BinaryExpression object at 0x22bd3d0>]
        >>> class_found
        []

    Dans cet exemple le paramètre :param:`class_found` n'a pas bougé puisque
    l'attribut `name` n'est pas un objet ezn relation. Mais si nous recherchions
    des traitments par status nous aurions

    .. code-block:: python

        >>> class_found = []
        >>> process_params(Treatment, class_found, status_name='test')
        [<sqlalchemy.sql.expression.BinaryExpression object at 0x22bd3d0>]
        >>> class_found
        [Status]

    """
    criterion = []
    for k, v in kwargs.iteritems():
        # Si il y a des __ dans le paramètre, on souhaite
        # faire une recherche sur un attribut d'une relation
        params = k.split('__')
        # Le dernier élément peut être un opérateur
        if params[-1] in operators.keys():
            op = params.pop()
            operator = operators[op]
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
            if klass not in class_found:
                class_found.append(klass)

        instrumented_attr = getattr(klass, comparator_attr_name)
        comparator = getattr(instrumented_attr, operator)
        criterion.append(comparator(v))

    return criterion
