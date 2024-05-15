from utils import extend, Expr, expr
from collections import defaultdict, deque
from expr_utils import conjuncts, disjuncts, is_prop_symbol, variables, prop_symbols, pl_true, to_cnf

def foward_chaining(kb, q: Expr) -> tuple[bool, list]:
    count = {c: len(conjuncts(c.args[0])) for c in kb.clauses if c.op == '==>'}
    inferred = defaultdict(bool)
    agenda = [s for s in kb.clauses if is_prop_symbol(s.op)]
    while agenda:
        p = agenda.pop()
        if p == q:
            return True, [str(symbol).lower() for symbol in set(agenda + list(inferred.keys()) + [p])]
        if not inferred[p]:
            inferred[p] = True
            for c in kb.clauses_with_premise(p):
                count[c] -= 1
                if count[c] == 0:
                    agenda.append(c.args[1])
                    #improve the performance by checking if the query is in the conclusion of the clause
                    if c.args[1] == q:
                        return True, [str(symbol).lower() for symbol in set(agenda + list(inferred.keys()) + [p])]
    return False, []

def tt_entails(kb, alpha):
    assert not variables(alpha)
    symbols = list(prop_symbols(kb & alpha))
    return tt_check_all(kb, alpha, symbols, {})


def tt_check_all(kb, alpha, symbols, model):
    """Auxiliary routine to implement tt_entails."""
    if not symbols:
        if pl_true(kb, model):
            result = pl_true(alpha, model)
            assert result in (True, False)
            return result
        else:
            return True
    else:
        P, rest = symbols[0], symbols[1:]
        return (tt_check_all(kb, alpha, rest, extend(model, P, True)) and
                tt_check_all(kb, alpha, rest, extend(model, P, False)))
        
def backward_chaining(kb, q: Expr) -> tuple[bool, list]:
    #improve performance
    agenda = set([s for s in kb.clauses if is_prop_symbol(s.op)])
    #improve performance
    failed = set()
    return or_search(kb, q, [], agenda, failed), [str(symbol).lower() for symbol in list(agenda) + [q]]

def or_search(kb, q: Expr, goals, agenda, failed) -> bool:
    if q in agenda:
        return True
    if q in goals or q in failed:
        return False
    for clause in kb.clauses_with_conclusion(q):
        result = and_search(kb, conjuncts(clause.args[0]), goals.copy() + [q], agenda, failed)
        if result:
            return True
    failed.add(q)
    return False

def and_search(kb, premise: list[Expr], goals, agenda, failed) -> bool:
    for p in premise:
        result = or_search(kb, p, goals, agenda, failed)
        if result:
            agenda.add(p)
        else:
            return False
    return True

def DPLL_Search(KB, q) -> tuple[bool, dict]: 
    #use set to elimiate duplicates
    sentence = to_cnf(Expr('&', *KB) & ~expr(q))
    symbols = list(prop_symbols(sentence))
    satisfy, model = DPLL(sentence, symbols, {})
    return not satisfy, model
    
def DPLL(sentence, symbols, model) -> tuple[bool, dict|None]:
    print('interation')
    #not sure if this work with partial model
    if pl_true(sentence, model) == False:
        return False, None
    
    if pl_true(sentence, model) == True:
        return True, model
    
    p, value = find_pure_symbol(sentence, symbols, model)
    if p:
        return DPLL(sentence, [s for s in symbols if s != p], extend(model, p, value))
    p, value = find_unit_clause(sentence, symbols, model)
    if p:
        return DPLL(sentence, [s for s in symbols if s != p], extend(model, p, value))
    
    p = symbols[0]
    
    branch1 = DPLL(sentence, [s for s in symbols if s != p], extend(model, p, True))
    if branch1[0]:
        return True, branch1[1]
    branch2 = DPLL(sentence, [s for s in symbols if s != p], extend(model, p, False))
    if branch2[0]:
        return True, branch2[1]
    
    return False, None
    
def find_pure_symbol(sentence, symbols, model) -> tuple[Expr, bool]:
    clauses = set(conjuncts(sentence))
    positive, negative = set(), set()
    for clause in clauses:
        if pl_true(clause, model):
            continue
        for literal in disjuncts(clause):
            if list(prop_symbols(literal))[0] not in symbols:
                continue
            if literal.op == '~':
                negative.add(literal.args[0])
            else:
                positive.add(literal)

    for p in positive:
        if p not in negative:
            return p, True
    for n in negative:
        if n not in positive:
            return n, False
    return None, None

def find_unit_clause(sentence, symbols, model) -> tuple[Expr, bool]:
    clauses = set(conjuncts(sentence))
    for clause in clauses:
        if pl_true(clause, model):
            continue
        literals = [s for s in prop_symbols(clause) if s in symbols]
        if len(literals) == 1:
            return literals[0], pl_true(clause, extend(model, literals[0], True))
    return None, None

sentence = expr('(~A | B | C) & (A | B | D) & (~A | ~C | ~D) & (B | C | D) & (B | ~C ) & (~C)')
print(DPLL(sentence, list(prop_symbols(sentence)), {}))