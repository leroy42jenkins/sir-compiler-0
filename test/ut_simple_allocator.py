import lib.grammar as gram
import lib.lexer as lex
import lib.parser as par
import lib.simple_allocator as sar

#
# test helpers
#

def printDict(di):
    for k in di:
        v = di[k]
        print('{ ' + str(k) + ' : ' + str(v) + ' }')

def printResultDicts(generated, expected):
    print('generated:')
    printDict(generated)
    print('')
    print('expected:')
    printDict(expected)
    print('')

def areMapsEqual(generated, expected):
    length = len(generated)
    expectedLength = len(expected)

    if expectedLength != length:
        print('test failed\n')
        print('generated length: ' + str(length))
        print('expected length: ' + str(expectedLength) + '\n')
        printResultDicts(generated, expected)
        return False

    for var in expected:
        reg = expected[var]
        geReg = generated[var]
        if geReg != reg:
            print('test failed\n')
            print('generated: ' + geReg)
            print('expected: ' + reg)
            print('for ' + var + '\n')
            printResultDicts(generated, expected)
            return False
    
    return True

def runTest(testSet):
    allRegs = testSet[0]
    pro = testSet[1]

    generatedMap = sar.getAssignmentDict(allRegs, pro, 2, lex.TVar)
    expectedMap = testSet[2][0]

    return areMapsEqual(generatedMap, expectedMap)
    
#
# test variables and functions
#

PRO_FUN_INT_0 = par.EPro(
    'fun',
    [
        lex.TVar('x0', 8)
    ],
    [
        par.EBinOp(
            lex.TVar('x0', 8), gram.ADD,
            lex.TVar('x0', 8), lex.TInt(gram.INT, '1')
        ),
        par.ECopy(
            lex.TVar('x1', 8), lex.TInt(gram.INT, '1')
        ),
        par.EBinOp(
            lex.TVar('x2', 8), gram.ADD,
            lex.TVar('x0', 8), lex.TVar('x1', 8)
        ),
        par.ECopy(
            lex.TVar('x3', 8), lex.TInt(gram.INT, '1')
        ),
        par.EBinOp(
            lex.TVar('x4', 8), gram.ADD,
            lex.TVar('x2', 8), lex.TVar('x3', 8)
        ),
        par.ECopy(
            lex.TVar('x5', 8), lex.TInt(gram.INT, '1')
        ),
        par.EBinOp(
            lex.TVar('x6', 8), gram.ADD,
            lex.TVar('x4', 8), lex.TVar('x5', 8)
        )
    ],
    lex.TVar('x0', 8)
)

PRO_FUN_INT_1 = par.EPro(
    'fun',
    [
        lex.TVar('x0', 8), lex.TVar('x1', 8),
        lex.TVar('x2', 8), lex.TVar('x3', 8)
    ],
    [
        par.EBinOp(
            lex.TVar('x0', 8), gram.ADD,
            lex.TVar('x0', 8), lex.TVar('x1', 8)
        ),
        par.EBinOp(
            lex.TVar('x0', 8), gram.ADD,
            lex.TVar('x0', 8), lex.TVar('x2', 8)
        ),
        par.EBinOp(
            lex.TVar('x0', 8), gram.ADD,
            lex.TVar('x0', 8), lex.TVar('x3', 8)
        ),
        par.ECopy(
            lex.TVar('x4', 8), lex.TInt(gram.INT, '1')
        ),
        par.EBinOp(
            lex.TVar('x0', 8), gram.ADD,
            lex.TVar('x0', 8), lex.TVar('x4', 8)
        )
    ],
    lex.TVar('x0', 8)
)

PRO_FUN_POINTER_0 = par.EPro(
    'fun',
    [
        lex.TVar('x0', 8), lex.TVar('x1', 8)
    ],
    [
        par.ECopy(
            lex.TVar('x2', 8), lex.TPointer('x0')
        ),
        par.ECopy(
            lex.TVar('x3', 8), lex.TPointer('x1')
        ),
        par.EBinOp(
            lex.TVar('x4', 8), gram.ADD,
            lex.TVar('x2', 8), lex.TVar('x3', 8)
        )
    ],
    lex.TVar('x4', 8)
)

simpleTestSets = [
    [
        [
            'r1', 'r2'
        ],
        PRO_FUN_INT_0,
        [
            {
                'x0': 'r1',
                'x1': 'r2',
                'x2': 'spill',
                'x3': 'r1',
                'x4': 'r2',
                'x5': 'r1',
                'x6': 'spill'
            },
            {}
        ]
    ],
    [
        [
            'r1', 'r2'
        ],
        PRO_FUN_INT_1,
        [
            {
                'x0': 'r1',
                'x1': 'r2',
                'x2': 'over',
                'x3': 'over',
                'x4': 'r2',
            },
            {}
        ]
    ],
    [
        [
            'r1'
        ],
        PRO_FUN_INT_0,
        [
            {
                'x0': 'r1',
                'x1': 'spill',
                'x2': 'spill',
                'x3': 'r1',
                'x4': 'spill',
                'x5': 'r1',
                'x6': 'spill'
            },
            {}
        ]
    ],
    [
        [
            'r1', 'r2', 'r3'
        ],
        PRO_FUN_INT_0,
        [
            {
                'x0': 'r1',
                'x1': 'r2',
                'x2': 'r3',
                'x3': 'r1',
                'x4': 'r2',
                'x5': 'r1',
                'x6': 'r3'
            },
            {}
        ]
    ],
    [
        [
            'r1', 'r2'
        ],
        PRO_FUN_POINTER_0,
        [
            {
                'x0': 'r1',
                'x1': 'r2',
                'x2': 'spill',
                'x3': 'r1',
                'x4': 'r2'
            },
            {}
        ]
    ],
    [
        [
            'r1', 'r2', 'r3'
        ],
        PRO_FUN_POINTER_0,
        [
            {
                'x0': 'r1',
                'x1': 'r2',
                'x2': 'r3',
                'x3': 'r1',
                'x4': 'r2'
            },
            {}
        ]
    ]
]

def runSimpleTests():
    for s in simpleTestSets:
        if (not runTest(s)):
            return False
        
    return True

#
# Run All Tests
#

def runAllTests():
    allPass = True
    allPass = runSimpleTests()

    if allPass:
        print('all simple allocator tests passed')
    else:
        print('at least one simple allocator test failed')
