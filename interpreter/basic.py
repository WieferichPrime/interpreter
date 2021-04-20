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
        for expr in parser.exprs_token:
            print(expr)
        str = input('>>> ')
    except:
        pass
sys.exit(0)

