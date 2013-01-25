#-*- coding: utf-8 -*-

class BaseModel(object):
    operators = {
        'not': '__ne__',
        'lt': '__lt__',
        'le': '__lte__',
        'gt': '__gt__',
        'gte': '__gte__',
        'in': 'in_',
        'like': 'like_',
        'ilike': 'ilike_'
    }

    @classmethod
    def search(cls, session, **kwargs):
        query = session.query(cls)
        # On maintient une liste des classes déjà jointes
        joinedClass = []
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
            while len(params) > 0:
                klass = getattr(klass, params.pop(0)).property.mapper.class_
                if klass not in joinedClass:
                    query = query.join(klass)
                    joinedClass.append(klass)

            instrumentedAttr = getattr(klass, comparator_attr_name)
            comparator = getattr(instrumentedAttr, operator)
            query = query.filter(comparator(v))

        return query


    @classmethod
    def get(cls, session, **kwargs):
        query = cls.search(session, **kwargs)
        return query.one()


    @classmethod
    def all(cls, session):
        return session.query(cls).all()


    @classmethod
    def filter(cls, session, **kwargs):
        query = cls.search(session, **kwargs)
        return query.all()
