import lib.grammar as gram
import lib.lexer as lex
import lib.parser as par
import test.ut_component_vars as vars

#
# general helpers
#

def areIndicesEqual(gi, ei):
    if gi != ei:
        print('index returned was not what was expected\n')
        print('generated: ' + str(gi))
        print('expected: ' + str(ei) + '\n')
        return False
    
    return True

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
        return False

    for i in range(length):
        if (not areExpressionStringsEqual(generated[i].toString(), expected[i].toString())):
            return False
        
    return True

def areNumUsesEqual(gu, eu):
    if gu != eu:
        print('usage returned was not what was expected\n')
        print('generated: ' + str(gu))
        print('expected: ' + str(eu) + '\n')
        return False
    
    return True

#
# basic test variables and test functions
#

basicTestSets = [
    [
        0,
        [
            lex.TLabel('@test'),
            lex.TSeparator(gram.SEPARATOR)
        ],
        2,
        par.getELabel,
        [
            2,
            par.ELabel('@test')
        ]
    ],
    [
        0,
        [
            lex.TJump(gram.JUMP),
            lex.TLabel('@test'),
            lex.TSeparator(gram.SEPARATOR)
        ],
        3,
        par.getEJump,
        [
            3,
            par.EJump(gram.JUMP, '@test')
        ]
    ]
]

def runBasicTests():
    for g in basicTestSets:
        gi, generated = g[3](g[0], g[1], g[2])
        ei = g[4][0]
        expected = g[4][1]

        if (not areIndicesEqual(gi, ei)):
            return False

        if (not areExpressionStringsEqual(generated.toString(), expected.toString())):
            return False
        
    return True

#
# comparison jumps
#

[
    [
        0,
        [
            lex.TJump(gram.JIGE),
            lex.TVar('x0', 8),
            lex.TVar('x1', 8),
            lex.TLabel('@test'),
            lex.TSeparator(gram.SEPARATOR)
        ],
        5,
        par.getECoJump,
        [
            5,
            par.ECoJump(gram.JIGE, lex.TVar('x0', 8), lex.TVar('x1', 8), '@test')
        ]
    ]
]

def runCoJumpTests():
    for g in basicTestSets:
        gi, generated = g[3](g[0], g[1], g[2])
        ei = g[4][0]
        expected = g[4][1]

        if (not areIndicesEqual(gi, ei)):
            return False

        if (not areExpressionStringsEqual(generated.toString(), expected.toString())):
            return False
        
    return True

#
# group test variables and test functions
#

groupTestSets = [
    [
        [
            lex.TVar('x1', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TInt(gram.INT, '1')
        ],
        par.getECopy,
        par.ECopy(
            lex.TVar('x1', 8),
            lex.TInt(gram.INT, '1')
        )
    ],
    [
        [
            lex.TVar('x1', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TUnOp(gram.NOT),
            lex.TVar('x0', 8)
        ],
        par.getEUnOp,
        par.EUnOp(
            lex.TVar('x1', 8),
            gram.NOT,
            lex.TVar('x0', 8)
        )
    ],
    [
        [
            lex.TVar('x2', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TBinOp(gram.AND),
            lex.TVar('x0', 8),
            lex.TVar('x1', 8)
        ],
        par.getEBinOp,
        par.EBinOp(
            lex.TVar('x2', 8),
            gram.AND,
            lex.TVar('x0', 8),
            lex.TVar('x1', 8)
        )
    ],
    [
        [
            lex.TVar('x1', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TIdentifier('fib'),
            lex.TVar('x0', 8),
            lex.TInt(gram.INT, '0'),
            lex.TInt(gram.INT, '1')
        ],
        par.getEProCall,
        par.EProCall(
            lex.TVar('x1', 8),
            'fib',
            [
                lex.TVar('x0', 8),
                lex.TInt(gram.INT, '0'),
                lex.TInt(gram.INT, '1')
            ]
        )
    ]
]

def runGroupTests():
    for g in groupTestSets:
        generated = g[1](g[0])
        expected = g[2]

        if (not areExpressionStringsEqual(generated.toString(), expected.toString())):
            return False
        
    return True

#
# pointer test variables and test functions
#

pointerTestSets = [
    [
        [
            lex.TPointLeftB(gram.POINT_LEFT_BRACKET),
            lex.TVar('x0', 8),
            lex.TPointRightB(gram.POINT_RIGHT_BRACKET),
            lex.TAssign(gram.ASSIGN),
            lex.TVar('x1', 8)
        ],
        [
            lex.TPointer('x0'),
            lex.TAssign(gram.ASSIGN),
            lex.TVar('x1', 8)
        ]
    ],
    [
        [
            lex.TVar('x1', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TPointLeftB(gram.POINT_LEFT_BRACKET),
            lex.TVar('x0', 8),
            lex.TPointRightB(gram.POINT_RIGHT_BRACKET)
        ],
        [
            lex.TVar('x1', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TPointer('x0')
        ]
    ]
]

def runPointerTests():
    for p in pointerTestSets:
        generated = par.getParsedPointerGroup(p[0])
        expected = p[1]

        if (not areListsOfExpressionsEqual(generated, expected)):
            return False
        
    return True

#
# assignment test variables and functions
#

assignmentByOpIdTestSets = [
    [
        0,
        [
            lex.TVar('x1', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TInt(gram.INT, '1'),
            lex.TSeparator(gram.SEPARATOR)
        ],
        4,
        [
            4,
            par.ECopy(
                lex.TVar('x1', 8),
                lex.TInt(gram.INT, '1')
            )
        ]
    ],
    [
        0,
        [
            lex.TVar('x1', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TUnOp(gram.NOT),
            lex.TVar('x0', 8),
            lex.TSeparator(gram.SEPARATOR)
        ],
        5,
        [
            5,
            par.EUnOp(
                lex.TVar('x1', 8),
                gram.NOT,
                lex.TVar('x0', 8)
            )
        ]
    ],
    [
        0,
        [
            lex.TVar('x2', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TBinOp(gram.AND),
            lex.TVar('x0', 8),
            lex.TVar('x1', 8),
            lex.TSeparator(gram.SEPARATOR)
        ],
        6,
        [
            6,
            par.EBinOp(
                lex.TVar('x2', 8),
                gram.AND,
                lex.TVar('x0', 8),
                lex.TVar('x1', 8)
            )
        ]
    ],
    [
        0,
        [
            lex.TVar('x1', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TIdentifier('fib'),
            lex.TVar('x0', 8),
            lex.TInt(gram.INT, '0'),
            lex.TInt(gram.INT, '1'),
            lex.TSeparator(gram.SEPARATOR)
        ],
        7,
        [
            7,
            par.EProCall(
                lex.TVar('x1', 8),
                'fib',
                [
                    lex.TVar('x0', 8),
                    lex.TInt(gram.INT, '0'),
                    lex.TInt(gram.INT, '1')
                ]
            )
        ]
    ]
]

def runAssignmentByOpTests():
    for g in assignmentByOpIdTestSets:
        gi, generated = par.getEAssignment(g[0], g[1], g[2])
        ei = g[3][0]
        expected = g[3][1]

        if (not areIndicesEqual(gi, ei)):
            return False

        if (not areExpressionStringsEqual(generated.toString(), expected.toString())):
            return False
                
    return True

#
# procedure line test variables and functions
#

proFirstLineTestSets = [
    [
        0,
        [
            lex.TIdentifier('fibo'),
            lex.TVar('x0', 8),
            lex.TVar('x1', 8),
            lex.TVar('x2', 8),
            lex.TSeparator(gram.SEPARATOR)
        ],
        5,
        [
            5,
            'fibo',
            [
                lex.TVar('x0', 8),
                lex.TVar('x1', 8),
                lex.TVar('x2', 8)
            ]
        ]
    ]
]

def runProFirstLineTests():
    for s in proFirstLineTestSets:
        gi, geName, geParams = par.getEProFirstLine(s[0], s[1], s[2])
        ei = s[3][0]
        eName = s[3][1]
        eParams = s[3][2]

        if (not areIndicesEqual(gi, ei)):
            return False
        
        if geName != eName:
            print('name returned was not was expected\n')
            return False
        
        if (not areListsOfExpressionsEqual(geParams, eParams)):
            return False
        
    return True

proLastLineTestSets = [
    [
        0,
        [
            lex.TVar('x2', 8),
            lex.TSeparator(gram.SEPARATOR)
        ],
        2,
        [
            2,
            lex.TVar('x2', 8)
        ]
    ],
    [
        0,
        [
            lex.TInt(gram.INT, '0'),
            lex.TSeparator(gram.SEPARATOR)
        ],
        2,
        [
            2,
            lex.TInt(gram.INT, '0')
        ]
    ]
]

def runProLastLineTests():
    for s in proLastLineTestSets:
        gi, geRet = par.getEProLastLine(s[0], s[1], s[2])
        ei = s[3][0]
        eRet = s[3][1]

        if (not areIndicesEqual(gi, ei)):
            return False
        
        if (not areExpressionStringsEqual(geRet.toString(), eRet.toString())):
            return False
                
    return True

proTestSets = [
    [
        0,
        [
            lex.TProId('pro'),
            lex.TIdentifier('addOne'),
            lex.TVar('x0', 8),
            lex.TVar('x1', 8),
            lex.TSeparator(gram.SEPARATOR),
            lex.TLabel('@top'),
            lex.TSeparator(gram.SEPARATOR),
            lex.TCoJump('jile'),
            lex.TVar('x0', 8),
            lex.TInt(gram.INT, '0'),
            lex.TLabel('@end'),
            lex.TSeparator(gram.SEPARATOR),
            lex.TVar('x1', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TBinOp('add'),
            lex.TVar('x1', 8),
            lex.TInt(gram.INT, '1'),
            lex.TSeparator(gram.SEPARATOR),
            lex.TVar('x0', 8),
            lex.TAssign(gram.ASSIGN),
            lex.TBinOp('sub'),
            lex.TVar('x0', 8),
            lex.TInt(gram.INT, '1'),
            lex.TSeparator(gram.SEPARATOR),
            lex.TJump('jump'),
            lex.TLabel('@top'),
            lex.TSeparator(gram.SEPARATOR),
            lex.TLabel('@end'),
            lex.TSeparator(gram.SEPARATOR),
            lex.TProRet('ret'),
            lex.TVar('x1', 8),
            lex.TSeparator(gram.SEPARATOR)
        ],
        par.EPro(
            'addOne',
            [
                lex.TVar('x0', 8),
                lex.TVar('x1', 8)
            ],
            [
                par.ELabel('@top'),
                par.ECoJump(
                    gram.JILE, lex.TVar('x0', 8),
                    lex.TInt(gram.INT, '0'), '@end'
                ),
                par.EBinOp(
                    lex.TVar('x1', 8), gram.ADD,
                    lex.TVar('x1', 8), lex.TInt(gram.INT, '1')
                ),
                par.EBinOp(
                    lex.TVar('x0', 8), gram.SUB,
                    lex.TVar('x0', 8), lex.TInt(gram.INT, '1')
                ),
                par.EJump(gram.JUMP, '@top'),
                par.ELabel('@end')
            ],
            lex.TVar('x1', 8)
        )
    ]
]

def runProTests():
    for s in proTestSets:
        length = len(s[1])
        gi, gePro = par.getEPro(s[0], s[1], length)
        ei = length
        ePro = s[2]

        if (not areIndicesEqual(gi, ei)):
            return False
        
        if (not areExpressionStringsEqual(gePro.toString(), ePro.toString())):
            return False
        
    return True

#
# memory test variables and functions
#

memCollectionTestSets = [
    [
        'ar',
        0,
        [
            lex.TInt(gram.INT, '1'),
            lex.TInt(gram.INT, '2'),
            lex.TInt(gram.INT, '3'),
            lex.TMemRightB(gram.MEM_RIGHT_BRACE),
            lex.TSeparator(gram.SEPARATOR)
        ],
        5,
        [
            5,
            par.EMemCollection(
                'ar',
                [
                    lex.TInt(gram.INT, '1'),
                    lex.TInt(gram.INT, '2'),
                    lex.TInt(gram.INT, '3')
                ]
            )
        ]
    ],
    [
        'ar',
        0,
        [
            lex.TSeparator(gram.SEPARATOR),
            lex.TInt(gram.INT, '1'),
            lex.TSeparator(gram.SEPARATOR),
            lex.TInt(gram.INT, '2'),
            lex.TSeparator(gram.SEPARATOR),
            lex.TInt(gram.INT, '3'),
            lex.TSeparator(gram.SEPARATOR),
            lex.TMemRightB(gram.MEM_RIGHT_BRACE),
            lex.TSeparator(gram.SEPARATOR)
        ],
        9,
        [
            9,
            par.EMemCollection(
                'ar',
                [
                    lex.TInt(gram.INT, '1'),
                    lex.TInt(gram.INT, '2'),
                    lex.TInt(gram.INT, '3')
                ]
            )
        ]
    ]
]

def runMemCollectionTests():
    for m in memCollectionTestSets:
        gi, geMem = par.getEMemCollection(m[0], m[1], m[2], m[3])
        ei = m[4][0]
        eMem = m[4][1]

        if (not areIndicesEqual(gi, ei)):
            return False
        
        if (not areExpressionStringsEqual(geMem.toString(), eMem.toString())):
            return False
        
    return True

memSizeTestSets = [
    [
        'ar',
        0,
        [
            lex.TInt(gram.INT, '42'),
            lex.TSeparator(gram.SEPARATOR)
        ],
        2,
        [
            2,
            par.EMemSize(
                'ar',
                '42'
            )
        ]
    ]
]

def runMemSizeTests():
    for m in memSizeTestSets:
        gi, geMem = par.getEMemSize(m[0], m[1], m[2], m[3])
        ei = m[4][0]
        eMem = m[4][1]

        if (not areIndicesEqual(gi, ei)):
            return False
        
        if (not areExpressionStringsEqual(geMem.toString(), eMem.toString())):
            return False
        
    return True

memTestSets = [
    [
        0,
        [
            lex.TIdentifier('ar'),
            lex.TMemLeftB(gram.MEM_LEFT_BRACE),
            lex.TInt(gram.INT, '1'),
            lex.TInt(gram.INT, '2'),
            lex.TInt(gram.INT, '3'),
            lex.TMemRightB(gram.MEM_RIGHT_BRACE),
            lex.TSeparator(gram.SEPARATOR)
        ],
        7,
        [
            7,
            par.EMemCollection(
                'ar',
                [
                    lex.TInt(gram.INT, '1'),
                    lex.TInt(gram.INT, '2'),
                    lex.TInt(gram.INT, '3')
                ]
            )
        ]
    ],
    [
        0,
        [
            lex.TIdentifier('ar'),
            lex.TInt(gram.INT, '42'),
            lex.TSeparator(gram.SEPARATOR)
        ],
        3,
        [
            3,
            par.EMemSize(
                'ar',
                '42'
            )
        ]
    ]
]

def runMemTests():
    for m in memTestSets:
        gi, geMem = par.getEMem(m[0], m[1], m[2])
        ei = m[3][0]
        eMem = m[3][1]

        if (not areIndicesEqual(gi, ei)):
            return False
        
        if (not areExpressionStringsEqual(geMem.toString(), eMem.toString())):
            return False
        
    return True

#
# Expression Tests
#

expressionTestSets = [
    [vars.TOKENS_0, vars.EXPRESSIONS_0],
    [vars.TOKENS_1, vars.EXPRESSIONS_1],
    [vars.TOKENS_2, vars.EXPRESSIONS_2],
    [vars.TOKENS_3, vars.EXPRESSIONS_3]
]

def runExpressionTests():
    for s in expressionTestSets:
        generated = par.getExpressions(s[0])
        expected = s[1]

        if (not areListsOfExpressionsEqual(generated, expected)):
            return False
        
    return True

#
# Run All Tests
#

def runAllTests():
    allPass = True
    allPass = allPass and runBasicTests()
    allPass = allPass and runGroupTests()
    allPass = allPass and runPointerTests()
    allPass = allPass and runAssignmentByOpTests()
    allPass = allPass and runProFirstLineTests()
    allPass = allPass and runProLastLineTests()
    allPass = allPass and runProTests()
    allPass = allPass and runMemCollectionTests()
    allPass = allPass and runMemSizeTests()
    allPass = allPass and runMemTests()
    allPass = allPass and runExpressionTests()

    if allPass:
        print('all parser tests passed')
    else:
        print('at least one parser test failed')
