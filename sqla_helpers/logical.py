# -*- coding: utf-8 -*-
from sqlalchemy import or_, and_
from sqla_helpers.process import process_params

class ASTNode(object):

    def __init__(self, operator, lhs=None, rhs=None, **operand):
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs
        self.operand = operand
        print operand


    def __call__(self, klass, class_found):

        if self.operand:
            print self.operand
            return  process_params(klass, class_found, **self.operand)

        clauses = []
        if self.lhs:
            clauses.extend(self.lhs(klass, class_found))
        if self.rhs:
            clauses.extend(self.rhs(klass, class_found))

        return self.operator(*clauses)


class OrASTNode(ASTNode):

    def __init__(self, lhs=None, rhs=None, **operand):
        super(OrASTNode, self).__init__(or_, lhs, rhs, **operand)


class AndASTNode(ASTNode):

    def __init__(self, rhs=None, lhs=None, **operand):
        super(AndASTNode, self).__init__(and_, lhs, rhs, **operand)



class Q(object):
    """
    Classe abstraite représentant des opérations logiques en conservrant une
    syntaxe sqla_helpers
    """

    def __init__(self, astnode=None, **kwargs):
        if astnode:
            self.ast = astnode
        else:
            self.ast = AndASTNode(**kwargs)


    def __call__(self, klass, class_found):
        return self.ast(klass, class_found)


    def __or__(self, q):
        return Q(OrASTNode(self.ast, q.ast))
