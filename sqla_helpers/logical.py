# -*- coding: utf-8 -*-

"""
Abstract Syntatic Tree
======================

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
    A tree's node represent a logic Sqlalchemy operator.
    Contains 2 child tree of a set of criterion.


    Handled criterions are describes in  :mod:`sqla_helpers`.

        >>> ast = AndASTNode(id=4, status__name='foo')

    Criterions 'll be process by the `process_param` function
    during processing of subtree by `__call__` function.

        >>> ast(MyClass, [])
        <sqlalchemy.sql.expression.BinaryExpression object at 0x1f04090>

    If a node contains criterions, the node is a leaf. (meaning the :attr:`ASTNode.operand`
    attribute is not `None`.)

    If node contains children, a recursive processing of children subtrees is done.

    `ASTNode.operator` method is excecuted during the return of `process_param`
    or during the recursive return of children.

    :class: `ASTNode` is an abstract class which doesn't implement :method: ASTNode.operator`.
    """

    def operator(self, *args, **kwargs):
        raise NotImplementedError()


    def __init__(self, lhs=None, rhs=None, **operand):
        self.lhs = lhs
        self.rhs = rhs
        self.operand = operand


    def __call__(self, klass, class_found):
        """
        Process every node.
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
        Excecut a logical or on `SQLAlchemy` criterions.
        """
        return or_(*args)


class AndASTNode(ASTNode):

    def operator(self, *args):
        """
        Excecut a logical and on `SQLAlchemy` criterions.
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
    Class representing logical operators with sqla_helpers syntax.

    Q object is only here for processing the `sqla_helpers` syntax
    and implements opertators such as `or`, `and`, `not` ...

    During operations, the :class:`Q` object maintains an AST.
    Each operation return a :class:`Q` object with an updated AST in
    relation the current object and the operating object.

    The :method: `__call__` from :class:`Q` call the :method:`__call__`
    from AST children. The return is an `SQLAlchemy` opertation usable in
    a `Query` object.
    """

    def __init__(self, astnode=None, **kwargs):
        if astnode:
            self.ast = astnode
        else:
            self.ast = AndASTNode(**kwargs)


    def __call__(self, klass, class_found):
        """
        Processing and interpreting AST of current `Q` object.
        """
        return self.ast(klass, class_found)


    def __or__(self, q):
        return Q(OrASTNode(self.ast, q.ast))


    def __and__(self, q):
        return Q(AndASTNode(self.ast, q.ast))


    def __invert__(self):
        return Q(NotASTNode(self.ast))
