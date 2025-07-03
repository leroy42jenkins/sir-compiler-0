import lib.lexer as lex
import test.ut_component_vars as vars

tokenTestPairs = [
    [vars.SOURCE_0, vars.TOKENS_0],
    [vars.SOURCE_1, vars.TOKENS_1],
    [vars.SOURCE_2, vars.TOKENS_2],
    [vars.SOURCE_3, vars.TOKENS_3]
]

def printAllTokens(tokens):
    for t in tokens:
        print(t.toString())

def printSegments(segments):
    for st in segments:
        print(st)

def printBoth(generated, expected):
    print('generated: ')
    printAllTokens(generated)
    print(' ')
    print('expected: ')
    printAllTokens(expected)
    print(' ')

def runTokenTest(source, expected):
    try:
        segments = lex.getSegments(source)
        generated = lex.getCodeTokens(segments)
        generatedLength = len(generated)

        if generatedLength != len(expected):
            print('generated tokens with different length than expected\n')
            printBoth(generated, expected)
            return False

        i = 0
        while i < generatedLength:
            g = generated[i]
            e = expected[i]

            if (g.toString() != e.toString()):
                print('generated token different from expected\n')
                print(g.toString() + ' not equal to ' + e.toString() + '\n')
                printBoth(generated, expected)
                return False

            i += 1

        return True
    except Exception as ex:
        print(ex)
        return False

def runAllTests():
    allPass = True

    for pair in tokenTestPairs:
        allPass = allPass and runTokenTest(pair[0], pair[1])

    if allPass:
        print('all lexer tests passed')
    else:
        print('at least one lexer test failed')
