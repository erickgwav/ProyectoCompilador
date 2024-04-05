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
    print(f"ERROR. Caracter desconocido: '{t.value[0]}'")
    t.lexer.skip(1)


# Ignorar espacios en blanco y saltos de línea
t_ignore = ' \t\n'

# Construir el lexer
lexer = lex.lex()