import sys
import lexurgy_scanner as lexer
import lexurgy_parser as parser
import lexurgy_semcheck as checker

if len(sys.argv) != 3:
    raise Exception(f'Incorrect syntax.\nSyntax:\n\tpython main.py <rulefile> <txtfile>')

# initialize classes
lex = lexer.Lexer(sys.argv[1])
par = parser.Parser(lex)

# parse
root = par.parse()

# create semantic checker
chck = checker.Checker(sys.argv[2], root)
chck.semcheck()

"""
while True:
    tok = lex.lex()
    if lex.lexeme != "":
        print(f'token: {tok}, lexeme: {lex.lexeme}')
    else:
        print(f'token: {tok}')
    if tok == lexer.Tokens.EOF: break """