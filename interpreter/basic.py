from Lexer import lex
from Parser import CheckSyntax, Parser
from Stack_Machine import StackMachine
import sys
str = input('>>> ')
while str != 'exit':
    try:
        tokens = lex(str)
        print(tokens)
        parser = CheckSyntax(tokens)
        lang = parser.lang()
        print(lang)
        for char in lang.rpn:
            print(char[0],end = '\t')
        print()
        for i in range(len(lang.rpn)):
            print(i,end = '\t')
        print()
    except:
        print('Syntax error')
    try:
        sm = StackMachine(lang.rpn)
        sm.run()
        for var in sm.variables.items():
            print(var)
    except BaseException:
        pass
    str = input('>>> ')
sys.exit(0)

