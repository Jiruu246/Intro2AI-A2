from logic import PropDefiniteKB
from utils import expr, Expr

# p1, p2, p3, a, b, c = map(Expr, 'p1 p2 p3 a b c'.split())

expression = expr('p1&B ==> C')
print(expression)

tells = []
asks = []
with open('test_HornKB copy.txt', 'r') as file:
    file.readline()
    clauses = list(filter(None, file.readline().strip().split(';')))
    for clause in clauses:
        if '=>' in clause:
            lhs, rhs = [symbol.strip() for symbol in clause.split('=>')]
            tells.append(Expr('==>', lhs, rhs))
        else:
            tells.append(clause)
    
    print(tells)
    file.readline()
    asks = list(filter(None, file.readline().strip().split(';')))
    print(asks)
    
# kb = PropDefiniteKB()
# for tell in tells:
#     kb.tell(expr(tell))
    
definite_clauses_KB = PropDefiniteKB()
for clause in ['(B & F) ==> E',
               '(A & E & F) ==> G',
               '(B & C) ==> F',
               '(A & B) ==> D',
               '(E & F) ==> H',
               '(H & I) ==>J',
               'A', 'B', 'C']:
    definite_clauses_KB.tell(expr(clause))
definite_clauses_KB.ask_generator(expr('F'))
# kb.ask_generator(expr(asks[0]))