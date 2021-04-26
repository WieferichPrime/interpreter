import sys

class Node:
    def __init__(self, name = '', value = '',height = 0):
        self.childs = []
        self.name = name
        self.value = value
        self.height = height
        self.rpn = []
    def __repr__(self):
        str = ''
        for child in self.childs:
            str += "\t"*child.height + f'{child}'
        return f'{self.name}\n{str}'

class Leaf:
    def __init__(self, name = '', value = '', height = 0):
        self.name = name
        self.value = value
        self.height = height

    def __repr__(self):
        return f'{self.name} {self.value}\n'

class CheckSyntax:
    def __init__(self, tokens):
        self.tokens = tokens
        self.height = 0
        self.bufer = []
        self.index = -1
        self.prev = 0
        self.advance()

    def advance(self):
        if self.index < len(self.tokens) - 1:
            self.index += 1
            self.current_tok = self.tokens[self.index]

    def lang(self):
        lang = Node('lang')
        prev = 0
        while(self.index < len(self.tokens) - 1):
            try:
                self.height=1
                expr = self.expr(prev)
                lang.childs.append(expr)
                lang.rpn += expr.rpn
                prev += len(expr.rpn)
            except BaseException:
                raise BaseException
        return lang

    def expr(self,prev):
        expr = Node('expr',height=self.height)
        self.height += 1
        if self.current_tok[1] == 'VAR':
            try:
                assign_expr = self.assign_expr()
                expr.childs.append(assign_expr)
                expr.rpn = assign_expr.rpn
                self.height -= 1
                return expr
            except BaseException:
                raise BaseException

        if self.current_tok[1] == 'IF_KW':
            try:
                if_expr = self.if_expr(prev)
                expr.childs.append(if_expr)
                expr.rpn  = if_expr.rpn
                self.height -= 1
                return expr
            except BaseException:
                raise BaseException
        if self.current_tok[1] == 'WHILE_KW':
            try:
                while_expr = self.while_expr(prev)
                expr.childs.append(while_expr)
                expr.rpn = while_expr.rpn
                self.height -= 1
                return expr
            except BaseException:
                raise BaseException

    def assign_expr(self):
        assign_expr = Node('assign_expr','=',self.height)
        try:
            self.check_next_t('VAR')
            self.bufer.append(self.current_tok)
            self.height += 1
            assign_expr.childs.append(Leaf(self.current_tok[1], self.current_tok[0],self.height))
            self.height -= 1
            self.advance()
            self.check_next_t('ASSIGN')
            self.bufer.append(self.current_tok)
            self.advance()
            self.height += 1
            assign_expr.childs.append(self.math_expr())
            self.check_next_t('CLOSE')
            self.advance()
            self.height-=1
            self.to_rpn(assign_expr)
            return assign_expr
        except BaseException:
            self.bufer.clear()
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
                    self.bufer.append(self.current_tok)
                    self.advance()
                    try:
                        self.height += 1
                        math_expr.childs.append(self.math_expr())
                    except:
                        raise BaseException
                except: break
            self.height-=1
            return math_expr
        except BaseException:
            self.bufer.clear()
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
                    self.bufer.append(self.current_tok)
                    self.advance()
                    try:
                        self.height += 1
                        logical_expr.childs.append(self.logical_expr())
                    except:
                        raise BaseException
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
                self.bufer.append(self.current_tok)
                self.advance()
                math_expr = self.math_expr()
                math_expr_wbr.childs.append(math_expr)
                self.check_next_t('RP')
                self.bufer.append(self.current_tok)
                self.advance()
                self.height-=1
                math_expr_wbr.rpn = math_expr.rpn
                return math_expr_wbr
        except BaseException:
            raise BaseException


    def while_expr(self, prev):
        while_expr = Node('while_expr', height=self.height)
        try:
            self.check_next_t('WHILE_KW')
            self.advance()
            self.height += 1
            if_head = self.if_head()
            while_expr.childs.append(if_head)
            if_head.rpn.append('end')
            if_head.rpn.append('!F')
            next_prev = prev + len(if_head.rpn)
            while_expr.rpn += if_head.rpn
            self.height += 1
            if_body = self.if_body(next_prev)
            while_expr.childs.append(if_body)
            if_body.rpn.append('start')
            if_body.rpn.append('!')
            while_expr.rpn += if_body.rpn
            for i in range(len(while_expr.rpn)):
                if while_expr.rpn[i] == 'start':
                    while_expr.rpn[i] = prev
                if while_expr.rpn[i] == 'end':
                    while_expr.rpn[i] = prev + len(while_expr.rpn)
            self.height-=1
            return while_expr
        except BaseException:
            raise BaseException

    def value(self):
        value = Leaf(height=self.height)
        try:
            try:
                self.check_next_t('INT')
                self.bufer.append(self.current_tok)
            except:
                self.check_next_t('VAR')
                self.bufer.append(self.current_tok)
            value.name = self.current_tok[1]
            value.value = self.current_tok[0]
            self.advance()
            self.height -= 1
            return value
        except BaseException:
            raise BaseException

    def if_expr(self, prev):
        try:
            if_expr = Node('if_expr',height=self.height)
            self.check_next_t('IF_KW')
            self.advance()
            self.height += 1
            if_head = self.if_head()
            if_expr.childs.append(if_head)
            if_head.rpn.append('else')
            if_head.rpn.append('!F')
            next_prev = prev + len(if_head.rpn) # next_prev - элементов ДО для следующего уровня вложенности
            if_expr.rpn += if_head.rpn
            self.height += 1
            if_body = self.if_body(next_prev)
            if_expr.childs.append(if_body)
            if_body.rpn.append('end')
            if_body.rpn.append('!')
            next_prev += len(if_body.rpn)
            if_expr.rpn += if_body.rpn
            for i in range(len(if_expr.rpn)):
                if if_expr.rpn[i] == 'else':
                    if_expr.rpn[i] = prev + len(if_expr.rpn)
                if if_expr.rpn[i] == 'end':
                    if_expr.rpn[i] = prev + len(if_expr.rpn)
                    end_index = i
            try:
                self.check_next_t(('ELSE_KW'))
                self.advance()
                try:
                    else_if_body = self.if_body(next_prev)
                    if_expr.childs.append(else_if_body)
                    if_expr.rpn+=else_if_body.rpn
                    for i in range(len(if_expr.rpn)):
                        if i == end_index:
                            if_expr.rpn[i] = prev + len(if_expr.rpn)
                except BaseException:
                    raise BaseException
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
            logical_expr =  self.logical_expr()
            self.to_rpn(logical_expr)
            if_head.rpn = logical_expr.rpn
            if_head.childs.append(logical_expr)
            self.check_next_t('RP')
            self.advance()
            self.height-=1
            return if_head
        except BaseException:
            self.bufer.clear()
            raise BaseException


    def if_body(self,prev):
        if_body = Node('if_body',height=self.height)
        self.height += 1
        try:
            self.check_next_t('LB')
            self.advance()
            expr = self.expr(prev)
            while(expr):
                if_body.rpn += expr.rpn
                if_body.childs.append(expr)
                try :
                    self.check_next_t('RB')
                    self.advance()
                    self.height -= 1
                    return if_body
                except:
                    expr = self.expr()
        except BaseException:
            self.bufer.clear()
            raise BaseException

    def check_next_t(self, values):
        if self.current_tok[1] not in values:
            raise BaseException

    def to_rpn(self, expr):
        parser = Parser(self.bufer)
        expr.rpn = parser.rpn()


class Parser:
    def __init__(self, tokens = []):
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

    def rpn(self):
        while ((len(self.tokens) != 0) | (self.current_tok[1] != None)):
            if (self.current_tok[1] in ('VAR','INT')):
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
            if (self.current_tok[1] in ('RP','RB')):
                while(self.stack[-1][1] not in ('LP','LB')):
                    self.output.append(self.stack.pop()[0])
                    if (len(self.stack) == 0):
                        break
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

