from Lexer import lex
from Parser import CheckSyntax,Parser
import sys


str = 'if(a == 1){a = a+1;}a = 123 * 2 + 2;'
tokens = lex(str)
parser = CheckSyntax(tokens)
lang = parser.lang()
print(lang)
