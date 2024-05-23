import csv, os
from iengine import extract_input_file
from KB_algo import PropKB, PropDefiniteKB
from utils import expr

""""This file is used for running the batch of test files in 1 go."""

METHODS = ['TT', 'DPLL', 'BC', 'FC']

content = ''
content = 'No; test case;' + '; '.join(METHODS) + '\n'

for root, dirs, files in os.walk('tests/'):
    for index, file in enumerate(files):
        line = str(index + 1) + '; '
        if file.endswith('.txt'):
            file_path = os.path.join(root, file)
            line += file_path + '; '
            tells, ask = extract_input_file(file_path)
            result = []
            for method in METHODS:
                kb = None               
                if ('generic' in file_path.lower()) and (method not in ['TT', 'DPLL']):
                        result.append('N/A')
                        continue
                
                if method in ['TT', 'DPLL']:
                    kb = PropKB()
                elif method in ['FC', 'BC']:
                    kb = PropDefiniteKB()
                else:
                    raise ValueError("Invalid KB type or method not compatible with KB type.")
                for tell in tells:
                    kb.tell(expr(tell))

                if (method == 'TT'):
                    entailment = kb.ask_generator_tt(expr(ask))
                elif (method == 'BC'):
                    assert(isinstance(kb, PropDefiniteKB))
                    entailment = kb.ask_generator_bc(expr(ask))
                elif (method == 'FC'):
                    assert(isinstance(kb, PropDefiniteKB))
                    entailment = kb.ask_generator_fc(expr(ask))
                elif (method == 'DPLL'):
                    entailment = kb.ask_generator_dpll(expr(ask))
                else:
                    raise ValueError("Invalid method")

                result.append('YES' if entailment[0] else 'NO')
                if result[-1] == 'YES' or method == 'DPLL':
                    if entailment[1]:
                        result[-1] += f': {str(entailment[1]).lower()}'
            line += ';'.join(result) + '\n'
        
        content += line

# Split the content into rows
rows = content.split('\n')

# Open the CSV file for writing
with open('test_results.csv', 'w', newline='') as f:
    # Create a CSV writer object with a semicolon delimiter
    writer = csv.writer(f, delimiter=';')
    
    # Iterate over the rows
    for row in rows:
        # Strip leading and trailing whitespace from the row and split each row into columns
        writer.writerow(row.strip().split(';'))