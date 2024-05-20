"""
Representations and Inference for Logic.

Covers both Propositional and First-Order Logic. First we have four
important data types:

    KB            Abstract class holds a knowledge base of logical expressions
    KB_Agent      Abstract class subclasses agents.Agent
    Expr          A logical expression, imported from utils.py

Be careful: some functions take an Expr as argument, and some take a KB.

Logical expressions can be created with Expr or expr, imported from utils, TODO
or with expr, which adds the capability to write a string that uses
the connectives ==>, <==, <=>, or <=/=>. But be careful: these have the
operator precedence of commas; you may need to add parens to make precedence work.
See logic.ipynb for examples.

Then we implement various functions for doing logical inference:

    pl_true          Evaluate a propositional logical sentence in a model
    tt_entails       Say if a statement is entailed by a KB
    fc
    bc
"""
from collections import defaultdict
from utils import remove_all, unique, first, Expr, subexpressions, extend
from parser_utils import *

class KB:
    """A knowledge base to which you can tell and ask sentences.
    To create a KB, first subclass this class and implement
    tell, ask_generator, and retract. Why ask_generator instead of ask?
    The book is a bit vague on what ask means --
    For a Propositional Logic KB, ask(P & Q) returns True or False, but for an
    FOL KB, something like ask(Brother(x, y)) might return many substitutions
    such as {x: Cain, y: Abel}, {x: Abel, y: Cain}, {x: George, y: Jeb}, etc.
    So ask_generator generates these one at a time, and ask either returns the
    first one or returns False."""

    def __init__(self, sentence=None):
        if sentence:
            self.tell(sentence)

    def tell(self, sentence):
        """Add the sentence to the KB."""
        raise NotImplementedError

    def ask(self, query):
        """Return a substitution that makes the query true, or, failing that, return False."""
        return first(self.ask_generator(query), default=False)

    def ask_generator(self, query):
        """Yield all the substitutions that make query true."""
        raise NotImplementedError

    def retract(self, sentence):
        """Remove sentence from the KB."""
        raise NotImplementedError


class PropKB(KB):
    """A KB for propositional logic. Inefficient, with no indexing."""

    def __init__(self, sentence=None):
        super().__init__(sentence)
        self.clauses = []

    def tell(self, sentence):
        """Add the sentence's clauses to the KB."""
        self.clauses.extend(conjuncts(to_cnf(sentence)))

    def ask_generator_tt(self, query):
        """Yield the empty substitution {} if KB entails query; else no results."""
        return tt_entails(Expr('&', *self.clauses), query)
    
    def ask_generator_dpll(self, query):
        return dpll_entails(self.clauses, query)

    def retract(self, sentence):
        """Remove the sentence's clauses from the KB."""
        for c in conjuncts(to_cnf(sentence)):
            if c in self.clauses:
                self.clauses.remove(c)

# ______________________________________________________________________________


def is_symbol(s):
    """A string s is a symbol if it starts with an alphabetic char.
    >>> is_symbol('R2D2')
    True
    """
    return isinstance(s, str) and s[:1].isalpha()


def is_var_symbol(s):
    """A logic variable symbol is an initial-lowercase string.
    >>> is_var_symbol('EXE')
    False
    """
    return is_symbol(s) and s[0].islower()


def is_prop_symbol(s):
    """A proposition logic symbol is an initial-uppercase string.
    >>> is_prop_symbol('exe')
    False
    """
    return is_symbol(s) and s[0].isupper()


def is_variable(x):
    """A variable is an Expr with no args and a lowercase symbol as the op."""
    return isinstance(x, Expr) and not x.args and x.op[0].islower()

def variables(s):
    """Return a set of the variables in expression s.
    >>> variables(expr('F(x, x) & G(x, y) & H(y, z) & R(A, z, 2)')) == {x, y, z}
    True
    """
    return {x for x in subexpressions(s) if is_variable(x)}


def is_definite_clause(s):
    """Returns True for exprs s of the form A & B & ... & C ==> D,
    where all literals are positive. In clause form, this is
    ~A | ~B | ... | ~C | D, where exactly one clause is positive.
    >>> is_definite_clause(expr('Farmer(Mac)'))
    True
    """
    if is_symbol(s.op):
        return True
    elif s.op == '==>':
        antecedent, consequent = s.args
        return is_symbol(consequent.op) and all(is_symbol(arg.op) for arg in conjuncts(antecedent))
    else:
        return False

# ______________________________________________________________________________

def tt_entails(kb, alpha):
    """
    [Figure 7.10]
    Does kb entail the sentence alpha? Use truth tables. For propositional
    kb's and sentences. Note that the 'kb' should be an Expr which is a
    conjunction of clauses.
    >>> tt_entails(expr('P & Q'), expr('Q'))
    True
    """
    number_of_kb_models = 0
    def increase_counter():
        nonlocal number_of_kb_models
        number_of_kb_models += 1

    assert not variables(alpha)
    symbols = list(prop_symbols(kb & alpha))
    return (tt_check_all(kb, alpha, symbols, {}, increase_counter), number_of_kb_models)


def tt_check_all(kb, alpha, symbols, model, increment):
    """Auxiliary routine to implement tt_entails."""
    if not symbols:
        if pl_true(kb, model):
            result = pl_true(alpha, model)
            assert result in (True, False)
            if result:
                increment()
            return result
        else:
            return True
    else:
        P, rest = symbols[0], symbols[1:]
        return (tt_check_all(kb, alpha, rest, extend(model, P, True), increment) and
                tt_check_all(kb, alpha, rest, extend(model, P, False), increment))


def prop_symbols(x):
    """Return the set of all propositional symbols in x."""
    if not isinstance(x, Expr):
        return set()
    elif is_prop_symbol(x.op):
        return {x}
    else:
        return {symbol for arg in x.args for symbol in prop_symbols(arg)}


def pl_true(exp, model={}):
    """Return True if the propositional logic expression is true in the model,
    and False if it is false. If the model does not specify the value for
    every proposition, this may return None to indicate 'not obvious';
    this may happen even when the expression is tautological.
    >>> pl_true(P, {}) is None
    True
    """
    if exp in (True, False):
        return exp
    op, args = exp.op, exp.args
    if is_prop_symbol(op):
        return model.get(exp)
    elif op == '~':
        p = pl_true(args[0], model)
        if p is None:
            return None
        else:
            return not p
    elif op == '|':
        result = False
        for arg in args:
            p = pl_true(arg, model)
            if p is True:
                return True
            if p is None:
                result = None
        return result
    elif op == '&':
        result = True
        for arg in args:
            p = pl_true(arg, model)
            if p is False:
                return False
            if p is None:
                result = None
        return result
    p, q = args
    if op == '==>':
        return pl_true(~p | q, model)

    pt = pl_true(p, model)
    if pt is None:
        return None
    qt = pl_true(q, model)
    if qt is None:
        return None
    if op == '<=>':
        return pt == qt
    else:
        raise ValueError('Illegal operator in logic expression' + str(exp))

# ______________________________________________________________________________


def pl_resolution(kb, alpha): #TODO: Delele this
    """
    [Figure 7.12]
    Propositional-logic resolution: say if alpha follows from KB.
    >>> pl_resolution(horn_clauses_KB, A)
    True
    """
    clauses = kb.clauses + conjuncts(to_cnf(~alpha))
    new = set()
    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j])
                 for i in range(n) for j in range(i + 1, n)]
        for (ci, cj) in pairs:
            resolvents = pl_resolve(ci, cj)
            if False in resolvents:
                return True
            new = new.union(set(resolvents))
        if new.issubset(set(clauses)):
            return False
        for c in new:
            if c not in clauses:
                clauses.append(c)


def pl_resolve(ci, cj):
    """Return all clauses that can be obtained by resolving clauses ci and cj."""
    clauses = []
    for di in disjuncts(ci):
        for dj in disjuncts(cj):
            if di == ~dj or ~di == dj:
                clauses.append(associate('|', unique(remove_all(di, disjuncts(ci)) + remove_all(dj, disjuncts(cj)))))
    return clauses


# ______________________________________________________________________________


class PropDefiniteKB(PropKB):
    """A KB of propositional definite clauses."""

    def tell(self, sentence):
        """Add a definite clause to this KB."""
        assert is_definite_clause(sentence), "Must be definite clause"
        self.clauses.append(sentence)

    def ask_generator_fc(self, query):
        return pl_fc_entails(self, query)
    
    def ask_generator_bc(self, query):
        return pl_bc_entails(self, query)

    def retract(self, sentence):
        self.clauses.remove(sentence)

    def clauses_with_premise(self, p):
        """Return a list of the clauses in KB that have p in their premise."""
        return [c for c in self.clauses if c.op == '==>' and p in conjuncts(c.args[0])]
    
    def clauses_with_conclusion(self, con):
        "Return a list of the clauses in KB that have con as the conclusion."
        return [c for c in self.clauses if c.op == '==>' and con == c.args[1]]
    

def pl_fc_entails(kb, q: Expr) -> tuple[bool, list]:
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
    return False, None

def pl_bc_entails(kb, q):
    """
    Use backward chaining to see if a PropDefiniteKB entails symbol q.
    """
    inferred = {s for s in kb.clauses if is_prop_symbol(s.op)}
    failed = set()
    entailments = {q}

    def backward_chaining_check(symbol, goal):
        nonlocal inferred, failed, entailments
        if symbol in inferred:
            return True
        if (symbol in failed) or (symbol in goal):
            return False
        
        goal.append(symbol)
        for c in kb.clauses_with_conclusion(symbol):
            result = True
            sub_goals = []
            for p in conjuncts(c.args[0]):
                sub_goals.append(p)
                result = result and backward_chaining_check(p, goal)
                if not result:
                    break
            if result == True:
                entailments.update(sub_goals)
                inferred.add(symbol)
                return True
        failed.add(symbol)
        return False
    
    return (backward_chaining_check(q, []), entailments)

def dpll_entails(KB, q) -> tuple[bool, dict]: 
    sentence = to_cnf(Expr('&', *KB) & ~expr(q))
    symbols = list(prop_symbols(sentence))
    satisfy, model = DPLL(sentence, symbols, {})
    return not satisfy, model
    
def DPLL(sentence, symbols, model) -> tuple[bool, dict|None]:
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