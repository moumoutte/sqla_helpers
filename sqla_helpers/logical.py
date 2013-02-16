# -*- coding: utf-8 -*-

"""
Arbre de syntaxe abstraite
==========================

.. autoclass:: ASTNode
    :members:
.. autoclass:: AndASTNode
    :members:
.. autoclass:: OrASTNode
    :members:

Q Object
========
.. autoclass:: Q
    :members:
"""

from sqlalchemy import or_, and_, not_
from sqla_helpers.process import process_params


class ASTNode(object):
    """
    Un nœud d'arbre représentant un opérateur logique (SQLAlchemy)
    Il contient soit un ensemble de critères soit deux autres nœud d'arbres (ses
    enfants.)

    Les critères gérés sont ceux d'écrit par la synxate de :mod:`sqla_helpers`

        >>> ast = AndASTNode(id=4, status__name='toto')

    Les critères seront interprétés par la fonction process_param lors du
    parcours du sous-arbre par la fonction __call__

        >>> ast(MyClass, [])
        <sqlalchemy.sql.expression.BinaryExpression object at 0x1f04090>

    Un nœud est une feuille de l'arbre si il contient des critères. (i.e. que
    l'attribut :attr:`ASTNode.operand` n'est pas à None)

    Sinon, il a des enfants et le parcours de l'arbre est un appel récursif pour
    chacun des fils.

    La méthode `ASTNode.operator` est exécutée au retour de process_params ou
    bien au retour de l'appel récursif sur les fils.

    ASTNode est une classe abstraite qui n'implémente pas `ASTNode.operator`.
    """

    def operator(self, *args, **kwargs):
        raise NotImplementedError()


    def __init__(self, lhs=None, rhs=None, **operand):
        self.lhs = lhs
        self.rhs = rhs
        self.operand = operand


    def __call__(self, klass, class_found):
        """
        Parcours et interprétation de chaque nœud de l'arbre.
        """
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
        """
        Exécute un OU logique sur des critères SQLAlchemy
        """
        return or_(*args)


class AndASTNode(ASTNode):

    def operator(self, *args):
        """
        Exécute un ET logique sur des critères SQLAlchemy
        """
        return and_(*args)


class NotASTNode(ASTNode):

    def __init__(self, lhs=None, **operand):
        super(NotASTNode, self).__init__(lhs, None, **operand)


    def operator(self, *args):
        """
        Exécute un NON logique sur les critères SQLAlchemy
        """
        return not_(*args)



class Q(object):
    """
    Classe représentant des opérations logiques en conservrant une
    syntaxe sqla_helpers


    Le Q object n'est là que pour récupérer la syntaxe sqla_helpers et
    implémenter des opérations (or , and, not...).
    Au fur et à mesure des opération le Q Object maintient un AST.
    Chaque opération renvoit en fait un Q object avec un AST mis à jour
    par rapport à l'objet courant et l'objet avec lequel on fait une opération
    C'est le __call__ du Q object qui fait un appel sous-jacent au __call__ de
    des nœud de l'ast. Le retour étant un opération d'SQLAlchemy que l'on peut
    passer un objet Query.
    """

    def __init__(self, astnode=None, **kwargs):
        if astnode:
            self.ast = astnode
        else:
            self.ast = AndASTNode(**kwargs)


    def __call__(self, klass, class_found):
        """
        Parcours et interprète l'arbre représenté par le Q object courant.
        """
        return self.ast(klass, class_found)


    def __or__(self, q):
        return Q(OrASTNode(self.ast, q.ast))


    def __and__(self, q):
        return Q(AndASTNode(self.ast, q.ast))


    def __invert__(self):
        return Q(NotASTNode(self.ast))
