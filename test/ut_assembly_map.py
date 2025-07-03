import lib.grammar as gram
import lib.assembly_map as asm

#
# helper functions
#

def printExpressions(expressions):
    for exp in expressions:
        print(exp)

def dump(generated, expected):
    print('generated: ')
    printExpressions(generated)
    print('')
    print('expected: ')
    printExpressions(expected)
    print('')

def areExpressionStringsEqual(generated, expected):
    if generated == expected:
        return True
    
    print('test failed\n')
    print('generated:')
    print(generated)
    print('\nexpected:')
    print(expected)
    print('')
    return False

def areListsOfExpressionsEqual(generated, expected):
    length = len(generated)

    if len(expected) != length:
        print('test failed\n')
        print('generated length: ' + str(length))
        print('\nexpected length: ' + str(len(expected)))
        print('')
        dump(generated, expected)
        return False
        
        
    for i in range(length):
        if (not areExpressionStringsEqual(generated[i], expected[i])):
            dump(generated, expected)
            return False
        
    return True

#
# x86-64 Intel System V test variables and functions
#

GasIntelX8664SystemVTestSets = [
    [
        lambda asmap: asmap.emitStackAllocation(16),
        [
            'sub rsp, 16'
        ]
    ],
    [
        lambda asmap: asmap.emitStackDeallocation(16),
        [
            'add rsp, 16'
        ]
    ],
    [
        lambda asmap: asmap.emitStackLoad('rdi', 8),
        [
            'mov rdi, [rsp + 8]'
        ]
    ],
    [
        lambda asmap: asmap.emitStackStore('rdi', 8),
        [
            'mov [rsp + 8], rdi'
        ]
    ],
    [
        lambda asmap: asmap.emitPush('rdi'),
        [
            'push rdi'
        ]
    ],
    [
        lambda asmap: asmap.emitPop('rdi'),
        [
            'pop rdi'
        ]
    ],
    [
        lambda asmap: asmap.emitLocalLabel('fib', '@test'),
        [
            'fib_test:'
        ]
    ],
    [
        lambda asmap: asmap.emitProName('fib'),
        [
            'fib:'
        ]
    ],
    [
        lambda asmap: asmap.emitJump(gram.JUMP, 'fib', '@test'),
        [
            'jmp fib_test'
        ]
    ],
    [
        lambda asmap: asmap.emitCoJump(gram.JILE, 'rdi', 'rsi', 'fib', '@test'),
        [
            'cmp rdi, rsi',
            'jle fib_test'
        ]
    ],
    [
        lambda asmap: asmap.emitCopy('rdi', 'rdi'),
        []
    ],
    [
        lambda asmap: asmap.emitCopy('rdi', 'rsi'),
        [
            'mov rdi, rsi'
        ]
    ],
    [
        lambda asmap: asmap.emitUnOp('rdi', gram.NOT, 'rdi'),
        [
            'not rdi'
        ]
    ],
    [
        lambda asmap: asmap.emitUnOp('rdi', gram.NOT, 'rsi'),
        [
            'mov rdi, rsi',
            'not rdi'
        ]
    ],
    #
    # binary operations
    #
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.AND, 'rdi', 'rdx'),
        [
            'and rdi, rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.AND, 'rsi', 'rdx'),
        [
            'mov rdi, rsi',
            'and rdi, rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.MUL, 'rsi', 'rdx'),
        [
            'mov rdi, rsi',
            'imul rdi, rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.DIV, 'rsi', 'r8'),
        [
            'push rdx',
            'push rax',
            'mov rax, rsi',
            'xor rdx, rdx',
            'cqo',
            'idiv r8',
            'mov rdi, rax',
            'pop rax',
            'pop rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.DIV, 'rsi', 'rdx'),
        [
            'push rdx',
            'push rax',
            'push r11',
            'mov r11, rdx',
            'mov rax, rsi',
            'xor rdx, rdx',
            'cqo',
            'idiv r11',
            'mov rdi, rax',
            'pop r11',
            'pop rax',
            'pop rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.DIV, 'rdx', 'rsi'),
        [
            'push rdx',
            'push rax',
            'mov rax, rdx',
            'xor rdx, rdx',
            'cqo',
            'idiv rsi',
            'mov rdi, rax',
            'pop rax',
            'pop rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdx', gram.DIV, 'rdi', 'rsi'),
        [
            'push rax',
            'mov rax, rdi',
            'xor rdx, rdx',
            'cqo',
            'idiv rsi',
            'mov rdx, rax',
            'pop rax',
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.DIV, 'rsi', 'rax'),
        [
            'push rdx',
            'push rax',
            'push r11',
            'mov r11, rax',
            'mov rax, rsi',
            'xor rdx, rdx',
            'cqo',
            'idiv r11',
            'mov rdi, rax',
            'pop r11',
            'pop rax',
            'pop rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.DIV, 'rax', 'rsi'),
        [
            'push rdx',
            'push rax',
            'mov rax, rax',
            'xor rdx, rdx',
            'cqo',
            'idiv rsi',
            'mov rdi, rax',
            'pop rax',
            'pop rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rax', gram.DIV, 'rdi', 'rsi'),
        [
            'push rdx',
            'mov rax, rdi',
            'xor rdx, rdx',
            'cqo',
            'idiv rsi',
            'pop rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.MOD, 'rsi', 'r8'),
        [
            'push rdx',
            'push rax',
            'mov rax, rsi',
            'xor rdx, rdx',
            'cqo',
            'idiv r8',
            'mov rdi, rdx',
            'pop rax',
            'pop rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.MOD, 'rsi', 'rdx'),
        [
            'push rdx',
            'push rax',
            'push r11',
            'mov r11, rdx',
            'mov rax, rsi',
            'xor rdx, rdx',
            'cqo',
            'idiv r11',
            'mov rdi, rdx',
            'pop r11',
            'pop rax',
            'pop rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.MOD, 'rdx', 'rsi'),
        [
            'push rdx',
            'push rax',
            'mov rax, rdx',
            'xor rdx, rdx',
            'cqo',
            'idiv rsi',
            'mov rdi, rdx',
            'pop rax',
            'pop rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdx', gram.MOD, 'rdi', 'rsi'),
        [
            'push rax',
            'mov rax, rdi',
            'xor rdx, rdx',
            'cqo',
            'idiv rsi',
            'pop rax',
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.MOD, 'rsi', 'rax'),
        [
            'push rdx',
            'push rax',
            'push r11',
            'mov r11, rax',
            'mov rax, rsi',
            'xor rdx, rdx',
            'cqo',
            'idiv r11',
            'mov rdi, rdx',
            'pop r11',
            'pop rax',
            'pop rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rdi', gram.MOD, 'rax', 'rsi'),
        [
            'push rdx',
            'push rax',
            'mov rax, rax',
            'xor rdx, rdx',
            'cqo',
            'idiv rsi',
            'mov rdi, rdx',
            'pop rax',
            'pop rdx'
        ]
    ],
    [
        lambda asmap: asmap.emitBinOp('rax', gram.MOD, 'rdi', 'rsi'),
        [
            'push rdx',
            'mov rax, rdi',
            'xor rdx, rdx',
            'cqo',
            'idiv rsi',
            'mov rax, rdx',
            'pop rdx'
        ]
    ],
    #
    # end binary operations
    #
    [
        lambda asmap: asmap.emitCall('fun'),
        [
            'call fun'
        ]
    ],
    [
        lambda asmap: asmap.emitRet(),
        [
            'ret'
        ]
    ],
    #
    # optimizations
    #
    [
        lambda asmap: asmap.emitOptimized([
            'mov rax, rax'
        ]),
        []
    ],
    [
        lambda asmap: asmap.emitOptimized([
            'mov rdi, rsi',
            'mov rsi, rdi'
        ]),
        [
            'mov rdi, rsi'
        ]
    ],
    [
        lambda asmap: asmap.emitOptimized([
            'mov rdi, rsi',
            'mov r8, rdi'
        ]),
        [
            'mov rdi, rsi',
            'mov r8, rdi'
        ]
    ]
]

def runGasIntelX8664SystemVTests():
    asmap = asm.GasIntelX8664SystemVMap()

    for s in GasIntelX8664SystemVTestSets:
        generated = s[0](asmap)
        expected = s[1]

        if (not areListsOfExpressionsEqual(generated, expected)):
            return False

    return True

#
# Run All Tests
#

def runAllTests():
    allPass = True
    allPass = allPass and runGasIntelX8664SystemVTests()

    if allPass:
        print('all assembly map tests passed')
    else:
        print('at least one assembly map test failed')
