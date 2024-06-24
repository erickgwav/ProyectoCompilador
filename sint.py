import ply.yacc as yacc
from lexer import tokens

def p_program(p):
    'program : MAIN LBRACE list_declaration RBRACE'
    p[0] = ('program', p[3])

def p_list_declaration(p):
    '''list_declaration : list_declaration declaration
                        | declaration'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_declaration(p):
    '''declaration : variable_declaration
                   | list_sentences'''
    p[0] = p[1]

def p_variable_declaration(p):
    'variable_declaration : type identifier SEMICLN'
    p[0] = ('variable_declaration', p[1], p[2])

def p_identifier(p):
    '''identifier : identifier COMMA IDENT
                  | IDENT'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_type(p):
    '''type : INTEGER
            | REAL'''
    p[0] = p[1]

def p_list_sentences(p):
    '''list_sentences : list_sentences sentence 
                      | sentence
                      | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_sentence(p):
    '''sentence : selection 
                | iteration
                | repeat
                | sent_in
                | sent_out
                | assign'''
    p[0] = p[1]

def p_assign(p):
    'assign : IDENT ASSIGN sent_expression'
    p[0] = ('assign', p[1], p[3])

def p_sent_expression(p):
    '''sent_expression : expression SEMICLN
                       | SEMICLN'''
    if len(p) == 3:
        p[0] = p[1]
    else:
        p[0] = None

def p_selection(p):
    '''selection : IF expression DO list_sentences END
                 | IF expression DO list_sentences ELSE list_sentences END'''
    if len(p) == 6:
        p[0] = ('if', p[2], p[4])
    else:
        p[0] = ('if-else', p[2], p[4], p[6])

def p_iteration(p):
    'iteration : WHILE expression DO list_sentences END'
    p[0] = ('while', p[2], p[4])

def p_repeat(p):
    'repeat : DO list_sentences WHILE expression'
    p[0] = ('do-while', p[2], p[4])

def p_sent_in(p):
    'sent_in : CIN identifier SEMICLN'
    p[0] = ('cin', p[2])

def p_sent_out(p):
    'sent_out : COUT expression SEMICLN'
    p[0] = ('cout', p[2])

def p_expression(p):
    '''expression : simple_expression relation_op simple_expression
                  | simple_expression'''
    if len(p) == 4:
        p[0] = ('relation', p[1], p[2], p[3])
    else:
        p[0] = p[1]

def p_relation_op(p):
    '''relation_op : MORETHAN
                   | LESSTHAN
                   | MOREEQUALS
                   | LESSEQUALS
                   | EQUALS
                   | NOTEQUALS'''
    p[0] = p[1]

def p_simple_expression(p):
    '''simple_expression : simple_expression first_op term
                         | term'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_first_op(p):
    '''first_op : PLUS
                | MINUS'''
    p[0] = p[1]

def p_term(p):
    '''term : term sec_op factor
            | factor'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_sec_op(p):
    '''sec_op : MULT
              | DIVIDE
              | MOD'''
    p[0] = p[1]

def p_factor(p):
    '''factor : factor third_op component
              | component'''
    if len(p) == 4:
        p[0] = ('pot', p[1], p[3])
    else:
        p[0] = p[1]

def p_third_op(p):
    'third_op : POT'
    p[0] = p[1]

def p_component(p):
    '''component : LPARENT expression RPARENT
                 | INT
                 | FLOAT
                 | IDENT'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_empty(p):
    'empty :'
    p[0] = []

def p_error(p):
    if p:
        print(f"Syntax error in '{p.value}', line '{p.lineno}', {p}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()