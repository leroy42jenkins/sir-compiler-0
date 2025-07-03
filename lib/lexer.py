import lib.grammar as gram

#
# Token Types
#

class Token:
    def __init__(self, name):
        self.name = name

    def toString(self):
        return self.name

class TInt(Token):
    def __init__(self, name, value):
        super().__init__(name)
        self.value = value

    def toString(self):
        return '{ TInt: ' + self.value + ' }'

class TChar(Token):
    def __init__(self, name, value):
        super().__init__(name)
        self.value = value
    
    def toString(self):
        return '{ TChar: ' + self.value + ' }'

class TString(Token):
    def __init__(self, name, value):
        super().__init__(name)
        self.value = value
    
    def toString(self):
        return '{ TString: ' + self.value + ' }'

class TVar(Token):
    def __init__(self, name, width):
        super().__init__(name)
        self.width = width

    def toString(self):
        return '{ TVar: ' + self.name + ' ' + str(self.width) + ' }'

class TLabel(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TLabel: ' + self.name + ' }'

class TJump(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TJump: ' + self.name + ' }'

class TCoJump(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TCoJump: ' + self.name + ' }'

class TAssign(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TAssign: ' + self.name + ' }'

class TUnOp(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TUnOp: ' + self.name + ' }'
    
class TBinOp(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TBinOp: ' + self.name + ' }'

class TSeparator(Token):
    def __init__(self, name):
        super().__init__(name)
    
    def toString(self):
        return '{ TSeparator }'

class TIdentifier(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TIdentifier: ' + self.name + ' }'

class TProId(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TProId: ' + self.name + ' }'

class TProRet(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TProRet: ' + self.name + ' }'

class TMemId(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TMemId: ' + self.name + ' }'

class TMemLeftB(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TMemLeftB: "' + self.name + '" }'

class TMemRightB(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TMemRightB: "' + self.name + '" }'

class TPointLeftB(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TPointLeftB: "' + self.name + '" }'

class TPointRightB(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TPointRightB: "' + self.name + '" }'

# compound token type used in parser
class TPointer(Token):
    def __init__(self, name):
        super().__init__(name)

    def toString(self):
        return '{ TPointer: ' + self.name + ' }'

#
# Token Functions
#

def getSegments(source):
    segments = []
    segment = ''
    inString = False
    inComment = False

    for i in range(len(source)):
        if inString:
            segment += source[i]
            if gram.isStringStop(i):
                segments.append(segment)
                segment = ''
                inString = False
        elif inComment:
            segment += source[i]
            if gram.isCommentStop(source, i):
                segments.append(segment)
                segment = ''
                inComment = False
        else:
            if gram.isStringStart(source, i):
                segment += source[i]
                inString = True
            elif gram.isCommentStart(source, i):
                segment += source[i]
                inComment = True
            elif gram.isSeparator(source, i):
                if len(segment) > 0:
                    segments.append(segment)
                    segment = ''
                segments.append(gram.SEPARATOR)
            elif gram.isWhiteSpace(source, i):
                if len(segment) > 0:
                    segments.append(segment)
                    segment = ''
            elif gram.isBra(source, i):
                if len(segment) > 0:
                    segments.append(segment)
                    segment = ''
                segments.append(source[i])
            else:
                if not gram.isCharToSkip(source, i):
                    segment += source[i]

    if len(segment) > 0:
        segments.append(segment)

    return segments

def getCodeTokens(segments):
    tokens = []

    for s in segments:
        if gram.isInt(s) or gram.isHexInt(s):
            tokens.append(TInt(gram.INT, s))
        elif gram.isChar(s):
            tokens.append(TChar(gram.CHAR, s))
        elif gram.isString(s):
            st = s[1:-1]
            tokens.append(TString(gram.STRING, st))
        elif gram.isVar(s):
            var, width = gram.getVarComponents(s)
            tokens.append(TVar(var, width))
        elif gram.isLabel(s):
            tokens.append(TLabel(s))
        elif gram.isJump(s):
            tokens.append(TJump(s))
        elif gram.isCoJump(s):
            tokens.append(TCoJump(s))
        elif gram.isUnOp(s):
            tokens.append(TUnOp(s))
        elif gram.isBinOp(s):
            tokens.append(TBinOp(s))
        elif s == gram.SEPARATOR:
            tokens.append(TSeparator(s))
        elif s == gram.ASSIGN:
            tokens.append(TAssign(s))
        elif s == gram.PRO_ID:
            tokens.append(TProId(s))
        elif s == gram.PRO_RET:
            tokens.append(TProRet(s))
        elif s == gram.MEM_ID:
            tokens.append(TMemId(s))
        elif s == gram.MEM_LEFT_BRACE:
            tokens.append(TMemLeftB(s))
        elif s == gram.MEM_RIGHT_BRACE:
            tokens.append(TMemRightB(s))
        elif s == gram.POINT_LEFT_BRACKET:
            tokens.append(TPointLeftB(s))
        elif s == gram.POINT_RIGHT_BRACKET:
            tokens.append(TPointRightB(s))
        else:
            # used for procedures and memory names
            tokens.append(TIdentifier(s))

    return tokens
