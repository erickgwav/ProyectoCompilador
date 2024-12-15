import ply.lex as lex
from sem import SemanticAnalyzer

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'do': 'DO',
    'then': 'THEN',
    'end': 'END',
    'switch': 'SWITCH',
    'case': 'CASE',
    'int': 'INT',
    'double': 'DOUBLE',
    'main': 'MAIN',
    'cin': 'CIN',
    'cout': 'COUT',
    'while': 'WHILE',
    'until': 'UNTIL',
    'and': 'AND',
    'or': 'OR'
}

tokens = [
    'COMENTARIO',
    'IDENTIFICADOR',
    'DOUBLE',
    'INT',
    'SHAFT',
    'COMMA',
    'UNDERSCORE',
    'NOT',
    'LPARENT',
    'RPARENT',
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'PIPE',
    'INC',
    'DEC',
    'MAS',
    'MENOS',
    'ENTRE',
    'POR',
    'MOD',
    'POT',
    'ASSIGN',
    'MORETHAN',
    'LESSTHAN',
    'MOREEQUALS',
    'LESSEQUALS',
    'EQUALS',
    'NOTEQUALS',
    'AND',
    'OR',
    'SEMICOLON',
    'STRING'
] + list(reserved.values())

states = (
    ('double','exclusive'),
    ('deletedot','exclusive'),
)

t_SHAFT = r'°'
t_COMMA = r','
t_UNDERSCORE = r'_'
t_NOT = r'!'
t_LPARENT = r'\('
t_RPARENT = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_PIPE = r'\|'
t_INC = r'\+\+'
t_DEC = r'--'
t_MAS = r'\+'
t_MENOS = r'-'
t_ENTRE = r'/'
t_POR = r'\*'
t_MOD = r'%'
t_POT = r'\^'
t_ASSIGN = r'='
t_MORETHAN = r'>'
t_LESSTHAN = r'<'
t_MOREEQUALS = r'>='
t_LESSEQUALS = r'<='
t_EQUALS = r'=='
t_NOTEQUALS = r'!='
t_AND = r'and'
t_OR = r'or'
t_SEMICOLON = r';'
t_STRING = r'\"[^\"]*\"'

def t_COMENTARIO(t):
    r'(\°\*(.|\n)*?\*\°)|(\°.*)'
    pass
    return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'IDENTIFICADOR')
    if t.type == 'IDENTIFICADOR':
        if not t.value in SemanticAnalyzer.return_symbol_table(SemanticAnalyzer):
            SemanticAnalyzer.add_to_temp_symbol_table(t.value, t.lexer.lineno)
    return t

def t_double(t):
    r'\d+\.'
    t.lexer.code_start = t.lexer.lexpos  - len(t.value)
    if t.lexer.lexdata[t.lexer.code_start - 1].isdigit() or t.lexer.lexdata[t.lexer.code_start - 1].isalpha():
        t.value = t.lexer.lexdata[t.lexer.code_start]
        t.type = 'MENOS'
        t.lexer.lexpos = t.lexer.code_start + 1
        t.lexer.begin('INITIAL')
        return t
    t.lexer.begin('double')

def t_double_isdouble(t):
    r'\d+'
    t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos]
    t.type = "DOUBLE"
    t.lexpos = t.lexer.code_start
    t.lexer.begin('INITIAL')
    return t

def t_double_error(t):
    t.lexer.skip(-1)
    t.value = "Ilegal character at '%s' in line %d column %d" % (t.value[0], t.lexer.lineno, t.lexer.lexpos + 1)
    t.lexer.begin('deletedot')
    return t

def t_deletedot_delete(t):
    r'\.'
    pass
    t.lexer.begin('INITIAL')

def t_INT(t):
    r'-?\d+'
    t.lexer.code_start = t.lexer.lexpos  - len(t.value)
    if t.lexer.lexdata[t.lexer.code_start - 1].isdigit() or t.lexer.lexdata[t.lexer.code_start - 1].isalpha():
        t.value = t.lexer.lexdata[t.lexer.code_start]
        t.type = 'MENOS'
        t.lexer.lexpos = t.lexer.code_start + 1
        t.lexer.begin('INITIAL')
        return t
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += 1

def t_error(t):
    t.lexer.skip(1)
    t.value = "Ilegal character at '%s' in line %d column %d" % (t.value[0], t.lexer.lineno, t.lexer.lexpos + 1)
    return t

def t_eof(t):
    t.lexer.lineno = 1
    pass

t_ignore = " \t"

lexer = lex.lex()