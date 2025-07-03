import lib.grammar as gram
import lib.lexer as lex
import lib.parser as par
import lib.assembly_map as asm
import lib.simple_allocator as sar
import lib.gen_code as gen

#
# test helpers
#

def printLines(lines):
    for line in lines:
        print(line)

    print('')

def areAsmStringsEqual(generated, expected):
    if generated == expected:
        return True
    
    print('test failed\n')
    print('generated:')
    print(generated)
    print('\nexpected:')
    print(expected)
    print('')
    return False

def areListsOfAsmStringsEqual(generated, expected):
    length = len(generated)

    if len(expected) != length:
        print('test failed\n')
        print('generated length: ' + str(length))
        print('\nexpected length: ' + str(len(expected)))
        print('')
        print('generated lines:')
        printLines(generated)
        print('expected lines:')
        printLines(expected)
        return False

    for i in range(length):
        if (not areAsmStringsEqual(generated[i], expected[i])):
            print('generated lines:')
            printLines(generated)
            print('expected lines:')
            printLines(expected)
            return False
        
    return True

#
# simple assembly map implementation
#

class SimpleAssemblyMap(asm.AssemblyMap):
    def __init__(self):
        super().__init__('SimpleAssemblyMap')

    # register section

    BYTE_MAP = {
        'r0': 'r0b',
        'r1': 'r1b',
        'r2': 'r2b',
        'r3': 'r3b',
        'r4': 'r4b',
        'r5': 'r5b',
        'r6': 'r6b',
        'r7': 'r7b',
        'r8': 'r8b',
        'r9': 'r9b',
        'r10': 'r10b'
    }

    WORD_MAP = {
        'r0': 'r0w',
        'r1': 'r1w',
        'r2': 'r2w',
        'r3': 'r3w',
        'r4': 'r4w',
        'r5': 'r5w',
        'r6': 'r6w',
        'r7': 'r7w',
        'r8': 'r8w',
        'r9': 'r9w',
        'r10': 'r10w'
    }

    DOUBLE_WORD_MAP = {
        'r0': 'r0d',
        'r1': 'r1d',
        'r2': 'r2d',
        'r3': 'r3d',
        'r4': 'r4d',
        'r5': 'r5d',
        'r6': 'r6d',
        'r7': 'r7d',
        'r8': 'r8d',
        'r9': 'r9d',
        'r10': 'r10d'
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
        gram.SUB: 'sub'
    }

    def getFramePointReg(self):
        return 'fp'
    
    def getStackPointReg(self):
        return 'sp'
    
    def getArgumentRegs(self):
        return [
            'r1', 'r2'
        ]
    
    def getCallerSavedRegs(self):
        return [
            'r1', 'r2', 'r3', 'r4'
        ]
    
    def getCalleeSavedRegs(self):
        return [
            'r5', 'r6', 'r7'
        ]
    
    def getIntermediateRegs(self):
        return [
            'r8', 'r9', 'r10'
        ]
    
    def getRetReg(self):
        return 'r0'
    
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
        return ['lea ' + dest + ', ' + source + '[ip]']
    
    def emitCopyIdentifierValue(self, dest, source):
        return ['mov ' + dest + ', ' + source + '[ip]']
    
    def emitUnOp(self, dest, op, source):
        if dest == source:
            return [self.getUnOp(op) + ' ' + dest]
        
        first = 'mov ' + dest + ', ' + source
        second = self.getUnOp(op) + ' ' + dest
        return [first, second]
    
    def emitBinOp(self, dest, op, left, right):
        if dest == left:
            return [self.getBinOp(op) + ' ' + dest + ', ' + right]
        
        first = 'mov ' + dest + ', ' + left
        second = self.getBinOp(op) + ' ' + dest + ', ' + right
        return [first, second]

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
        
        return (pre[0] == cur[1]) and (pre[1] == cur[0])

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

#
# procedure tests
#

SOURCE_CODE_0 = """
pro simple_inc_0 x0
    x1 = add x0 1
    ret x1

pro simple_test_0 x0 x1 x2 x3
    x10 = add x0 x1
    x11 = add x10 x2
    x12 = add x11 x3
    x13 = simple_inc_0 x12
    ret x13
"""

TARGET_CODE_0 = """
.section .text

.global simple_inc_0
.global simple_test_0

simple_inc_0:
mov r2, r1
add r2, 1
mov r0, r2
ret

simple_test_0:
sub sp, 48
mov [sp], r5
mov [sp + 8], r6
mov r3, r1
add r3, r2
mov r10, [sp + 56]
mov r4, r3
add r4, r10
mov r10, [sp + 64]
mov r5, r4
add r5, r10
mov [sp + 16], r1
mov [sp + 24], r2
mov [sp + 32], r3
mov [sp + 40], r4
mov r1, r5
call simple_inc_0
mov r1, [sp + 16]
mov r2, [sp + 24]
mov r3, [sp + 32]
mov r4, [sp + 40]
mov r6, r0
mov r0, r6
mov r5, [sp]
mov r6, [sp + 8]
add sp, 48
ret
"""


SOURCE_CODE_1 = """
pro simple_args_1 x0 x1 x2 x3 x4
    x10 = add x0 x1
    x11 = add x10 x2
    x12 = add x11 x3
    x13 = add x12 x4
    ret x13

pro simple_test_1 x0
    x1 = 1
    x2 = 2
    x3 = 3
    x4 = 4
    x5 = simple_args_1 x0 x1 x2 x3 x4
    ret x5
"""

TARGET_CODE_1 = """
.section .text

.global simple_args_1
.global simple_test_1

simple_args_1:
sub sp, 16
mov [sp], r5
mov [sp + 8], r6
mov r3, r1
add r3, r2
mov r10, [sp + 24]
mov r4, r3
add r4, r10
mov r10, [sp + 32]
mov r5, r4
add r5, r10
mov r10, [sp + 40]
mov r6, r5
add r6, r10
mov r0, r6
mov r5, [sp]
mov r6, [sp + 8]
add sp, 16
ret

simple_test_1:
sub sp, 48
mov [sp], r5
mov [sp + 8], r6
mov r2, 1
mov r3, 2
mov r4, 3
mov r5, 4
mov [sp + 16], r1
mov [sp + 24], r2
mov [sp + 32], r3
mov [sp + 40], r4
mov r1, [sp + 16]
mov r2, [sp + 24]
push r5
push r4
push r3
call simple_args_1
add sp, 24
mov r1, [sp + 16]
mov r2, [sp + 24]
mov r3, [sp + 32]
mov r4, [sp + 40]
mov r6, r0
mov r0, r6
mov r5, [sp]
mov r6, [sp + 8]
add sp, 48
ret
"""

SOURCE_CODE_2 = """
pro swap_chars x0 x1
    x2 = [x0]
    x3 = [x1]
    [x0] = x3b
    [x1] = x2b
    ret 0
"""

TARGET_CODE_2 = """
.section .text

.global swap_chars

swap_chars:
mov r3, [r1]
mov r4, [r2]
mov [r1], r4b
mov [r2], r3b
mov r0, 0
ret
"""

SOURCE_CODE_3 = """
mem ar {1 2 3}

pro setAr x0 x1
    x2 = ar
    x2 = add x2 x0
    [x2] = x1
    ret 0
"""

TARGET_CODE_3 = """
.section .text

.global setAr

setAr:
lea r3, ar[ip]
add r3, r1
mov [r3], r2
mov r0, 0
ret

.section .data

ar: .quad 1, 2, 3
"""

SOURCE_CODE_4 = """
pro add4 x0 x1 x2 x3
    x4 = add x0 x1
    x4 = add x4 x2
    x4 = add x4 x3
    ret x4

pro testAdd4 x0
    x4 = add4 x0 2 3 4
    ret x4
"""

TARGET_CODE_4 = """
.section .text

.global add4
.global testAdd4

add4:
mov r3, r1
add r3, r2
mov r10, [sp + 8]
add r3, r10
mov r10, [sp + 16]
add r3, r10
mov r0, r3
ret

testAdd4:
sub sp, 16
mov [sp], r1
mov [sp + 8], r2
mov r1, [sp]
mov r2, 2
mov r8, 4
push r8
mov r8, 3
push r8
call add4
add sp, 16
mov r1, [sp]
mov r2, [sp + 8]
mov r2, r0
mov r0, r2
add sp, 16
ret
"""

SOURCE_CODE_5 = """
pro id x0
    ret x0

pro runTest x0 x1
    x2 = !x0 x1
    ret x2
"""

TARGET_CODE_5 = """
.section .text

.global id
.global runTest

id:
mov r0, r1
ret

runTest:
sub sp, 32
mov r1, r2
call r1
mov r3, r0
mov r0, r3
add sp, 32
ret
"""

testSetA = [
    [SOURCE_CODE_0, TARGET_CODE_0],
    [SOURCE_CODE_1, TARGET_CODE_1],
    [SOURCE_CODE_2, TARGET_CODE_2],
    [SOURCE_CODE_3, TARGET_CODE_3],
    [SOURCE_CODE_4, TARGET_CODE_4],
    [SOURCE_CODE_5, TARGET_CODE_5]
]

#
# test functions
#

def runBasicTests(testSet):
    asmap = SimpleAssemblyMap()

    for s in testSet:
        code = gen.generateCodeLinesFromText(s[0], asmap)
        generated = '\n'.join(code).strip()
        expected = s[1].strip()

        if (not areAsmStringsEqual(generated, expected)):
            return False

    return True

#
# Run All Tests
#

def runAllTests():
    allPass = True
    allPass = allPass and runBasicTests(testSetA)

    if allPass:
        print('all procedure code generation tests passed')
    else:
        print('at least one procedure code generation test failed')
