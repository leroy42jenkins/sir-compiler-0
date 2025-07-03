import lib.grammar as gram
import lib.lexer as lex

#
# default map with x86-64 ISA and Intel syntax
#

class AssemblyMap():
    def __init__(self, name):
        self.name = name

    # register section

    def getFramePointReg(self):
        return ''
    
    def getStackPointReg(self):
        return ''
    
    def getArgumentRegs(self):
        return []
    
    def getCallerSavedRegs(self):
        return []
    
    def getCalleeSavedRegs(self):
        return []
    
    def getIntermediateRegs(self):
        return []
    
    def getRetReg(self):
        return ''
    
    def getByteReg(self, reg):
        return reg
    
    def getWordReg(self, reg):
        return reg
    
    def getDoubleWordReg(self, reg):
        return reg

    def getRegistersToMap(self):
        arguments = self.getArgumentRegs()
        callerSaved = self.getCallerSavedRegs()
        calleeSaved = self.getCalleeSavedRegs()
        intermediate = self.getIntermediateRegs()

        registerMap = {}

        for r in arguments:
            registerMap[r] = True
        
        for r in callerSaved:
            if (r not in intermediate):
                registerMap[r] = True

        for r in calleeSaved:
            if (r not in intermediate):
                registerMap[r] = True
        
        return [k for k in registerMap.keys()]
    
    def isReg(self, name):
        return False
        
    # code generation section

    def getJump(self, j):
        return j
    
    def getUnOp(self, op):
        return op

    def getBinOp(self, op):
        return op
    
    def getPointer(self, name):
        return []
        
    def getByteAlignment(self):
        return 0
    
    def emitSectionData(self):
        return []
    
    def emitSectionText(self):
        return []
    
    def emitGlobal(self, name):
        return []

    def emitStackAllocation(self, bytes):
        return []
    
    def emitStackDeallocation(self, bytes):
        return []
    
    def emitStackLoad(self, dest, offset):
        return []
    
    def emitStackStore(self, source, offset):
        return []
    
    def emitPush(self, source):
        return []
    
    def emitPop(self, dest):
        return []

    def emitLocalLabel(self, proName, labelName):
        return []

    def emitProName(self, name):
        return []

    def emitJump(self, j, proName, labelName):
        return []
    
    def emitCoJump(self, j, left, right, proName, labelName):
        return []
    
    def emitCopy(self, dest, source):
        return []
    
    def emitCopyIdentifierAddress(self, dest, source):
        return []
    
    def emitCopyIdentifierValue(self, dest, source):
        return []

    def emitUnOp(self, dest, op, source):
        return []
    
    def emitBinOp(self, dest, op, left, right):
        return []

    def emitCall(self, proName):
        return []
    
    def emitRet(self):
        return []
    
    def emitMemCollection(self, name, collection):
        return []
    
    def emitMemSize(self, name, size):
        return []
    
    def emitOptimized(self, code):
        return code
    
class GasIntelX8664SystemVMap(AssemblyMap):
    def __init__(self):
        super().__init__('GasIntelX8664SystemVMap')

    # register section

    BYTE_MAP = {
        'rax': 'al',
        'rbx': 'bl',
        'rcx': 'cl',
        'rdx': 'dl',
        'rsi': 'sil',
        'rdi': 'dil',
        'rbp': 'bpl',
        'rsp': 'spl',
        'r8': 'r8b',
        'r9': 'r9b',
        'r10': 'r10b',
        'r11': 'r11b',
        'r12': 'r12b',
        'r13': 'r13b',
        'r14': 'r14b',
        'r15': 'r15b'
    }

    WORD_MAP = {
        'rax': 'ax',
        'rbx': 'bx',
        'rcx': 'cx',
        'rdx': 'dx',
        'rsi': 'si',
        'rdi': 'di',
        'rbp': 'bp',
        'rsp': 'sp',
        'r8': 'r8w',
        'r9': 'r9w',
        'r10': 'r10w',
        'r11': 'r11w',
        'r12': 'r12w',
        'r13': 'r13w',
        'r14': 'r14w',
        'r15': 'r15w'
    }

    DOUBLE_WORD_MAP = {
        'rax': 'eax',
        'rbx': 'ebx',
        'rcx': 'ecx',
        'rdx': 'edx',
        'rsi': 'esi',
        'rdi': 'edi',
        'rbp': 'ebp',
        'rsp': 'esp',
        'r8': 'r8d',
        'r9': 'r9d',
        'r10': 'r10d',
        'r11': 'r11d',
        'r12': 'r12d',
        'r13': 'r13d',
        'r14': 'r14d',
        'r15': 'r15d'
    }

    JUMP_MAP = {
        gram.JUMP: 'jmp',
        gram.JIL: 'jl',
        gram.JILE: 'jle',
        gram.JIE: 'je',
        gram.JIN: 'jne',
        gram.JIGE: 'jge',
        gram.JIG: 'jg'
    }

    UN_OP_MAP = {
        gram.NOT: 'not'
    }

    BIN_OP_MAP = {
        gram.OR: 'or',
        gram.AND: 'and',
        gram.XOR: 'xor',
        gram.ADD: 'add',
        gram.SUB: 'sub',
        gram.MUL: 'imul',
        gram.DIV: 'idiv',
        gram.MOD: 'idiv'
    }

    def getFramePointReg(self):
        return 'rbp'
    
    def getStackPointReg(self):
        return 'rsp'
    
    def getArgumentRegs(self):
        return [
            'rdi', 'rsi',
            'rdx', 'rcx',
            'r8', 'r9'
        ]
    
    def getCallerSavedRegs(self):
        return [
            'rdi', 'rsi',
            'rdx', 'rcx',
            'r8', 'r9',
            'r10', 'r11'
        ]
    
    def getCalleeSavedRegs(self):
        return [
            'rbx',
            'r12', 'r13',
            'r14', 'r15'
        ]
    
    def getIntermediateRegs(self):
        return [
            'rax',
            'r10', 'r11'
        ]
    
    def getRetReg(self):
        return 'rax'
    
    def getByteReg(self, reg):
        return self.BYTE_MAP[reg]
    
    def getWordReg(self, reg):
        return self.WORD_MAP[reg]
    
    def getDoubleWordReg(self, reg):
        return self.DOUBLE_WORD_MAP[reg]
    
    def isReg(self, name):
        return name in self.DOUBLE_WORD_MAP
        
    # code generation section
    
    def getJump(self, j):
        return self.JUMP_MAP[j]
    
    def getUnOp(self, op):
        return self.UN_OP_MAP[op]

    def getBinOp(self, op):
        return self.BIN_OP_MAP[op]
    
    def getPointer(self, name):
        return '[' + name + ']'
    
    def getByteAlignment(self):
        return 16

    def emitSectionData(self):
        return ['.section .data']
    
    def emitSectionText(self):
        return ['.section .text']
    
    def emitGlobal(self, name):
        return ['.global ' + name]
        
    def emitStackAllocation(self, bytes):
        sp = self.getStackPointReg()
        return ['sub ' + sp + ', ' + str(bytes)]
    
    def emitStackDeallocation(self, bytes):
        sp = self.getStackPointReg()
        return ['add ' + sp + ', ' + str(bytes)]
    
    def emitStackLoad(self, dest, offset):
        sp = self.getStackPointReg()

        if offset == 0:
            return ['mov ' + dest + ', [' + sp + ']']
        
        return ['mov ' + dest + ', [' + sp + ' + ' + str(offset) + ']']
    
    def emitStackStore(self, source, offset):
        sp = self.getStackPointReg()

        if offset == 0:
            return ['mov [' + sp + '], ' + source]
        
        return ['mov [' + sp + ' + ' + str(offset) + '], ' + source]
    
    def emitPush(self, source):
        return ['push ' + source]
    
    def emitPop(self, dest):
        return ['pop ' + dest]

    def emitLocalLabel(self, proName, labelName):
        return [proName + '_' + labelName[1:] + ':']

    def emitProName(self, name):
        return [name + ':']

    def emitJump(self, j, proName, labelName):
        return [self.getJump(j) + ' ' + proName + '_' + labelName[1:]]
    
    def emitCoJump(self, j, left, right, proName, labelName):
        first = 'cmp ' + left + ', ' + right
        second = self.getJump(j) + ' ' + proName + '_' + labelName[1:]
        return [first, second]
    
    def emitCopy(self, dest, source):
        if source == dest:
            return []
        
        return ['mov ' + dest + ', ' + source]
    
    def emitCopyIdentifierAddress(self, dest, source):
        return ['lea ' + dest + ', ' + source + '[rip]']
    
    def emitCopyIdentifierValue(self, dest, source):
        return ['mov ' + dest + ', ' + source + '[rip]']
    
    def emitUnOp(self, dest, op, source):
        if dest == source:
            return [self.getUnOp(op) + ' ' + dest]
        
        first = 'mov ' + dest + ', ' + source
        second = self.getUnOp(op) + ' ' + dest
        return [first, second]
    
    def emitBinOp(self, dest, op, left, right):
        if op == gram.MUL:
            return self.emitMulOp(dest, left, right)
        elif op == gram.DIV:
            return self.emitDivOp(dest, left, right)
        elif op == gram.MOD:
            return self.emitModOp(dest, left, right)

        if dest == left:
            return [self.getBinOp(op) + ' ' + dest + ', ' + right]
        
        first = 'mov ' + dest + ', ' + left
        second = self.getBinOp(op) + ' ' + dest + ', ' + right
        return [first, second]
    
    def emitMulOp(self, dest, left, right):
        if dest == left:
            return ['imul ' + dest + ', ' + right]
        
        first = 'mov ' + dest + ', ' + left
        second = 'imul ' + dest + ', ' + right
        return [first, second]
    
    def emitDivOp(self, dest, left, right):
        code = []
        pre = []
        post = []

        if dest == 'rdx':
            pre.extend(self.emitPush('rax'))
            post.extend(self.emitPop('rax'))

            code.append('mov rax, ' + left)
            code.append('xor rdx, rdx')
            code.append('cqo')
            code.append('idiv ' + right)
            code.append('mov rdx, rax')
        elif dest == 'rax':
            pre.extend(self.emitPush('rdx'))
            post.extend(self.emitPop('rdx'))
            
            code.append('mov rax, ' + left)
            code.append('xor rdx, rdx')
            code.append('cqo')
            code.append('idiv ' + right)
        else:
            pre.extend(self.emitPush('rdx'))
            pre.extend(self.emitPush('rax'))

            ri = right
            
            if ri in ['rax', 'rdx']:
                ri = 'r11'
                code.append('mov ' + ri + ', ' + right)
                pre.extend(self.emitPush('r11'))
                post.extend(self.emitPop('r11'))

            post.extend(self.emitPop('rax'))
            post.extend(self.emitPop('rdx'))

            code.append('mov rax, ' + left)
            code.append('xor rdx, rdx')
            code.append('cqo')
            code.append('idiv ' + ri)
            code.append('mov ' + dest + ', rax')
        
        return pre + code + post
    
    def emitModOp(self, dest, left, right):
        code = []
        pre = []
        post = []

        if dest == 'rdx':
            pre.extend(self.emitPush('rax'))
            post.extend(self.emitPop('rax'))

            code.append('mov rax, ' + left)
            code.append('xor rdx, rdx')
            code.append('cqo')
            code.append('idiv ' + right)
        elif dest == 'rax':
            pre.extend(self.emitPush('rdx'))
            post.extend(self.emitPop('rdx'))
            
            code.append('mov rax, ' + left)
            code.append('xor rdx, rdx')
            code.append('cqo')
            code.append('idiv ' + right)
            code.append('mov rax, rdx')
        else:
            pre.extend(self.emitPush('rdx'))
            pre.extend(self.emitPush('rax'))

            ri = right
            
            if ri in ['rax', 'rdx']:
                ri = 'r11'
                code.append('mov ' + ri + ', ' + right)
                pre.extend(self.emitPush('r11'))
                post.extend(self.emitPop('r11'))

            post.extend(self.emitPop('rax'))
            post.extend(self.emitPop('rdx'))

            code.append('mov rax, ' + left)
            code.append('xor rdx, rdx')
            code.append('cqo')
            code.append('idiv ' + ri)
            code.append('mov ' + dest + ', rdx')
        
        return pre + code + post

    def emitCall(self, proName):
        return ['call ' + proName]
    
    def emitRet(self):
        return ['ret']
    
    def emitMemCollection(self, name, collection):
        length = len(collection)

        if length < 1:
            return []
        
        sequence = name + ':'
        first = collection[0]
        tokenType = type(first)

        if tokenType == lex.TInt:
            col = [i.value for i in collection]
            sequence += ' .quad ' + ', '.join(col)
        elif tokenType == lex.TChar:
            col = ["'" + c.value + "'" for c in collection]
            sequence += ' .byte ' + ', '.join(col)
        elif tokenType == lex.TString:
            col = [s.value for s in collection]
            sequence += ' .ascii "' + ''.join(col) + '"'
        else:
            raise Exception('unsupported memroy collection type: ' + type(first))

        return [sequence]
    
    def emitMemSize(self, name, size):
        if int(size) < 1:
            return []
        
        return [name + ': .zero ' + size]
    
    def getLineItems(self, line):
        return [i.replace(',', '') for i in line.split(' ')]
    
    def isMovToSelf(self, cur):
        return (len(cur) == 3) and (cur[0] == 'mov') and (cur[1] == cur[2])
    
    def isAssignCross(self, pre, cur):
        if (len(pre) != 3) or (len(cur) != 3):
            return False
        
        if (pre[0] != 'mov') or (cur[0] != 'mov'):
            return False
        
        return (pre[1] == cur[2]) and (pre[2] == cur[1])

    def emitOptimized(self, code):
        optimized = []

        i = 0
        iend = len(code)

        while i < iend:
            cur = code[i]
            curItems = self.getLineItems(cur)

            if (not self.isMovToSelf(curItems)):
                if (i == 0):
                    optimized.append(cur)
                else:
                    pre = code[i - 1]
                    preItems = self.getLineItems(pre)
                    if (not self.isAssignCross(preItems, curItems)):
                        optimized.append(cur)

            i += 1

        return optimized
