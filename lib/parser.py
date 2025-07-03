import lib.grammar as gram
import lib.lexer as lex

#
# Parser Expression Types
#

class Exp:
    def __init__(self, name):
        self.name = name

    def toString(self):
        return self.name

class ELabel(Exp):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ ELabel: ' + self.name + ' }'

class EJump(Exp):
    def __init__(self, name, labelName):
        super().__init__(name)
        self.labelName = labelName

    def toString(self):
        return '{ EJump: ' + self.name + ' ' + self.labelName + ' }'

class ECoJump(Exp):
    def __init__(self, name, left, right, labelName):
        super().__init__(name)
        self.left = left
        self.right = right
        self.labelName = labelName

    def toString(self):
        body = self.left.toString() + ' ' + self.right.toString() + ' ' + self.labelName
        return '{ ECoJump: ' + self.name + ' ' + body + ' }'

class ECopy(Exp):
    def __init__(self, dest, source):
        super().__init__('ECopy')
        self.dest = dest
        self.source = source

    def toString(self):
        body = self.dest.toString() + ' ' + gram.ASSIGN + ' ' + self.source.toString()
        return '{ ' + self.name + ': ' + body + ' }'

class EUnOp(Exp):
    def __init__(self, dest, op, source):
        super().__init__('EUnOp')
        self.dest = dest
        self.op = op
        self.source = source

    def toString(self):
        body = self.dest.toString() + ' ' + gram.ASSIGN + ' ' + self.op + ' ' + self.source.toString()
        return '{ ' + self.name + ': ' + body + ' }'
    
class EBinOp(Exp):
    def __init__(self, dest, op, left, right):
        super().__init__('EBinOp')
        self.dest = dest
        self.op = op
        self.left = left
        self.right = right

    def toString(self):
        body = self.dest.toString() + ' ' + gram.ASSIGN + ' ' + self.op + ' ' + self.left.toString() + ' ' + self.right.toString()
        return '{ ' + self.name + ': ' + body + ' }'
    
class EProCall(Exp):
    def __init__(self, dest, id, params):
        super().__init__('EProCall')
        self.dest = dest
        self.id = id
        self.params = params

    def toString(self):
        body = self.dest.toString() + ' ' + gram.ASSIGN + ' ' + self.id

        for p in self.params:
            body += ' ' +  p.toString()
        
        return '{ ' + self.name + ': ' + body + ' }'
    
class EPro(Exp):
    def __setProperties(self):
        for p in self.params:
            if isinstance(p, lex.TVar):
                self.usesInt = True

        intRelatedTypes = [lex.TVar]

        for exp in self.expressions:
            if isinstance(exp, ECoJump):
                if isValidTokenInTypeList(exp.left, intRelatedTypes):
                    self.usesInt = True
                elif isValidTokenInTypeList(exp.right, intRelatedTypes):
                    self.usesInt = True
            elif isinstance(exp, ECopy):
                if isValidTokenInTypeList(exp.dest, intRelatedTypes):
                    self.usesInt = True
                elif isValidTokenInTypeList(exp.source, intRelatedTypes):
                    self.usesInt = True
            elif isinstance(exp, EUnOp):
                if isValidTokenInTypeList(exp.dest, intRelatedTypes):
                    self.usesInt = True
                elif isValidTokenInTypeList(exp.source, intRelatedTypes):
                    self.usesInt = True
            elif isinstance(exp, EBinOp):
                if isValidTokenInTypeList(exp.dest, intRelatedTypes):
                    self.usesInt = True
                elif isValidTokenInTypeList(exp.left, intRelatedTypes):
                    self.usesInt = True
                elif isValidTokenInTypeList(exp.right, intRelatedTypes):
                    self.usesInt = True
            elif isinstance(exp, EProCall):
                self.isLeaf = False

        if isValidTokenInTypeList(self.ret, intRelatedTypes):
            self.usesInt = True

    def __init__(self, name, params, exps, ret):
        super().__init__(name)
        self.params = params
        self.expressions = exps
        self.ret = ret
        self.isLeaf = True
        self.usesInt = False
        self.__setProperties()

    def toString(self):
        params = ''
        for p in self.params:
            params += ' ' + p.toString()

        expressions = ''
        for exp in self.expressions:
            expressions += '\t' + exp.toString() + '\n'
        
        return ''.join([
            'pro ' + self.name + params + '\n',
            '\tisLeaf: ' + str(self.isLeaf) + '\n',
            '\tusesInt: ' + str(self.usesInt) + '\n',
            expressions,
            '\tret ' + self.ret.toString() + '\n'
        ])
    
class EMemCollection(Exp):
    def __init__(self, name, collection):
        super().__init__(name)
        self.collection = collection

    def toString(self):
        collection = ''
        for c in self.collection:
            collection += '\t' + c.toString() + '\n'

        return ''.join([
            'mem ' + self.name + ' {\n',
            collection,
            '}\n'
        ])

class EMemSize(Exp):
    def __init__(self, name, size):
        super().__init__(name)
        self.size = size

    def toString(self):
        return 'mem ' + self.name + ' ' + self.size

# TODO: include multiplication and division information
class ProcedureProperties:
    def __init__(self, usesInt):
        self.usesInt = usesInt

def getProcedureProperties(pros):
    usesInt = {}

    for pro in pros:
        usesInt[pro.name] = pro.usesInt

    return ProcedureProperties(usesInt)

#
# Parser Functions
#

OP_TYPE_COPY = 0
OP_TYPE_UN_OP = 1
OP_TYPE_BIN_OP = 2
OP_TYPE_PRO_CALL = 3

RETURN_TYPES = [lex.TInt, lex.TChar, lex.TVar]
INTEGER_TYPES = [lex.TInt, lex.TChar, lex.TVar]
LITERAL_TYPES = [lex.TInt, lex.TChar, lex.TString]

def isValidTokenInTypeList(t, validTypeList):
    for v in validTypeList:
        if isinstance(t, v):
            return True
        
    return False

def getParamFromPointer(pointer):
    name = pointer.name
    if gram.isVar(name):
        n, w = gram.getVarComponents(name)
        return lex.TVar(n, w)
    
    return lex.TIdentifier(name)

def getParamsFromPossiblePointers(possibles):
    params = []

    for p in possibles:
        if isinstance(p, lex.TPointer):
            name = p.name
            if gram.isVar(name):
                n, w = gram.getVarComponents(name)
                v = lex.TVar(n, w)
                params.append(v)
        else:
            params.append(p)

    return params

def getParamsFromExpression(exp):
    params = []
    
    if isinstance(exp, ECoJump):
        params.extend([exp.left, exp.right])
    elif isinstance(exp, ECopy):
        params.extend([exp.dest, exp.source])
    elif isinstance(exp, EUnOp):
        params.extend([exp.dest, exp.source])
    elif isinstance(exp, EBinOp):
        params.extend([exp.dest, exp.left, exp.right])
    elif isinstance(exp, EProCall):
        params.append(exp.dest)
        params.extend(exp.params)

    return getParamsFromPossiblePointers(params)

# basic expression statements
#############################

def getELabel(i, tokens, length):
    if i + 1 >= length:
        raise Exception('invalid number of tokens for label definition')
    
    elab = ELabel(tokens[i].name)
    sep = tokens[i + 1]

    if not isinstance(sep, lex.TSeparator):
        raise Exception('label must be followed by separator')

    return i + 2, elab

def getEJump(i, tokens, length):
    if i + 2 >= length:
        raise Exception('invalid number of tokens for unconditional jump')

    if not isinstance(tokens[i + 1], lex.TLabel):
        raise Exception('uncondtional jump must be followed by label')

    if not isinstance(tokens[i + 2], lex.TSeparator):
        raise Exception('label must be followed by separator')

    name = tokens[i].name
    labelName = tokens[i + 1].name

    return i + 3, EJump(name, labelName)

def getECoJump(i, tokens, length):
    if i + 4 >= length:
        raise Exception('invalid number of tokens for conditional jump')
    
    jump = tokens[i]
    left = tokens[i + 1]
    right = tokens[i + 2]
    label = tokens[i + 3]
    sep = tokens[i + 4]

    validCompTypes = [
        lex.TInt, lex.TChar,
        lex.TVar
    ]

    if (not isValidTokenInTypeList(left, validCompTypes)):
        raise Exception('invalid left parameter for conditional jump')

    if (not isValidTokenInTypeList(right, validCompTypes)):
        raise Exception('invalid right parameter for conditional jump')
    
    if not isinstance(label, lex.TLabel):
        raise Exception('invalid label for conditional jump')
    
    if not isinstance(sep, lex.TSeparator):
        raise Exception('conditional jump must be followed by separator')

    return i + 5, ECoJump(jump.name, left, right, label.name)

# group assignment statements
#############################

def getECopy(group):
    dest = group[0]
    eq = group[1]
    source = group[2]

    if (not isValidTokenInTypeList(dest, [lex.TVar, lex.TPointer])):
        raise Exception('first token must be variable or memory pointer')
    
    if (not isinstance(eq, lex.TAssign)):
        raise Exception('second token must be assignment')
    
    validCopyTypes = [
        lex.TInt, lex.TChar,
        lex.TIdentifier, lex.TPointer,
        lex.TVar
    ]

    if (not isValidTokenInTypeList(source, validCopyTypes)):
        raise Exception('third token must be literal, identifier, variable or memory pointer')

    return ECopy(dest, source)

def getEUnOp(group):
    dest = group[0]
    eq = group[1]
    op = group[2]
    source = group[3]

    if (not isValidTokenInTypeList(dest, [lex.TVar])):
        raise Exception('first token must be variable or memory pointer in unary operation')
    
    if (not isinstance(eq, lex.TAssign)):
        raise Exception('second token must be assignment in unary operation')

    if (not isinstance(op, lex.TUnOp)):
        raise Exception('third token must be unary operator in unary operation')
    
    validSourceTypes = [
        lex.TInt, lex.TChar,
        lex.TVar
    ]

    if (not isValidTokenInTypeList(source, validSourceTypes)):
        raise Exception('fourth token must be literal, variable or memory pointer in unary operation')

    return EUnOp(dest, op.name, source)

def getEBinOp(group):
    dest = group[0]
    eq = group[1]
    op = group[2]
    left = group[3]
    right = group[4]

    if (not isValidTokenInTypeList(dest, [lex.TVar])):
        raise Exception('first token must be variable or memory pointer in binary operation')
    
    if (not isinstance(eq, lex.TAssign)):
        raise Exception('second token must be assignment in binary operation')

    if (not isinstance(op, lex.TBinOp)):
        raise Exception('third token must be binary operator in binary operation')

    validSourceTypes = [
        lex.TInt, lex.TChar,
        lex.TVar
    ]

    if (not isValidTokenInTypeList(left, validSourceTypes)):
        raise Exception('fourth token must be literal, variable or memory pointer in binary operation')
    
    if (not isValidTokenInTypeList(right, validSourceTypes)):
        raise Exception('fifth token must be literal, variable or memory pointer in binary operation')

    return EBinOp(dest, op.name, left, right)

def getEProCall(group):
    dest = group[0]
    eq = group[1]
    id = group[2]
    params = group[3:]

    if (not isValidTokenInTypeList(dest, [lex.TVar])):
        raise Exception('first token must be variable or memory pointer in procedure call')
    
    if (not isinstance(eq, lex.TAssign)):
        raise Exception('second token must be assignment in procedure call')

    if (not isinstance(id, lex.TIdentifier)):
        raise Exception('third token must be identifier in procedure call')

    validParamTypes = [
        lex.TInt, lex.TChar,
        lex.TIdentifier, lex.TVar
    ]

    for p in params:
        if (not isValidTokenInTypeList(p, validParamTypes)):
            raise Exception('parameter token must be literal, identifier, variable or memory pointer in procedure call')
    
    return EProCall(dest, id.name, params)

# group assignment helpers
##########################

def getParsedPointerGroup(group):
    name = ''
    inPointer = False
    parsed = []

    for t in group:
        if inPointer:
            if isinstance(t, lex.TPointRightB):
                inPointer = False

                if len(name) == 0:
                    raise Exception('pointer reference must not be blank')
                
                parsed.append(lex.TPointer(name))
                name = ''
            elif len(name) == 0:
                if isinstance(t, lex.TVar):
                    name = t.name
                else:
                    raise Exception('pointer reference must be variable')
            else:
                raise Exception('pointer must not have more than one token')
        else:
            if isinstance(t, lex.TPointLeftB):
                inPointer = True
            else:
                parsed.append(t)

    return parsed

def getEAssignmentOpId(group):
    opId = OP_TYPE_COPY
    gi = 0
    gend = len(group)

    while gi < gend:
        t = group[gi]
        if isinstance(t, lex.TUnOp):
            opId = OP_TYPE_UN_OP
        elif isinstance(t, lex.TBinOp):
            opId = OP_TYPE_BIN_OP
        elif isinstance(t, lex.TIdentifier) and (gi + 1 < gend):
            opId = OP_TYPE_PRO_CALL

        gi += 1

    return opId

def getEAssignmentByOpId(opId, group):
    if opId == OP_TYPE_COPY:
        return getECopy(group)
    elif opId == OP_TYPE_UN_OP:
        return getEUnOp(group)
    elif opId == OP_TYPE_BIN_OP:
        return getEBinOp(group)
    elif opId == OP_TYPE_PRO_CALL:
        return getEProCall(group)
    else:
        raise Exception('invalid assignment')

    return None

def getEAssignment(i, tokens, length):
    group = []

    while i < length:
        t = tokens[i]
        i += 1

        if isinstance(t, lex.TSeparator):
            break
        else:
            group.append(t)

    parsedPointerGroup = getParsedPointerGroup(group)
    opId = getEAssignmentOpId(parsedPointerGroup)
    assignment = getEAssignmentByOpId(opId, parsedPointerGroup)

    return i, assignment

# procedures
############

def getEProFirstLine(i, tokens, length):
    name = ''
    params = []

    if (i < length) and (isinstance(tokens[i], lex.TIdentifier)):
        name = tokens[i].name

    if len(name) == 0:
        raise Exception('procdures must have names')
    
    i += 1

    while i < length:
        t = tokens[i]
        i += 1
        if isinstance(t, lex.TSeparator):
            break
        elif isinstance(t, lex.TVar):
            params.append(t)
        else:
            raise Exception('invalid token used as procedure parameter')

    return i, name, params

def getEProLastLine(i, tokens, length):
    ret = None

    if (i < length) and (isValidTokenInTypeList(tokens[i], RETURN_TYPES)):
        ret = tokens[i]
        i += 1
    else:
        raise Exception('invalid token used as procedure return value')
    
    if (i < length) and (not isinstance(tokens[i], lex.TSeparator)):
        raise Exception('procedures must be followed by separators')

    return i + 1, ret

def getEPro(i, tokens, length):
    i, name, params = getEProFirstLine(i + 1, tokens, length)
    expressions = []

    while i < length:
        t = tokens[i]
        if isinstance(t, lex.TSeparator):
            i += 1
        elif isinstance(t, lex.TLabel):
            i, elab = getELabel(i, tokens, length)
            expressions.append(elab)
        elif isinstance(t, lex.TJump):
            i, eJump = getEJump(i, tokens, length)
            expressions.append(eJump)
        elif isinstance(t, lex.TCoJump):
            i, eCoJump = getECoJump(i, tokens, length)
            expressions.append(eCoJump)
        elif isValidTokenInTypeList(t, [lex.TPointLeftB, lex.TVar]):
            i, assignment = getEAssignment(i, tokens, length)
            expressions.append(assignment)
        elif isinstance(t, lex.TProRet):
            i, ret = getEProLastLine(i + 1, tokens, length)
            pro = EPro(
                name,
                params,
                expressions,
                ret
            )
            return i, pro
        else:
            raise Exception('invalid token in sequence')
        
    return i, None

# memory
########

def getEMemCollection(name, i, tokens, length):
    collection = []

    validCollectionTypes = [
        lex.TInt, lex.TChar, lex.TString
    ]

    while i < length:
        t = tokens[i]
        i += 1

        if isinstance(t, lex.TMemRightB):
            break

        if isinstance(t, lex.TSeparator):
            continue

        if (not isValidTokenInTypeList(t, validCollectionTypes)):
            raise Exception('token must be literal, variable or identifier in memory collection')
        
        if len(collection) > 0 and (not isinstance(t, type(collection[-1]))):
            raise Exception('each token must have same type in memory collection')

        collection.append(t)

    if len(collection) == 0:
        raise Exception('memory collection must not be empty')
    
    if (i < length) and (not isinstance(tokens[i], lex.TSeparator)):
        raise Exception('memory collections must be followed by separators')
        
    return i + 1, EMemCollection(name, collection)
    
def getEMemSize(name, i, tokens, length):
    size = tokens[i].value
    i += 1

    if (i < length) and (not isinstance(tokens[i], lex.TSeparator)):
        raise Exception('memory size blocks must be followed by separators')

    return i + 1, EMemSize(name, size)

def getEMem(i, tokens, length):
    name = ''

    if (i < length) and (isinstance(tokens[i], lex.TIdentifier)):
        name = tokens[i].name

    if len(name) == 0:
        raise Exception('memory collections must have names')
    
    i += 1

    if i < length:
        t = tokens[i]
        if isinstance(t, lex.TMemLeftB):
            return getEMemCollection(name, i + 1, tokens, length)
        elif isinstance(t, lex.TInt):
            return getEMemSize(name, i, tokens, length)
        else:
            raise Exception('memory identifiers must be followed by collections or integer sizes')

    return i, None

# main expression function
##########################

def getExpressions(tokens):
    expressions = []

    length = len(tokens)
    i = 0

    while i < length:
        if isinstance(tokens[i], lex.TSeparator):
            i += 1
        elif isinstance(tokens[i], lex.TProId):
            i, pro = getEPro(i, tokens, length)
            expressions.append(pro)
        elif isinstance(tokens[i], lex.TMemId):
            i, mem = getEMem(i + 1, tokens, length)
            expressions.append(mem)
        else:
            raise Exception('invalid token in sequence')
        
    return expressions
