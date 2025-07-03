import lib.grammar as gram
import lib.lexer as lex
import lib.parser as par

#
# Variables
#

SOURCE_0 = """
pro inc x0
    x0 = add x0 1
    ret x0

pro addNext x0
    x1 = inc x0
    x0 = add x0 x1
    ret x0
"""

TOKENS_0 = [
    lex.TSeparator(gram.SEPARATOR),
    lex.TProId('pro'),
    lex.TIdentifier('inc'),
    lex.TVar('x0', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TVar('x0', 8),
    lex.TAssign(gram.ASSIGN),
    lex.TBinOp('add'),
    lex.TVar('x0', 8),
    lex.TInt(gram.INT, '1'),
    lex.TSeparator(gram.SEPARATOR),
    lex.TProRet('ret'),
    lex.TVar('x0', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TSeparator(gram.SEPARATOR),
    lex.TProId('pro'),
    lex.TIdentifier('addNext'),
    lex.TVar('x0', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TVar('x1', 8),
    lex.TAssign(gram.ASSIGN),
    lex.TIdentifier('inc'),
    lex.TVar('x0', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TVar('x0', 8),
    lex.TAssign(gram.ASSIGN),
    lex.TBinOp('add'),
    lex.TVar('x0', 8),
    lex.TVar('x1', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TProRet('ret'),
    lex.TVar('x0', 8),
    lex.TSeparator(gram.SEPARATOR)
]

EXPRESSIONS_0 = [
    par.EPro(
        'inc',
        [
            lex.TVar('x0', 8)
        ],
        [
            par.EBinOp(
                lex.TVar('x0', 8), gram.ADD,
                lex.TVar('x0', 8), lex.TInt(gram.INT, '1')
            )
        ],
        lex.TVar('x0', 8)
    ),
    par.EPro(
        'addNext',
        [
            lex.TVar('x0', 8)
        ],
        [
            par.EProCall(
                lex.TVar('x1', 8),
                'inc',
                [
                    lex.TVar('x0', 8)
                ]
            ),
            par.EBinOp(
                lex.TVar('x0', 8), gram.ADD,
                lex.TVar('x0', 8), lex.TVar('x1', 8)
            )
        ],
        lex.TVar('x0', 8)
    )
]

SOURCE_1 = """
pro addOne x0 x1
    @top
    jile x0 0 @end
    x1 = add x1 1
    x0 = sub x0 1
    jump @top
    @end
    ret x1
"""

TOKENS_1 = [
    lex.TSeparator(gram.SEPARATOR),
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
]

EXPRESSIONS_1 = [
    par.EPro(
        'addOne',
        [
            lex.TVar('x0', 8), lex.TVar('x1', 8)
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

SOURCE_2 = """
mem ar {1 2 3}

pro setAr x0 x1
    x2 = ar
    x2 = add x2 x0
    [x2] = x1
    ret 0
"""

TOKENS_2 = [
    lex.TSeparator(gram.SEPARATOR),
    lex.TMemId(gram.MEM_ID),
    lex.TIdentifier('ar'),
    lex.TMemLeftB(gram.MEM_LEFT_BRACE),
    lex.TInt(gram.INT, '1'),
    lex.TInt(gram.INT, '2'),
    lex.TInt(gram.INT, '3'),
    lex.TMemRightB(gram.MEM_RIGHT_BRACE),
    lex.TSeparator(gram.SEPARATOR),
    lex.TSeparator(gram.SEPARATOR),
    lex.TProId('pro'),
    lex.TIdentifier('setAr'),
    lex.TVar('x0', 8),
    lex.TVar('x1', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TVar('x2', 8),
    lex.TAssign(gram.ASSIGN),
    lex.TIdentifier('ar'),
    lex.TSeparator(gram.SEPARATOR),
    lex.TVar('x2', 8),
    lex.TAssign(gram.ASSIGN),
    lex.TBinOp('add'),
    lex.TVar('x2', 8),
    lex.TVar('x0', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TPointLeftB(gram.POINT_LEFT_BRACKET),
    lex.TVar('x2', 8),
    lex.TPointRightB(gram.POINT_RIGHT_BRACKET),
    lex.TAssign(gram.ASSIGN),
    lex.TVar('x1', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TProRet('ret'),
    lex.TInt(gram.INT, '0'),
    lex.TSeparator(gram.SEPARATOR)
]

EXPRESSIONS_2 = [
    par.EMemCollection(
        'ar',
        [
            lex.TInt(gram.INT, '1'),
            lex.TInt(gram.INT, '2'),
            lex.TInt(gram.INT, '3')
        ]
    ),
    par.EPro(
        'setAr',
        [
            lex.TVar('x0', 8), lex.TVar('x1', 8)
        ],
        [
            par.ECopy(
                lex.TVar('x2', 8), lex.TIdentifier('ar')
            ),
            par.EBinOp(
                lex.TVar('x2', 8), gram.ADD,
                lex.TVar('x2', 8), lex.TVar('x0', 8)
            ),
            par.ECopy(
                lex.TPointer('x2'), lex.TVar('x1', 8)
            ),
        ],
        lex.TInt(gram.INT, '0')
    )
]

SOURCE_3 = """
pro id x0
    ret x0

pro runTest x0 x1
    x2 = !x0 x1
    ret x2
"""

TOKENS_3 = [
    lex.TSeparator(gram.SEPARATOR),
    lex.TProId('pro'),
    lex.TIdentifier('id'),
    lex.TVar('x0', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TProRet('ret'),
    lex.TVar('x0', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TSeparator(gram.SEPARATOR),
    lex.TProId('pro'),
    lex.TIdentifier('runTest'),
    lex.TVar('x0', 8),
    lex.TVar('x1', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TVar('x2', 8),
    lex.TAssign(gram.ASSIGN),
    lex.TIdentifier('!x0'),
    lex.TVar('x1', 8),
    lex.TSeparator(gram.SEPARATOR),
    lex.TProRet('ret'),
    lex.TVar('x2', 8),
    lex.TSeparator(gram.SEPARATOR)
]

EXPRESSIONS_3 = [
    par.EPro(
        'id',
        [
            lex.TVar('x0', 8)
        ],
        [],
        lex.TVar('x0', 8)
    ),
    par.EPro(
        'runTest',
        [
            lex.TVar('x0', 8), lex.TVar('x1', 8)
        ],
        [
            par.EProCall(
                lex.TVar('x2', 8),
                '!x0',
                [
                    lex.TVar('x1', 8)
                ]
            )
        ],
        lex.TVar('x2', 8)
    )
]
