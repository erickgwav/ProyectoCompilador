import ply.lex as lex

# Lista de tokens
tokens = [
    'ENTERO',
    'REAL',
    'PALABRA_CLAVE',
    'IDENTIFICADOR',
    'OPERADOR_ARITMETICO',
    'OPERADOR_RELACIONAL',
    'OPERADOR_LOGICO',  
    'SIMBOLO',          
    'ASIGNACION',
    'COMENTARIO',
    'COMENTARIO_MULTILINEA',
]

# Definición de tokens

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)  # Incrementar el contador de línea en función del número de saltos de línea
    t.lexer.lexpos = 0

def t_REAL(t):
    r'\b\d+\.\d+\b'
    return t

def t_ENTERO(t):
    r'\b\d+\b'
    return t

def t_PALABRA_CLAVE(t):
    r'\b(if|else|do|while|switch|case|break|for|int|double|main|then|end|return|float|cin|cout)\b'
    return t

def t_OPERADOR_LOGICO(t):
    r'\b(and|or)\b'
    return t

def t_IDENTIFICADOR(t):
    r'\b[a-zA-Z_]\w*\b'
    return t

def t_OPERADOR_ARITMETICO(t):
    r'[\+\-\*/%^]'
    return t

def t_OPERADOR_RELACIONAL(t):
    r'(<=|>=|!=|==|<|>)'
    return t

def t_SIMBOLO(t):
    r'[\{\}\(\),;]'
    return t

def t_ASIGNACION(t):
    r'='
    return t

def t_COMENTARIO(t):
    r'°°.*'
    return t

def t_COMENTARIO_MULTILINEA(t):
    r'°\*(.|\n)*?\*°'
    t.lexer.lineno += t.value.count('\n')  # Contar líneas en comentarios multilínea
    return t

def t_error(t):
    # Obtener la posición del token incorrecto
    position = t.lexpos
    
    # Contar el número de saltos de línea antes de la posición actual
    line_number = t.lexer.lexdata.count('\n', 0, position) + 1
    
    # Calcular la columna contando los caracteres desde el último salto de línea hasta la posición actual
    last_line_start = t.lexer.lexdata.rfind('\n', 0, position)
    if last_line_start < 0:
        last_line_start = 0
    column_number = position - last_line_start
    
    # Imprimir el error con el número de línea y columna
    print(f"Error en la línea {line_number}, columna {column_number}: Caracter inesperado '{t.value[0]}'")
    
    # Saltar al siguiente carácter para continuar el análisis
    t.lexer.skip(1)


# Ignorar espacios en blanco y saltos de línea
t_ignore = ' \t\n'

# Construir el lexer
lexer = lex.lex()