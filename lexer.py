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
def t_REAL(t):
    r'\b\d+\.\d+\b'
    print(f"Token REAL: Identificador='{t.type}', Valor='{t.value}', Línea='{t.lineno}', Columna='{t.lexpos + 1}'")
    return t

def t_ENTERO(t):
    r'\b\d+\b'
    print(f"Token ENTERO: Identificador='{t.type}', Valor='{t.value}', Línea='{t.lineno}', Columna='{t.lexpos + 1}'")
    return t

def t_PALABRA_CLAVE(t):
    r'\b(if|else|do|while|switch|case|break|for|int|double|main|then|end|return|float|cin|cout)\b'
    print(f"Token PALABRA_CLAVE: Identificador='{t.type}', Valor='{t.value}', Línea='{t.lineno}', Columna='{t.lexpos + 1}'")
    return t

def t_OPERADOR_LOGICO(t):
    r'\b(and|or)\b'
    print(f"Token OPERADOR_LOGICO: Identificador='{t.type}', Valor='{t.value}', Línea='{t.lineno}', Columna='{t.lexpos + 1}'")
    return t

def t_IDENTIFICADOR(t):
    r'\b[a-zA-Z_]\w*\b'
    print(f"Token IDENTIFICADOR: Identificador='{t.type}', Valor='{t.value}', Línea='{t.lineno}', Columna='{t.lexpos + 1}'")
    return t

def t_OPERADOR_ARITMETICO(t):
    r'[\+\-\*/%^]'
    print(f"Token OPERADOR_ARITMETICO: Identificador='{t.type}', Valor='{t.value}', Línea='{t.lineno}', Columna='{t.lexpos + 1}'")
    return t

def t_OPERADOR_RELACIONAL(t):
    r'(<=|>=|!=|==|<|>)'
    print(f"Token OPERADOR_RELACIONAL: Identificador='{t.type}', Valor='{t.value}', Línea='{t.lineno}', Columna='{t.lexpos + 1}'")
    return t

def t_SIMBOLO(t):
    r'[\{\}\(\),;]'
    print(f"Token SIMBOLO: Identificador='{t.type}', Valor='{t.value}', Línea='{t.lineno}', Columna='{t.lexpos + 1}'")
    return t

def t_ASIGNACION(t):
    r'='
    print(f"Token ASIGNACION: Identificador='{t.type}', Valor='{t.value}', Línea='{t.lineno}', Columna='{t.lexpos + 1}'")
    return t

def t_COMENTARIO(t):
    r'°°.*'
    print(f"Token COMENTARIO: Identificador='{t.type}', Valor='{t.value}', Línea='{t.lineno}', Columna='{t.lexpos + 1}'")
    return t

def t_COMENTARIO_MULTILINEA(t):
    r'°\*(.|\n)*?\*°'
    t.lexer.lineno += t.value.count('\n')  # Contar líneas en comentarios multilínea
    print(f"Token COMENTARIO_MULTILINEA: Identificador='{t.type}', Valor='{t.value}', Línea='{t.lineno}', Columna='{t.lexpos + 1}'")
    return t

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


# Ignorar espacios en blanco y saltos de línea
t_ignore = ' \t\n'

# Construir el lexer
lexer = lex.lex()


# # Definición de tokens
# t_ENTERO = r'\b\d+\b'
# t_REAL = r'\b\d+\.\d+\b'
# t_IDENTIFICADOR = r'\b[a-zA-Z_]\w*\b'
# t_OPERADOR_ARITMETICO = r'[\+\-\*/%^]'
# t_OPERADOR_RELACIONAL = r'(<=|>=|!=|==|<|>)'
# t_PALABRA_CLAVE = r'\b(if|else|do|while|switch|case|break|for|int|double|main|then|end|return|float|cin|cout)\b'
# t_SIMBOLO = r'[\{\}\(\),;]'
# t_ASIGNACION = r'='

# def t_OPERADOR_LOGICO(t):
#     r'\b(and|or)\b'
#     return t

# # Token para comentario de una línea
# def t_COMENTARIO(t):
#     r'°°.*'
#     return t

# # Token para comentario multilínea
# def t_COMENTARIO_MULTILINEA(t):
#     r'°\*(.|\n)*?\*°'
#     t.lexer.lineno += t.value.count('\n')  # Contar líneas en comentarios multilínea
#     return t
    
# # Ignorar espacios en blanco y saltos de línea
# t_ignore = ' \t\n'

# # Manejo de errores
# def t_error(t):
#     print(f"Illegal character '{t.value[0]}'")
#     t.lexer.skip(1)

# # Construir el lexer
# lexer = lex.lex()
