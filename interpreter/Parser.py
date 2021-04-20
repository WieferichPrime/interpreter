import sys

class Node:
    def __init__(self, name = '', value = '',height = 0):
        self.childs = []
        self.name = name
        self.value = value
        self.height = height
    def __str__(self):
        str = ''
        for child in self.childs:
            str += "\t"*child.height + f'{child}'
        return f'{self.name}\n{str}'

class Leaf:
    def __init__(self, name = '', value = '', height = 0):
        self.name = name
        self.value = value
        self.height = height

    def __str__(self):
        return f'{self.name} {self.value}\n'

class CheckSyntax:
    def __init__(self, tokens):
        self.tokens = tokens
        self.bufer = []
        self.height = 0
        self.advance()
        self.exprs_token = []


    def advance(self):
        if (len(self.tokens) != 0):
            self.current_tok = self.tokens.pop(0)
            self.bufer.append(self.current_tok)
        else: self.current_tok = ('', 'None', None)

    def lang(self):
        lang = Node('lang')
        while((len(self.tokens) != 0) | (self.current_tok[1] != 'None')):
            try:
                self.height=1
                lang.childs.append(self.expr())
                if self.current_tok[1] != 'None':
                    last = self.bufer.pop()
                    self.exprs_token.append(self.bufer.copy())
                    self.bufer.clear()
                    self.bufer.append(last)
                else:
                    self.exprs_token.append(self.bufer.copy())
                    self.bufer.clear()
            except:
                return 'Syntax error'
        return lang

    def expr(self):
        expr = Node('expr',height=self.height)
        self.height += 1

        if self.current_tok[1] == 'VAR':
            try:
                expr.childs.append(self.assign_expr())
                self.height -= 1
                return expr
            except BaseException:
                raise BaseException

        if self.current_tok[1] == 'IF_KW':
            try:
                expr.childs.append(self.if_expr())
                self.height -= 1
                return expr
            except BaseException:
                raise BaseException
        if self.current_tok[1] == 'WHILE_KW':
            try:
                expr.childs.append(self.while_expr())
                self.height -= 1
                return expr
            except BaseException:
                raise BaseException

    def assign_expr(self):
        assign_expr = Node('assign_expr','=',self.height)
        try:
            self.check_next_t('VAR')
            self.height += 1
            assign_expr.childs.append(Leaf(self.current_tok[1], self.current_tok[0],self.height))
            self.height -= 1
            self.advance()
            self.check_next_t('ASSIGN')
            self.advance()
            self.height += 1
            assign_expr.childs.append(self.math_expr())
            self.check_next_t('CLOSE')
            self.advance()
            self.height-=1
            return assign_expr
        except BaseException:
            raise BaseException


    def math_expr(self):
        math_expr = Node('math_expr',height=self.height)
        try:
            self.height += 1
            try:
                math_expr.childs.append(self.value())
            except:
                math_expr.childs.append(self.math_expr_wbr())
            while (len(self.tokens) > 1):
                try:
                    self.check_next_t(('PLUS', 'MINUS', 'DIV', 'MUL'))
                    math_expr.value = self.current_tok[0]
                    self.advance()
                    self.height += 1
                    math_expr.childs.append(self.math_expr())
                except: break
            self.height-=1
            return math_expr
        except BaseException:
            raise BaseException

    def logical_expr(self):
        logical_expr = Node('logical_expr',height=self.height)
        try:
            self.height += 1
            logical_expr.childs.append(self.value())
            while (len(self.tokens) != 1):
                try:
                    self.check_next_t('LOGICAL_OP')
                    logical_expr.value = self.current_tok[0]
                    self.advance()
                    self.height += 1
                    logical_expr.childs.append(self.logical_expr())
                except: break
            self.height-=1
            return logical_expr
        except BaseException:
            raise BaseException

    def math_expr_wbr(self):
        math_expr_wbr = Node('math_expr_wbr',height=self.height)
        self.height += 1
        try:
                self.check_next_t('LP')
                self.advance()
                math_expr_wbr.childs.append(self.math_expr())
                self.check_next_t('RP')
                self.advance()
                self.height-=1
                return math_expr_wbr
        except BaseException:
            raise BaseException


    def while_expr(self):
        while_expr = Node('while_expr', height=self.height)
        try:
            self.check_next_t('WHILE_KW')
            self.advance()
            self.height += 1
            while_expr.childs.append(self.if_head())
            self.height += 1
            while_expr.childs.append(self.if_body())
            self.height-=1
            return while_expr
        except BaseException:
            raise BaseException

    def value(self):
        value = Leaf(height=self.height)
        try:
            try:
                self.check_next_t('INT')
            except:
                self.check_next_t('VAR')
            value.name = self.current_tok[1]
            value.value = self.current_tok[0]
            self.advance()
            self.height -= 1
            return value
        except BaseException:
            raise BaseException

    def if_expr(self):
        try:
            if_expr = Node('if_expr',height=self.height)
            self.check_next_t('IF_KW')
            self.advance()
            self.height += 1
            if_expr.childs.append(self.if_head())
            self.height += 1
            if_expr.childs.append(self.if_body())
            try:
                self.check_next_t(('ELSE_KW'))
                self.advance()
                if_expr.childs.append(self.if_body())
            except:
                pass
            self.height-=1
            return if_expr
        except BaseException:
            raise BaseException

    def if_head(self):
        if_head = Node('if_head',height=self.height)
        try:
            self.check_next_t('LP')
            self.advance()
            self.height += 1
            if_head.childs.append(self.logical_expr())
            self.check_next_t('RP')
            self.advance()
            self.height-=1
            return if_head
        except BaseException:
            raise BaseException


    def if_body(self):
        if_body = Node('if_body',height=self.height)
        self.height += 1
        try:
            self.check_next_t('LB')
            self.advance()
            expr = self.expr()
            while(expr):
                if_body.childs.append(expr)
                try :
                    self.check_next_t('RB')
                    self.advance()
                    self.height-=1
                    return if_body
                except:
                    expr = self.expr()
        except BaseException:
            raise BaseException

    def check_next_t(self, values):
        if self.current_tok[1] not in values:
            raise BaseException



class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.advance()
        self.stack = []
        self.output = []
    def advance(self):
        if (len(self.tokens) != 0):
            self.current_tok = self.tokens.pop(0)
        else:
            self.current_tok = ('', None)
        return self.current_tok

    def rpn(self, tokens):
        while ((len(self.tokens) != 0) | (self.current_tok[1] != None)):
            if (self.current_tok[1] in ('VAR','INT','ELSE_KW')):
                self.output.append(self.current_tok[0])
                self.advance()
            if self.is_func(self.current_tok):
                self.stack.append(self.current_tok)
                self.advance()
            if self.is_op(self.current_tok):
                if (len(self.stack) != 0):
                    if self.is_op(self.stack[-1]):
                        if self.stack[-1][2] >= self.current_tok[2]:
                            self.output.append(self.stack.pop()[0])
                self.stack.append(self.current_tok)
                self.advance()
            if (self.current_tok[1] in ('LP','LB')):
                self.stack.append(self.current_tok)
                self.advance()
            if (self.current_tok[1] in ('RP','RB','CLOSE')):
                while(self.stack[-1][1] not in ('LP','LB')):
                    self.output.append(self.stack.pop()[0])
                    if (len(self.stack) == 0):
                        break
                if self.current_tok[1] not in ('CLOSE'):
                    self.stack.pop()
                self.advance()
                if (len(self.stack) != 0):
                    if self.is_func(self.stack[-1]):
                        self.output.append(self.stack.pop()[0])
        while(len(self.stack) != 0):
            self.output.append(self.stack.pop()[0])
        return self.output

    def is_op(self, t):
        return t[1] in ('PLUS', 'MINUS', 'DIV', 'MUL', 'ASSIGN','LOGICAL_OP')

    def is_func(self, t):
        return t[1] in ('IF_KW', 'WHILE_KW')

