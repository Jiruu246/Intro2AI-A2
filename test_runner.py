import os
from iengine import extract_input_file
from KB_algo import PropKB, PropDefiniteKB
from utils import expr

METHODS = ['TT', 'DPLL', 'BC', 'FC']

for root, dirs, files in os.walk('tests/'):
    for file in files:
        if file.endswith('.txt'):
            file_path = os.path.join(root, file)
            print(file_path)
            tells, ask = extract_input_file(file_path)
            result = ''
            for method in METHODS:
                kb = None
                if 'generic' in file_path.lower():
                    if method not in ['TT', 'DPLL']:
                        result += 'N/A '
                        continue
                    kb = PropKB()
                elif 'horn' in file_path.lower():
                    kb = PropDefiniteKB()
                else:
                    raise ValueError("Invalid KB type or method not compatible with KB type.")
                for tell in tells:
                    kb.tell(expr(tell))

                if (method == 'TT'):
                    result += ('YES' if kb.ask_generator_tt(expr(ask))[0] else 'NO') + ' '
                elif (method == 'BC'):
                    assert(isinstance(kb, PropDefiniteKB))
                    result += ('YES' if kb.ask_generator_bc(expr(ask))[0] else 'NO') + ' '
                elif (method == 'FC'):
                    assert(isinstance(kb, PropDefiniteKB))
                    result += ('YES' if kb.ask_generator_fc(expr(ask))[0] else 'NO') + ' '
                elif (method == 'DPLL'):
                    result += ('YES' if kb.ask_generator_dpll(expr(ask))[0] else 'NO') + ' '
                else:
                    raise ValueError("Invalid method")
            print(result)
            

