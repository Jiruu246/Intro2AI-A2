from KB_algo import PropKB, PropDefiniteKB
import sys
from utils import expr
import re

# ______________________________________________________________________________

infix_or = '||'
infix_imp = '=>'

def expr_handle_infix(x):
    return re.sub(r"(?<!<)" + infix_imp, '==>', x.replace(infix_or, '|'))

# ______________________________________________________________________________

# Read input from file
def extract_input_file(filename):
    with open(filename, "r") as file:
        input_text = expr_handle_infix(file.read().upper())

    # Extracting TELL and ASK statements
    tell_start = input_text.find("TELL")
    ask_start = input_text.find("ASK")

    tell_section = input_text[tell_start+len("TELL"):ask_start].strip()
    tell_statements = [statement.strip() for statement in tell_section.split(';') if statement.strip()]
    ask_statement = input_text[ask_start+len("ASK"):].strip()


    KB = tell_statements
    query = ask_statement

    return (KB, query)

def inference_engine():
    filename = sys.argv[1]
    method = sys.argv[2]

    (kb_sentences, query) = extract_input_file(filename)

    kb = None
    if method in ['TT', 'DPLL']:
        kb = PropKB()
    elif method in ['FC', 'BC']:
        kb = PropDefiniteKB()
    else:
        raise ValueError("Invalid KB type or method not compatible with KB type.")
    assert kb is not None

    for kb_sentence in kb_sentences:
        kb.tell(expr(kb_sentence))

    if (method == 'TT'):
        result = kb.ask_generator_tt(expr(query))
    elif (method == 'BC'):
        assert(isinstance(kb, PropDefiniteKB))
        result = kb.ask_generator_bc(expr(query))
    elif (method == 'FC'):
        assert(isinstance(kb, PropDefiniteKB))
        result = kb.ask_generator_fc(expr(query))
    elif (method == 'DPLL'):
        result = kb.ask_generator_dpll(expr(query))

    else:
        raise ValueError("Invalid method") 
    
    output = ''
    if result[0]:
        output += 'YES'
    else:
        output += 'NO'

    #This is required since DPLL will output the partial model when the query is false
    if output == 'YES' or method == 'DPLL':
        if result[1]:
            output += f': {str(result[1]).lower()}'

    print(output)

if __name__ == "__main__":
    inference_engine()

