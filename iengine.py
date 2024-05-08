from KB_algo import PropKB, PropDefiniteKB
import sys
from utils import expr

# ______________________________________________________________________________

infix_imp = '=>'

def expr_handle_infix_imp(x):
    x = x.replace(infix_imp, '==>')
    return x

infix_or = '||'

def expr_handle_infix_or(x):
    x = x.replace(infix_or, '|')
    return x

infix_biconditional = '<==>'

def expr_handle_infix_biconditional(x):
    x = x.replace(infix_biconditional, '<=>')
    return x

# ______________________________________________________________________________

# Read input from file
def extract_input_file(filename):
    with open(filename, "r") as file:
        input_text = file.read().upper()

    # Extracting TELL and ASK statements
    tell_start = input_text.find("TELL")
    ask_start = input_text.find("ASK")

    tell_section = input_text[tell_start+len("TELL"):ask_start].strip()
    tell_statements = [statement.strip() for statement in tell_section.split(';') if statement.strip()]
    ask_statement = input_text[ask_start+len("ASK"):].strip()


    KB = tell_statements
    query = ask_statement

    return (KB, query)

def TT_inference_engine(kbsentences, query):
    kb = PropKB()
    for sentence in kbsentences:
        kb.tell(expr(expr_handle_infix_biconditional(expr_handle_infix_imp(expr_handle_infix_or(sentence)))))

    return kb.ask_generator(expr(expr_handle_infix_biconditional(expr_handle_infix_imp(expr_handle_infix_or(query)))))

def BC_inference_engine(kbsentences, query):
    kb = PropDefiniteKB()

    for sentence in kbsentences:
        kb.tell(expr(expr_handle_infix_imp(sentence)))

    return kb.ask_generator_bc(expr(query))


def inference_engine():
    filename = sys.argv[1]
    method = sys.argv[2]

    (kb_sentences, query) = extract_input_file(filename)
    if (method == 'TT'):
        result = TT_inference_engine(kb_sentences, query)
    elif (method == 'BC'):
        result = BC_inference_engine(kb_sentences, query)
        for element in result[1]:
            element.op = element.op.lower() 
    
    if (result[0]):
        print('{}{}'.format('YES: ', str(result[1])))
    else:
        print('NO')

if __name__ == "__main__":
    inference_engine()

