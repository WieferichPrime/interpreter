from Lexer import lex
from Parser import CheckSyntax, Parser
import sys
str = input('>>> ')
while str != 'exit':
    try:
        tokens = lex(str)
        parser = CheckSyntax(tokens)
        lang = parser.lang()
        print(lang,lang.rpn)
    except:
        print('Syntax error')
    str = input('>>> ')
sys.exit(0)

