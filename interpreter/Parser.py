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
        self.buffer = []
        self.index = -1
        self.ret_index = 0
        self.advance()

    def advance(self):
        if self.index < len(self.tokens):
            self.index += 1
            if self.index == len(self.tokens):
                self.current_tok = ('',None)
            else:
                self.current_tok = self.tokens[self.index]

    def lang(self):
        lang = Node('lang')
        prev = 0
        while(self.index < len(self.tokens)):
            try:
                self.height=1
                expr = self.expr(prev)
                lang.childs.append(expr)
                lang.rpn += expr.rpn.copy()
                prev += len(expr.rpn)
            except BaseException:
                raise BaseException
        return lang

    def expr(self,prev):
        expr = Node('expr',height=self.height)
        self.height += 1
        self.ret_index = self.index
        if self.current_tok[1] == 'VAR':
            try:
                assign_expr = self.assign_expr()
                expr.childs.append(assign_expr)
                expr.rpn = assign_expr.rpn.copy()
                self.height -= 1
                return expr
            except BaseException:
                self.index = self.ret_index - 1;
                self.advance()
                self.buffer.clear()
                if self.current_tok[1] == 'VAR':
                    try:
                        function = self.function()
                        expr.childs.append(function)
                        self.check_next_t('CLOSE')
                        self.advance()
                        self.to_rpn(function)
                        expr.rpn = function.rpn.copy()
                        self.height -= 1
                        return expr
                    except BaseException:
                        self.index = self.ret_index - 1;
                        self.advance()
                        self.buffer.clear()
                        if self.current_tok[1] == 'VAR':
                            try:
                                method = self.method()
                                expr.childs.append(method)
                                self.check_next_t('CLOSE')
                                self.advance()
                                self.to_rpn(method)
                                expr.rpn = method.rpn.copy()
                                self.height -= 1
                                return expr
                            except BaseException:
                                raise BaseException
                else:
                    raise BaseException
        elif self.current_tok[1] == 'IF_KW':
            try:
                if_expr = self.if_expr(prev)
                expr.childs.append(if_expr)
                expr.rpn  = if_expr.rpn.copy()
                self.height -= 1
                return expr
            except BaseException:
                raise BaseException
        elif self.current_tok[1] == 'WHILE_KW':
            try:
                while_expr = self.while_expr(prev)
                expr.childs.append(while_expr)
                expr.rpn = while_expr.rpn.copy()
                self.height -= 1
                return expr
            except BaseException:
                raise BaseException

    def assign_expr(self):
        assign_expr = Node('assign_expr','=',self.height)
        try:
            self.check_next_t('VAR')
            self.buffer.append(self.current_tok)
            self.height += 1
            assign_expr.childs.append(Leaf(self.current_tok[1], self.current_tok[0],self.height))
            self.height -= 1
            self.advance()
            self.check_next_t('ASSIGN')
            self.buffer.append(self.current_tok)
            self.advance()
            self.height += 1
            self.ret_index = self.index
            try:
                if self.current_tok[1] == 'VAR' and self.tokens[self.index + 1][1] == 'POINT':
                    assign_expr.childs.append(self.method())
                elif self.current_tok[1] in ('VAR', 'LINKED_LIST_KW'):
                    assign_expr.childs.append(self.function())
            except:
                self.index = self.ret_index - 1
                self.advance()
                self.buffer.clear()
                assign_expr.childs.append(self.math_expr())
            self.check_next_t('CLOSE')
            self.advance()
            self.height -= 1
            self.to_rpn(assign_expr)
            return assign_expr
        except BaseException:
            #self.buffer.clear()
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
                    self.buffer.append(self.current_tok)
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
            #self.buffer.clear()
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
                    self.buffer.append(self.current_tok)
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
                self.buffer.append(self.current_tok)
                self.advance()
                math_expr = self.math_expr()
                math_expr_wbr.childs.append(math_expr)
                self.check_next_t('RP')
                self.buffer.append(self.current_tok)
                self.advance()
                self.height-=1
                math_expr_wbr.rpn = math_expr.rpn.copy()
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
            if_head.rpn.append(('!F',None))
            next_prev = prev + len(if_head.rpn)
            while_expr.rpn += if_head.rpn.copy()
            self.height += 1
            if_body = self.if_body(next_prev)
            while_expr.childs.append(if_body)
            if_body.rpn.append('start')
            if_body.rpn.append(('!',None))
            while_expr.rpn += if_body.rpn.copy()
            for i in range(len(while_expr.rpn)):
                if while_expr.rpn[i] == 'start':
                    while_expr.rpn[i] = (prev,'INT')
                if while_expr.rpn[i] == 'end':
                    while_expr.rpn[i] = (prev + len(while_expr.rpn),'INT')
            self.height-=1
            return while_expr
        except BaseException:
            raise BaseException

    def value(self):
        value = Leaf(height=self.height)
        try:
            try:
                self.check_next_t('INT')
                self.buffer.append(self.current_tok)
            except:
                self.check_next_t('VAR')
                self.buffer.append(self.current_tok)
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
            if_head.rpn.append(('!F',None))
            next_prev = prev + len(if_head.rpn) # next_prev - элементов ДО для следующего уровня вложенности
            if_expr.rpn += if_head.rpn.copy()
            self.height += 1
            if_body = self.if_body(next_prev)
            if_expr.childs.append(if_body)
            if_body.rpn.append('end')
            if_body.rpn.append(('!',None))
            next_prev += len(if_body.rpn)
            if_expr.rpn += if_body.rpn.copy()
            for i in range(len(if_expr.rpn)):
                if if_expr.rpn[i] == 'else':
                    if_expr.rpn[i] = (prev + len(if_expr.rpn),'INT')
                if if_expr.rpn[i] == 'end':
                    if_expr.rpn[i] = (prev + len(if_expr.rpn),'INT')
                    end_index = i
            try:
                self.check_next_t(('ELSE_KW'))
                self.advance()
                try:
                    else_if_body = self.if_body(next_prev)
                    if_expr.childs.append(else_if_body)
                    if_expr.rpn+=else_if_body.rpn.copy()
                    for i in range(len(if_expr.rpn)):
                        if i == end_index:
                            if_expr.rpn[i] = (prev + len(if_expr.rpn),'INT')
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
            self.height -= 1
            return if_head
        except BaseException:
            #self.buffer.clear()
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
                    expr = self.expr(prev)
        except BaseException:
            #self.buffer.clear()
            raise BaseException

    def method(self):
        try:
            method = Node('method',height = self.height)
            self.height += 1
            self.check_next_t('VAR')
            self.buffer.append(self.current_tok)
            self.advance()
            self.check_next_t('POINT')
            self.advance()
            func = self.function()
            method.childs.append(func)
            self.height -= 1
            return method
        except BaseException:
            raise BaseException

    def function(self):
        try:
            function = Node('function',height=self.height)
            self.height += 1
            self.check_next_t(('LINKED_LIST_KW', 'VAR'))
            if self.current_tok[1] == 'VAR':
                lst = list(self.current_tok)
                lst[1] = 'function_name'
                self.current_tok = tuple(lst)
            self.buffer.append(self.current_tok)
            self.advance()
            self.check_next_t('LP')
            self.buffer.append(self.current_tok)
            self.advance()
            function.childs.append(self.args())
            self.height -= 1
            self.check_next_t('RP')
            self.buffer.append(self.current_tok)
            self.advance()
            self.height -= 1
            return function
        except BaseException:
            #self.buffer.clear()
            raise BaseException


    def args(self):
        args = Node('args',height=self.height)
        self.height += 1
        try:
            value = self.value()
            self.check_next_t('COMMA')
            self.advance()
            while (value):
                value = self.value()
                args.childs.append(value)
                self.check_next_t('COMMA')
                self.advance()
        except:
            pass
        return args

    def check_next_t(self, values):
        if self.current_tok[1] not in values:
            raise BaseException

    def to_rpn(self, expr):
        parser = Parser(self.buffer)
        expr.rpn = parser.rpn()
        self.buffer.clear()


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
        var_count = 0
        read_vars = False
        while ((len(self.tokens) != 0) | (self.current_tok[1] != None)):
            if (self.current_tok[1] in ('VAR','INT')):
                if read_vars:
                    var_count += 1
                self.output.append(self.current_tok)
                self.advance()
            elif self.is_func(self.current_tok):
                read_vars = True
                self.stack.append(self.current_tok)
                self.advance()
            elif self.is_op(self.current_tok):
                if (len(self.stack) != 0):
                    if self.is_op(self.stack[-1]):
                        if self.stack[-1][2] >= self.current_tok[2]:
                            self.output.append(self.stack.pop())
                self.stack.append(self.current_tok)
                self.advance()
            elif (self.current_tok[1] in ('LP','LB')):
                self.stack.append(self.current_tok)
                self.advance()
            elif (self.current_tok[1] in ('RP','RB')):
                while(self.stack[-1][1] not in ('LP','LB')):
                    self.output.append(self.stack.pop())
                    if (len(self.stack) == 0):
                        break
                self.stack.pop()
                self.advance()
                if (len(self.stack) != 0):
                    if self.is_func(self.stack[-1]):
                        lst = list(self.stack.pop())
                        if read_vars:
                            lst[2] = var_count
                            func = tuple(lst)
                            read_vars = False
                            var_count = 0
                        self.output.append(func)
            elif self.current_tok[1] == 'POINT':
                self.advance()
        while(len(self.stack) != 0):
            self.output.append(self.stack.pop())
        return self.output

    def is_op(self, t):
        return t[1] in ('PLUS', 'MINUS', 'DIV', 'MUL', 'ASSIGN','LOGICAL_OP')

    def is_func(self, t):
        return t[1] in ('LINKED_LIST_KW','function_name')

