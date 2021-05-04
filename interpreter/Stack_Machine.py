from LinkedList import LinkedList

class StackMachine:
    def __init__(self, input):
        self.stack = []
        self.input = input
        self.index = -1
        self.variables = {}
        self.advance()

    def advance(self):
        if self.index < len(self.input):
            self.index += 1
            if self.index == len(self.input):
                self.current_elem = ('', None)
            else:
                self.current_elem = self.input[self.index]

    def is_defined(self,a):
        try:
            if a in self.variables.keys():
                if self.variables[a] == 'Undefined':
                    raise BaseException
        except:
            print(f'Variable {a} is not defined')
            raise BaseException

    def bin_log_op(self,b,a,op):
        if op == '>':
            return a > b
        if op == '<':
            return a < b
        if op == '>=':
            return a >= b
        if op == '<=':
            return a <= b
        if op == '==':
            return a == b
        if op == '!=':
            return a != b
        if op == '&&':
            return a & b
        if op == '||':
            return a | b

    def bin_op(self,b,a,op):
        self.is_defined(a)
        if op == '+':
            return a+b
        if op == '-':
            return a-b
        if op == '*':
            return a*b
        if op == '/':
            return a/b

    def assign_op(self, b, a):
        try:
            self.is_defined(b)
            self.variables[a] = b
        except:
            raise BaseException

    def jmp(self, pos):
        if pos == len(self.input):
            self.index = pos
            return
        self.index = pos
        self.current_elem = self.input[self.index]

    def jmpf(self,pos,f):
        if not f:
            self.jmp(pos)
        else:
            self.advance()

    def run(self):
        try:
            while self.index < len(self.input):
                if self.current_elem[1] == 'INT':
                    self.stack.append(int(self.current_elem[0]))
                    self.advance()
                elif self.current_elem[1] == 'VAR':
                    if self.current_elem[0] not in self.variables:
                        self.variables[self.current_elem[0]] = 'Undefined'
                    self.stack.append(self.current_elem[0])
                    self.advance()
                elif self.current_elem[1] == 'LOGICAL_OP':
                    b = self.stack.pop()
                    a = self.stack.pop()
                    if b in self.variables.keys():
                        self.is_defined(b)
                        b = self.variables[b]
                    if a in self.variables.keys():
                        self.is_defined(a)
                        a = self.variables[a]
                    self.stack.append(self.bin_log_op(b, a, self.current_elem[0]))
                    self.advance()
                elif self.current_elem[1] == 'PLUS' or self.current_elem[1] == 'MINUS' or self.current_elem[1] == 'MUL' or self.current_elem[1] == 'DIV':
                    b = self.stack.pop()
                    a = self.stack.pop()
                    if b in self.variables.keys():
                        self.is_defined(b)
                        b = self.variables[b]
                    if a in self.variables.keys():
                        self.is_defined(a)
                        a = self.variables[a]
                    self.stack.append(self.bin_op(b,a,self.current_elem[0]))
                    self.advance()
                elif self.current_elem[1] == 'ASSIGN':
                    b = self.stack.pop()
                    if b in self.variables.keys():
                        self.is_defined(b)
                        b = self.variables[b]
                    self.assign_op(b, self.stack.pop())
                    self.advance()
                elif self.current_elem[0] == '!':
                    self.jmp(self.stack.pop())
                elif self.current_elem[0] == '!F':
                    pos = self.stack.pop()
                    f = self.stack.pop()
                    self.jmpf(pos, f)
                elif self.current_elem[1] in ('LINKED_LIST_KW','function_name'):
                    args = []
                    i = self.current_elem[2] # число параметров функции
                    while(i != 0):
                        args.insert(0, self.stack.pop())
                        i -= 1
                    if len(args) == 1:
                        args = args[0]
                    if self.current_elem[1] == 'LINKED_LIST_KW':
                        self.stack.append(LinkedList(args))
                        self.advance()
                    elif self.current_elem[0] == 'push':
                        self.variables[self.stack.pop()].push(args)
                        self.advance()
                    elif self.current_elem[0] == 'contains':
                        self.stack.append(self.variables[self.stack.pop()].contains(args))
                        self.advance()
                    elif self.current_elem[0] == 'get':
                        a = self.stack.pop()
                        lst = self.variables[a]
                        c = lst.get(args)
                        self.stack.append(c)
                        self.advance()
                    elif self.current_elem[0] == 'remove':
                        self.variables[self.stack.pop()].remove(args)
                        self.advance()
        except BaseException:
            raise BaseException

