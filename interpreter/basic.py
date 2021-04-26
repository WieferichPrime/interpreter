from Lexer import lex
from Parser import CheckSyntax, Parser
import sys
str = input('>>> ')
while str != 'exit':
    try:
        tokens = lex(str)
        parser = CheckSyntax(tokens)
        lang = parser.lang()
        print(lang)
        for char in lang.rpn:
            print(char,end = '\t')
        print()
        for i in range(len(lang.rpn)):
            print(i,end = '\t')
        print()
    except:
        print('Syntax error')
    str = input('>>> ')
sys.exit(0)

