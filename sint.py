import ply.yacc as yacc
from lexer import tokens
from sem import SemanticAnalyzer

errores_sintacticos = []

def p_programa(p):
    'programa : MAIN LBRACE lista_declaraciones RBRACE'
    p[0] = ('programa', p[3])

def p_lista_declaraciones(p):
    '''lista_declaraciones : lista_declaraciones declaracion
                        | declaracion'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_declaracion(p):
    '''declaracion : declaracion_variable
                   | lista_sentencias
                   | comentario'''
    p[0] = p[1]

def p_comentario(p):
    'comentario : COMENTARIO'
    p[0] = None

def p_declaracion_variable(p):
    'declaracion_variable : tipo identificador SEMICOLON'
    p[0] = (p[1], p[2])

def p_identificador(p):
    '''identificador : identificador COMMA IDENTIFICADOR
                  | IDENTIFICADOR'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_tipo(p):
    '''tipo : INT
            | DOUBLE'''
    p[0] = p[1]

def p_lista_sentencias(p):
    '''lista_sentencias : lista_sentencias sentencia 
                      | vacio'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_sentencia(p):
    '''sentencia : seleccion 
                | iteracion
                | repeticion
                | entrada
                | salida
                | asignacion
                | incremento
                | decremento
                | declaracion_variable'''
    p[0] = p[1]

def p_asignacion(p):
    'asignacion : IDENTIFICADOR ASSIGN expresion_finalizada'
    p[0] = (p[2], p[1], p[3])

def p_incremento(p):
    'incremento : IDENTIFICADOR INC SEMICOLON'
    p[0] = ('incremento', p[1], '+', [p[1], '1'])

def p_decremento(p):
    'decremento : IDENTIFICADOR DEC SEMICOLON'
    p[0] = ('decremento', p[1], '-', [p[1], 1])

def p_expresion_finalizada(p):
    '''expresion_finalizada : expresion SEMICOLON
                       | SEMICOLON'''
    if len(p) == 3:
        p[0] = p[1]
    else:
        p[0] = None

def p_seleccion(p):
    '''seleccion : IF expresion THEN lista_sentencias END
                 | IF expresion THEN lista_sentencias ELSE lista_sentencias END'''
    if len(p) == 6:
        p[0] = ('if', p[2], p[4])
    else:
        p[0] = ('if-else', p[2], p[4], p[6])

def p_iteracion(p):
    'iteracion : WHILE expresion DO lista_sentencias END'
    p[0] = ('while', p[2], p[4])

def p_repeticion(p):
    'repeticion : DO lista_sentencias UNTIL expresion SEMICOLON'
    p[0] = ('do-until', p[2], p[4])

def p_entrada(p):
    'entrada : CIN IDENTIFICADOR SEMICOLON'
    p[0] = ('cin', p[2])

def p_salida(p):
    'salida : COUT expresion SEMICOLON'
    p[0] = ('cout', p[2])

def p_expresion(p):
    '''expresion : expresion operador_comparacion expresion_comparacion
                 | expresion_comparacion'''
    if len(p) == 4:
        p[0] = ('comparador', p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_operador_comparacion(p):
    '''operador_comparacion : AND
                     | OR'''
    p[0] = p[1]

def p_expresion_comparacion(p):
    '''expresion_comparacion : expresion_simple operacion_relacional expresion_simple
                       | expresion_simple'''
    if len(p) == 4:
        p[0] = ('relacion', p[2], [p[1], p[3]])
    else:
        p[0] = p[1]

def p_operacion_relacional(p):
    '''operacion_relacional : MORETHAN
                   | LESSTHAN
                   | MOREEQUALS
                   | LESSEQUALS
                   | EQUALS
                   | NOTEQUALS'''
    p[0] = p[1]

def p_expresion_simple(p):
    '''expresion_simple : expresion_simple primer_operador term
                         | term'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_primer_operador(p):
    '''primer_operador : MAS
                | MENOS'''
    p[0] = p[1]

def p_term(p):
    '''term : term segundo_operador factor
            | factor'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_segundo_operador(p):
    '''segundo_operador : POR
              | ENTRE
              | MOD'''
    p[0] = p[1]

def p_factor(p):
    '''factor : factor tercer_operador componente
              | componente'''
    if len(p) == 4:
        p[0] = ('pot', p[1], p[3])
    else:
        p[0] = p[1]

def p_tercer_operador(p):
    'tercer_operador : POT'
    p[0] = p[1]

def p_componente(p):
    '''componente : LPARENT expresion RPARENT
                 | INT
                 | DOUBLE
                 | IDENTIFICADOR'''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_vacio(p):
    'vacio :'
    p[0] = []

def p_error(p):
    if p:
        error_message = f"Error de sintaxis en '{p.value}', línea {p.lineno}"
        errores_sintacticos.append(error_message)
        parser.errok()
    else:
        error_message = "Error de sintaxis en EOF"
        errores_sintacticos.append(error_message)
    
    if hasattr(parser, 'error_output') and parser.error_output is not None:
        parser.error_output.append(error_message)
    else:
        print(error_message)

def set_error_output(output_widget):
    parser.error_output = output_widget

parser = yacc.yacc()