from KB import PropDefiniteKB
from kb_parser import parse_kb
from inference_engine import foward_chaining

tells, ask = parse_kb('tests/test_HornKB.txt')
print(tells)
print(ask)
kb = PropDefiniteKB()
for st_expr in tells:
    kb.tell(st_expr)
print(kb.ask_generator_fc(ask))
print(kb.ask_generator_bc(ask))