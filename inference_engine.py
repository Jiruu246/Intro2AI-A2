from utils import extend, Expr
from collections import defaultdict, deque
from expr_utils import conjuncts, is_prop_symbol, variables, prop_symbols, pl_true

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
    agenda = set([s for s in kb.clauses if is_prop_symbol(s.op)])
    return or_search(kb, q, [], agenda), [str(symbol).lower() for symbol in list(agenda) + [q]]

def or_search(kb, q: Expr, goals, agenda) -> bool:
    if q in agenda:
        return True
    if q in goals:
        return False
    for clause in kb.clauses_with_conclusion(q):
        result = and_search(kb, conjuncts(clause.args[0]), goals.copy() + [q], agenda)
        if result:
            return True
    return False

def and_search(kb, premise: list[Expr], goals, agenda) -> bool:
    for p in premise:
        result = or_search(kb, p, goals, agenda)
        if result:
            agenda.add(p)
        else:
            return False
    return True