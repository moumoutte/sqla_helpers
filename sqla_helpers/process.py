# -*- coding: utf-8 -*-
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

def process_params(cls, class_found, **kwargs):
    """
    Retourne une liste de critère.
    """
    criterion = []
    for k, v in kwargs.iteritems():
        # Si il y a des __ dans le paramètre, on souhaite
        # faire une recherche sur un attribut d'une relation
        print k, v
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
