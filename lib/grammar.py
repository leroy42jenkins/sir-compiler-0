import re

# keywords
##########

# procedures
PRO_ID = 'pro'
PRO_RET = 'ret'
PRO_VAR_CALL = '!'

# static memory
MEM_ID = 'mem'
MEM_LEFT_BRACE = '{'
MEM_RIGHT_BRACE = '}'

# pointers
POINT_LEFT_BRACKET = '['
POINT_RIGHT_BRACKET = ']'

# jump
JUMP = 'jump'

# conditional jumps
JIL = 'jil'
JILE = 'jile'
JIE = 'jie'
JIN = 'jin'
JIGE = 'jige'
JIG = 'jig'

# assignment
ASSIGN = '='

# unary operators
NOT = 'not'

# binary operators
OR = 'or'
AND = 'and'
XOR = 'xor'
ADD = 'add'
SUB = 'sub'
MUL = 'mul'
DIV = 'div'
MOD = 'mod'

# assistant constants
#####################

SEPARATOR = '\n'
INT = 'INT'
CHAR = 'CHAR'
STRING = 'STRING'

# assistant sets
################

BRA_SET = {
    MEM_LEFT_BRACE, MEM_RIGHT_BRACE,
    POINT_LEFT_BRACKET, POINT_RIGHT_BRACKET
}

UNOP_SET = {
    NOT
}

BINOP_SET = {
    OR, AND, XOR, ADD, SUB, MUL, DIV, MOD
}

CO_JUMP_SET = { 
    JIL, JILE, JIE, JIN, JIGE, JIG
}

# description
#############

DESCRIPTION_SYNTAX = f"""
Syntax:
    
    procedures:
        {PRO_ID} >> define name
        {PRO_RET} >> return value
        {PRO_VAR_CALL} >> call procedure

    tatic memory:
        {MEM_ID} >> define name
        {MEM_LEFT_BRACE} >> left brace
        {MEM_RIGHT_BRACE} >> right brace
    
    pointers:
        {POINT_LEFT_BRACKET} >> left bracket
        {POINT_RIGHT_BRACKET} >> right bracket
    
    unconditional jump:
        {JUMP}
    
    conditional jumps:
        {JIL} >> less than
        {JILE} >> less than or equal to
        {JIE} >> equal to
        {JIN} >> not equal to
        {JIGE} >> greater than or equal to
        {JIG} >> greater than
    
    assignment:
        {ASSIGN} >> set a variable 
    
    unary operators:
        {NOT} >> logical not
    
    binary operators:
        {OR} >> logical or
        {AND} >> logical and
        {XOR} >> logical exclusive or
        {ADD} >> add integers
        {SUB} >> subtract integers
        {MUL} >> multiply integers
        {DIV} >> divide integers
        {MOD} >> modulus of integers
"""

DESCRIPTION_EXAMPLES = f"""
Examples:

    pro simple_inc x0
        x1 = add x0 1
        ret x1

    pro simple_inc_test x0
        x1 = simple_inc x0
        ret x1

    pro swap_chars x0 x1
        x2 = [x0]
        x3 = [x1]
        [x0] = x3b
        [x1] = x2b
        ret 0

    pro reverse_char_array x0 x1
        @begin
        jige x0 x1 @end
        x2 = [x0]
        x3 = [x1]
        [x0] = x3b
        [x1] = x2b
        x0 = add x0 1
        x1 = sub x1 1
        jump @begin
        @end
        ret 0

    mem internal_ar {{1 2 3}}

    pro sum_internal_ar x0
        x1 = internal_ar
        x2 = add x1 16
        x3 = 0
        @begin
        jig x1 x2 @end
        x4 = [x1]
        x3 = add x3 x4
        x1 = add x1 8
        jump @begin
        @end
        ret x3
"""

#
# helpers
#

def isUnescapedEnd(source, i, c):
    if source[i] != c:
        return False
    
    i -= 1
    count = 0
    while (i >= 0 and source[i] == '\\'):
        i -= 1
        count += 1

    return count % 2 == 0

def isStringStart(source, i):
    return source[i] == '"'

def isStringStop(source, i):
    return isUnescapedEnd(source, i, '"')

def isCommentStart(source, i):
    return source[i] == '#'

def isCommentStop(source, i):
    return isUnescapedEnd(source, i, '\n')

def isSeparator(source, i):
    c = source[i]
    return c == '\n'

def isWhiteSpace(source, i):
    c = source[i]
    return c == ' ' or c == '\t'

def isCharToSkip(source, i):
    c = source[i]
    return c == '\r'

def isBra(source, i):
    c = source[i]
    return c in BRA_SET

# string functions
##################

def isInt(st):
    i = st
    if i.startswith('-'):
        i = i[1:]
    
    return i.isdigit()

def isHexInt(st):
    res = re.search('^[0][xX][0-9a-fA-F]+$', st)
    return res != None and res.start() == 0

def isChar(st):
    return len(st) >= 2 and st.startswith("'") and st.endswith("'")

def isString(st):
    return len(st) >= 2 and st.startswith('"') and st.endswith('"')

def isVar(st):
    res = re.search('^[x][0-9]+[bwd]{0,1}$', st)
    return res != None and res.start() == 0

def isUnOp(st):
    return st in UNOP_SET

def isBinOp(st):
    return st in BINOP_SET

def isLabel(st):
    return len(st) > 2 and st.startswith('@')

def isJump(st):
    return st == JUMP

def isCoJump(st):
    return st in CO_JUMP_SET

def getVarComponents(st):
    if st[-1] == 'b':
        return st[:-1], 1
    elif st[-1] == 'w':
        return st[:-1], 2
    elif st[-1] == 'd':
        return st[:-1], 4
    else:
        return st, 8
