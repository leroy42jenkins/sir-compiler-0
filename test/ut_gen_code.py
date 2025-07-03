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

def getDictLines(dict):
    lines = []
    for k in dict:
        v = dict[k]
        lines.append(k + ': ' + str(v))

    return lines

def areDictStringsEqual(generated, expected):
    generatedLines = getDictLines(generated)
    expectedLines = getDictLines(expected)
    return areListsOfAsmStringsEqual(generatedLines, expectedLines)

#
# basic tests
#

basicX8664Asmap = asm.GasIntelX8664SystemVMap()

basicX8664Assignments = gen.AssignmentCollection({
        'x0': 'rdi',
        'x1': 'rsi',
        'x2': sar.SPILL,
        'x3': sar.SPILL,
        'x4': sar.SPILL
    }, {
        'v_x2': 0,
        'v_x3': 8,
        'v_x4': 16
    }
)

basicX8664TestSets = [
    #
    # labels and jumps
    #
    [
        lambda: gen.getAsmLocalLabel(
            par.ELabel('@test'),
            'fun',
            basicX8664Asmap
        ),
        [
            'fun_test:'
        ]
    ],
    [
        lambda: gen.getAsmJump(
            par.EJump(
                gram.JUMP,
                '@test'
            ),
            'fun',
            basicX8664Asmap
        ),
        [
            'jmp fun_test'
        ]
    ],
    [
        lambda: gen.getAsmCoJump(
            par.ECoJump(
                gram.JIGE,
                lex.TVar('x0', 8),
                lex.TVar('x1', 8),
                '@test'
            ),
            'fun',
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'cmp rdi, rsi',
            'jge fun_test'
        ]
    ],
    [
        lambda: gen.getAsmCoJump(
            par.ECoJump(
                gram.JIGE,
                lex.TVar('x2', 8),
                lex.TVar('x3', 8),
                '@test'
            ),
            'fun',
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov rax, [rsp]',
            'mov r10, [rsp + 8]',
            'cmp rax, r10',
            'jge fun_test'
        ]
    ],
    #
    # literal to var and var to var copies
    #
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x0', 8),
                lex.TInt(gram.INT, '1')
            ),
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov rdi, 1'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x0', 8),
                lex.TVar('x2', 8)
            ),
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov r10, [rsp]',
            'mov rdi, r10'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x2', 8),
                lex.TVar('x0', 8)
            ),
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov rax, rdi',
            'mov [rsp], rax'
        ]
    ],
    #
    # pointer to var and var to pointer copies
    #
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x0', 8),
                lex.TPointer('x1')
            ),
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov rdi, [rsi]'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TPointer('x0'),
                lex.TVar('x1', 8)
            ),
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov [rdi], rsi'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x2', 8),
                lex.TPointer('x3')
            ),
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov r10, [rsp + 8]',
            'mov rax, [r10]',
            'mov [rsp], rax'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TPointer('x2'),
                lex.TVar('x3', 8)
            ),
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov rax, [rsp]',
            'mov r10, [rsp + 8]',
            'mov [rax], r10'
        ]
    ],
    #
    # unary operations
    #
    [
        lambda: gen.getAsmUnOp(
            par.EUnOp(
                lex.TVar('x0', 8),
                gram.NOT,
                lex.TVar('x1', 8)
            ),
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov rdi, rsi',
            'not rdi'
        ]
    ],
    [
        lambda: gen.getAsmUnOp(
            par.EUnOp(
                lex.TVar('x2', 8),
                gram.NOT,
                lex.TVar('x3', 8)
            ),
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov rax, [rsp]',
            'mov r10, [rsp + 8]',
            'mov rax, r10',
            'not rax',
            'mov [rsp], rax'
        ]
    ],
    #
    # binary operations
    #
    [
        lambda: gen.getAsmBinOp(
            par.EBinOp(
                lex.TVar('x0', 8),
                gram.ADD,
                lex.TVar('x1', 8),
                lex.TVar('x1', 8)
            ),
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov rdi, rsi',
            'add rdi, rsi'
        ]
    ],
    [
        lambda: gen.getAsmBinOp(
            par.EBinOp(
                lex.TVar('x2', 8),
                gram.ADD,
                lex.TVar('x3', 8),
                lex.TVar('x4', 8)
            ),
            basicX8664Asmap,
            basicX8664Assignments
        ),
        [
            'mov rax, [rsp]',
            'mov r10, [rsp + 8]',
            'mov r11, [rsp + 16]',
            'mov rax, r10',
            'add rax, r11',
            'mov [rsp], rax'
        ]
    ]
]

#
# sized basic tests
#

sizedBasicX8664Asmap = asm.GasIntelX8664SystemVMap()

sizedBasicX8664Assignments = gen.AssignmentCollection({
        'x0': 'rdi',
        'x1': 'rsi',
        'x2': sar.SPILL,
        'x3': sar.SPILL,
        'x4': sar.SPILL
    }, {
        'v_x2': 0,
        'v_x3': 8,
        'v_x4': 16
    }
)

sizedBasicX8664TestSets = [
    #
    # jumps
    #
    [
        lambda: gen.getAsmCoJump(
            par.ECoJump(
                gram.JIGE,
                lex.TVar('x0', 4),
                lex.TVar('x1', 4),
                '@test'
            ),
            'fun',
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'cmp edi, esi',
            'jge fun_test'
        ]
    ],
    [
        lambda: gen.getAsmCoJump(
            par.ECoJump(
                gram.JIGE,
                lex.TVar('x2', 4),
                lex.TVar('x3', 4),
                '@test'
            ),
            'fun',
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov eax, [rsp]',
            'mov r10d, [rsp + 8]',
            'cmp eax, r10d',
            'jge fun_test'
        ]
    ],
    #
    # copies
    #
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x0', 4),
                lex.TInt(gram.INT, '1')
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov edi, 1'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x0', 4),
                lex.TVar('x1', 4)
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov edi, esi'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x0', 4),
                lex.TPointer('x1')
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov edi, [rsi]'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TPointer('x0'),
                lex.TVar('x1', 4)
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov [rdi], esi'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x2', 4),
                lex.TPointer('x3')
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov r10, [rsp + 8]',
            'mov eax, [r10]',
            'mov [rsp], eax'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TPointer('x2'),
                lex.TVar('x3', 4)
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov rax, [rsp]',
            'mov r10d, [rsp + 8]',
            'mov [rax], r10d'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x2', 2),
                lex.TPointer('x3')
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov r10, [rsp + 8]',
            'mov ax, [r10]',
            'mov [rsp], ax'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TPointer('x2'),
                lex.TVar('x3', 2)
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov rax, [rsp]',
            'mov r10w, [rsp + 8]',
            'mov [rax], r10w'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x2', 1),
                lex.TPointer('x3')
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov r10, [rsp + 8]',
            'mov al, [r10]',
            'mov [rsp], al'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TPointer('x2'),
                lex.TVar('x3', 1)
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov rax, [rsp]',
            'mov r10b, [rsp + 8]',
            'mov [rax], r10b'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x0', 8),
                lex.TIdentifier('array_0')
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'lea rdi, array_0[rip]'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x2', 8),
                lex.TIdentifier('array_0')
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'lea rax, array_0[rip]',
            'mov [rsp], rax'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x0', 8),
                lex.TPointer('array_0')
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov rdi, array_0[rip]'
        ]
    ],
    [
        lambda: gen.getAsmCopy(
            par.ECopy(
                lex.TVar('x2', 8),
                lex.TPointer('array_0')
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov rax, array_0[rip]',
            'mov [rsp], rax'
        ]
    ],
    #
    # unary operations
    #
    [
        lambda: gen.getAsmUnOp(
            par.EUnOp(
                lex.TVar('x0', 4),
                gram.NOT,
                lex.TVar('x1', 4)
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov edi, esi',
            'not edi'
        ]
    ],
    [
        lambda: gen.getAsmUnOp(
            par.EUnOp(
                lex.TVar('x2', 4),
                gram.NOT,
                lex.TVar('x3', 4)
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov eax, [rsp]',
            'mov r10d, [rsp + 8]',
            'mov eax, r10d',
            'not eax',
            'mov [rsp], eax'
        ]
    ],
    #
    # binary operations
    #
    [
        lambda: gen.getAsmBinOp(
            par.EBinOp(
                lex.TVar('x0', 4),
                gram.ADD,
                lex.TVar('x1', 4),
                lex.TVar('x1', 4)
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov edi, esi',
            'add edi, esi'
        ]
    ],
    [
        lambda: gen.getAsmBinOp(
            par.EBinOp(
                lex.TVar('x2', 4),
                gram.ADD,
                lex.TVar('x3', 4),
                lex.TVar('x4', 4)
            ),
            sizedBasicX8664Asmap,
            sizedBasicX8664Assignments
        ),
        [
            'mov eax, [rsp]',
            'mov r10d, [rsp + 8]',
            'mov r11d, [rsp + 16]',
            'mov eax, r10d',
            'add eax, r11d',
            'mov [rsp], eax'
        ]
    ]
]

#
# procedure offSetDict tests
#

proOffsetX8664Asmap = asm.GasIntelX8664SystemVMap()

proOffsetX8664TestSets = [
    [
        lambda: gen.getOffsetDict(
            par.EPro(
                'add7Ints',
                [
                    lex.TVar('x0', 8),
                    lex.TVar('x1', 8),
                    lex.TVar('x2', 8),
                    lex.TVar('x3', 8),
                    lex.TVar('x4', 8),
                    lex.TVar('x5', 8),
                    lex.TVar('x6', 8)
                ],
                [
                    par.ECopy(
                        lex.TVar('x7', 8),
                        lex.TVar('x0', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x7', 8),
                        gram.ADD,
                        lex.TVar('x7', 8),
                        lex.TVar('x1', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x7', 8),
                        gram.ADD,
                        lex.TVar('x7', 8),
                        lex.TVar('x2', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x7', 8),
                        gram.ADD,
                        lex.TVar('x7', 8),
                        lex.TVar('x3', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x7', 8),
                        gram.ADD,
                        lex.TVar('x7', 8),
                        lex.TVar('x4', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x7', 8),
                        gram.ADD,
                        lex.TVar('x7', 8),
                        lex.TVar('x5', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x7', 8),
                        gram.ADD,
                        lex.TVar('x7', 8),
                        lex.TVar('x6', 8)
                    )
                ],
                lex.TVar('x7', 8)
            ),
            proOffsetX8664Asmap,
            {
                'x0': 'rdi',
                'x1': 'rsi',
                'x2': 'rdx',
                'x3': 'rcx',
                'x4': 'r8',
                'x5': 'r9',
                'x6': sar.OVER,
                'x7': 'r11'
            }
        ),
        {
            'v_x6': 8,
            gen.OFFSET_STACK: 0
        }
    ],
    [
        lambda: gen.getOffsetDict(
            par.EPro(
                'add8Ints',
                [
                    lex.TVar('x0', 8),
                    lex.TVar('x1', 8),
                    lex.TVar('x2', 8),
                    lex.TVar('x3', 8),
                    lex.TVar('x4', 8),
                    lex.TVar('x5', 8),
                    lex.TVar('x6', 8),
                    lex.TVar('x7', 8),
                ],
                [
                    par.ECopy(
                        lex.TVar('x10', 8),
                        lex.TVar('x0', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x10', 8),
                        gram.ADD,
                        lex.TVar('x10', 8),
                        lex.TVar('x1', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x10', 8),
                        gram.ADD,
                        lex.TVar('x10', 8),
                        lex.TVar('x2', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x10', 8),
                        gram.ADD,
                        lex.TVar('x10', 8),
                        lex.TVar('x3', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x10', 8),
                        gram.ADD,
                        lex.TVar('x10', 8),
                        lex.TVar('x4', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x10', 8),
                        gram.ADD,
                        lex.TVar('x10', 8),
                        lex.TVar('x5', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x10', 8),
                        gram.ADD,
                        lex.TVar('x10', 8),
                        lex.TVar('x6', 8)
                    ),
                    par.EBinOp(
                        lex.TVar('x10', 8),
                        gram.ADD,
                        lex.TVar('x10', 8),
                        lex.TVar('x7', 8)
                    ),
                    par.ECopy(
                        lex.TVar('x8', 8),
                        lex.TInt(gram.INT, '1')
                    ),
                    par.EBinOp(
                        lex.TVar('x10', 8),
                        gram.ADD,
                        lex.TVar('x10', 8),
                        lex.TVar('x8', 8)
                    )
                ],
                lex.TVar('x10', 8)
            ),
            proOffsetX8664Asmap,
            {
                'x0': 'rdi',
                'x1': 'rsi',
                'x2': 'rdx',
                'x3': 'rcx',
                'x4': 'r8',
                'x5': 'r9',
                'x6': sar.OVER,
                'x7': sar.OVER,
                'x8': sar.SPILL
            }
        ),
        {
            'v_x6': 24,
            'v_x7': 32,
            'v_x8': 0,
            gen.OFFSET_STACK: 16
        }
    ]
]

#
# memroy basic tests
#

memBasicX8664Asmap = asm.GasIntelX8664SystemVMap()

memBasicX8664TestSets = [
    [
        lambda: gen.getAsmMemCollection(
            par.EMemCollection(
                'intMem',
                [
                    lex.TInt(gram.INT, '1'),
                    lex.TInt(gram.INT, '2'),
                    lex.TInt(gram.INT, '3')
                ]
            ),
            memBasicX8664Asmap
        ),
        [
            'intMem: .quad 1, 2, 3'
        ]
    ],
    [
        lambda: gen.getAsmMemCollection(
            par.EMemCollection(
                'charMem',
                [
                    lex.TChar(gram.CHAR, 'a'),
                    lex.TChar(gram.CHAR, 'b'),
                ]
            ),
            memBasicX8664Asmap
        ),
        [
            "charMem: .byte 'a', 'b'"
        ]
    ],
    [
        lambda: gen.getAsmMemCollection(
            par.EMemCollection(
                'stringMem',
                [
                    lex.TString(gram.STRING, 'test 1 '),
                    lex.TString(gram.STRING, 'test 2 '),
                    lex.TString(gram.STRING, 'test 3'),
                ]
            ),
            memBasicX8664Asmap
        ),
        [
            'stringMem: .ascii "test 1 test 2 test 3"'
        ]
    ],
    [
        lambda: gen.getAsmMemSize(
            par.EMemSize(
                'sizeMem',
                '42'
            ),
            memBasicX8664Asmap
        ),
        [
            'sizeMem: .zero 42'
        ]
    ]
]

#
# test functions
#

def runBasicTests(basicTestSets):
    for s in basicTestSets:
        generated = s[0]()
        expected = s[1]

        if (not areListsOfAsmStringsEqual(generated, expected)):
            return False

    return True

def runOffsetTests(offsetTestSets):
    for s in offsetTestSets:
        generated = s[0]()
        expected = s[1]

        if (not areDictStringsEqual(generated, expected)):
            return False

    return True

#
# Run All Tests
#

def runAllTests():
    allPass = True
    allPass = allPass and runBasicTests(basicX8664TestSets)
    allPass = allPass and runBasicTests(sizedBasicX8664TestSets)
    allPass = allPass and runOffsetTests(proOffsetX8664TestSets)
    allPass = allPass and runBasicTests(memBasicX8664TestSets)

    if allPass:
        print('all code generation tests passed')
    else:
        print('at least one code generation test failed')
