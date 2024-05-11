from KB import PropDefiniteKB, PropKB
from kb_parser import parse_kb
from inference_engine import foward_chaining, DPLL_Search, tt_entails
from expr_utils import expr

tells, ask = parse_kb('tests/test_genericKB.txt')
print(tells)
print(ask)
kb = PropKB()
for sentence in tells:
    kb.tell(sentence)
# print(kb.ask_generator_fc(ask))
# print(kb.ask_generator_bc(ask))
print(DPLL_Search(kb.clauses, ask))
# print(tt_entails(kb.clauses, expr(ask.upper())))