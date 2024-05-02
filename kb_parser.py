from utils import Expr, expr
from expr_utils import expr_handle_infix_imp

def parse_kb(filename) -> tuple[list[Expr], Expr]: 
    tells = []
    ask = None
    action = None
    with open(filename, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            if line.strip() == 'TELL':
                action = 'TELL'
            elif line.strip() == 'ASK':
                action = 'ASK'
            else:
                if action is None:
                    raise ValueError('Invalid action')
                if action == 'TELL':
                    # format the implication operator and make format the propositional symbol
                    # only apply to PropKB
                    tells.extend([expr(expr_handle_infix_imp(clause.upper())) for clause in list(filter(None, line.strip().split(';')))])
                elif action == 'ASK':
                    ask = expr(line.strip().upper())
                    
    return (tells, ask)