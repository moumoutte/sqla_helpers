# -*- coding: utf-8 -*-
from sqlalchemy import or_, and_, not_
from sqla_helpers.process import process_params

class ASTNode(object):

    def operator(self, *args, **kwargs):
        raise NotImplementedError()


    def __init__(self, lhs=None, rhs=None, **operand):
        self.lhs = lhs
        self.rhs = rhs
        self.operand = operand


    def __call__(self, klass, class_found):
        # Si l'on a des paramètres bruts, c'est que l'on est une feuille de
        # l'arbre
        # On retourne alors le process des paramètres
        if self.operand:
            clauses = process_params(klass, class_found, **self.operand)
        else:
            # Sinon, nous avons des enfants et l'on retourne l'opération que l'on
            # représente sur le retour des enfants.
            clauses = []
            if self.lhs:
                clauses.append(self.lhs(klass, class_found))
            if self.rhs:
                clauses.append(self.rhs(klass, class_found))

        return self.operator(*clauses)


class OrASTNode(ASTNode):

    def operator(self, *args):
        return or_(*args)


class AndASTNode(ASTNode):

    def operator(self, *args):
        return and_(*args)


class NotASTNode(ASTNode):

    def __init__(self, lhs=None, **operand):
        super(NotASTNode, self).__init__(lhs, None, **operand)


    def operator(self, *args):
        return not_(*args)



class Q(object):
    """
    Classe abstraite représentant des opérations logiques en conservrant une
    syntaxe sqla_helpers
    """

    # Le Q object n'est là que pour récupérer la syntaxe sqla_helpers et
    # implémenter des opérations (or , and, not...).
    # Au fur et à mesure des opération le Q Object maintient un AST.
    # Chaque opération renvoit en fait un Q object avec un AST mis à jour
    # par rapport à l'objet courant et l'objet avec lequel on fait une opération
    # C'est le __call__ du Q object qui fait un appel sous-jacent au __call__ de
    # des nœud de l'ast. Le retour étant un opération d'SQLAlchemy que l'on peut
    # passer un objet Query.
    def __init__(self, astnode=None, **kwargs):
        if astnode:
            self.ast = astnode
        else:
            self.ast = AndASTNode(**kwargs)


    def __call__(self, klass, class_found):
        return self.ast(klass, class_found)


    def __or__(self, q):
        return Q(OrASTNode(self.ast, q.ast))


    def __and__(self, q):
        return Q(AndASTNode(self.ast, q.ast))


    def __invert__(self):
        return Q(NotASTNode(self.ast))
