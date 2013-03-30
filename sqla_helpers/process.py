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
Dictonnary of usasable operators to a `InstrumentedAttribut`.
Keys are operators in :mod:`sqla_helpers` syntax and values are methods name
called by an InstrumentAttribut object.
"""

def process_params(cls, class_found, **kwargs):
    """
    Returns a `SQLAlchemy` criterions list matching :mod:`sqla_helpers` syntax.

    :param:`cls` is the root class providing attributes

    During processing, found attributes are stored  in :param:`class_found`
    parameters. :param:`class_found` is a set.

    Attribute is updated during process.

    .. rubric:: Example

    If a quering on the attribute `name` from a `Treatment` object, the function
    'll be called:

    .. code-block:: python

        >>> class_found = []
        >>> process_params(Treatment, class_found, name='test')
        [<sqlalchemy.sql.expression.BinaryExpression object at 0x22bd3d0>]
        >>> class_found
        []

    In this example, because of the attribute `name` isn't in the related object, the
    :param:`class_found` isn't modified. In other hand a query on `status` attribute :

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
