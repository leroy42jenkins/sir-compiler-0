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

#
# basic tests
#

SOURCE_CODE_0 = """
pro simple_test_0 x0
    x1 = add x0 1
    x2 = add x1 1
    x3 = add x2 1
    x4 = add x3 1
    ret x4
"""

TARGET_CODE_0 = """
.section .text

.global simple_test_0

simple_test_0:
mov rsi, rdi
add rsi, 1
mov rdx, rsi
add rdx, 1
mov rcx, rdx
add rcx, 1
mov r8, rcx
add r8, 1
mov rax, r8
ret
"""

SOURCE_CODE_1 = """
pro simple_test_1 x0 x1 x2 x3 x4 x5 x6 x7
    x0 = add x0 x1
    x0 = add x0 x2
    x0 = add x0 x3
    x0 = add x0 x4
    x0 = add x0 x5
    x0 = add x0 x6
    x0 = add x0 x7
    ret x0
"""

TARGET_CODE_1 = """
.section .text

.global simple_test_1

simple_test_1:
add rdi, rsi
add rdi, rdx
add rdi, rcx
add rdi, r8
add rdi, r9
mov r11, [rsp + 8]
add rdi, r11
mov r11, [rsp + 16]
add rdi, r11
mov rax, rdi
ret
"""

SOURCE_CODE_2 = """
pro simple_inc_2 x0
    x1 = add x0 1
    ret x1

pro simple_test_2 x0
    x1 = add x0 2
    x2 = simple_inc_2 x1
    ret x2
"""

TARGET_CODE_2 = """
.section .text

.global simple_inc_2
.global simple_test_2

simple_inc_2:
mov rsi, rdi
add rsi, 1
mov rax, rsi
ret

simple_test_2:
sub rsp, 32
mov rsi, rdi
add rsi, 2
mov [rsp], rdi
mov [rsp + 8], rsi
mov [rsp + 16], rdx
mov rdi, rsi
call simple_inc_2
mov rdi, [rsp]
mov rsi, [rsp + 8]
mov rdx, [rsp + 16]
mov rdx, rax
add rsp, 32
ret
"""

SOURCE_CODE_3 = """
pro simple_test_3 x0 x1 x2 x3 x4 x5 x6 x7
    x10 = add x0 x1
    x11 = add x10 x2
    x12 = add x11 x3
    x13 = add x12 x4
    x14 = add x13 x5
    x15 = add x14 x6
    x16 = add x15 x7
    ret x16
"""

TARGET_CODE_3 = """
.section .text

.global simple_test_3

simple_test_3:
sub rsp, 48
mov [rsp], rbx
mov [rsp + 8], r12
mov [rsp + 16], r13
mov [rsp + 24], r14
mov [rsp + 32], r15
mov rbx, rdi
add rbx, rsi
mov r12, rbx
add r12, rdx
mov r13, r12
add r13, rcx
mov r14, r13
add r14, r8
mov r15, r14
add r15, r9
mov r11, [rsp + 56]
mov rbx, r15
add rbx, r11
mov r11, [rsp + 64]
mov rdi, rbx
add rdi, r11
mov rax, rdi
mov rbx, [rsp]
mov r12, [rsp + 8]
mov r13, [rsp + 16]
mov r14, [rsp + 24]
mov r15, [rsp + 32]
add rsp, 48
ret
"""

SOURCE_CODE_4 = """
pro simple_inc_4 x0
    x1 = add x0 1
    ret x1

pro simple_test_4 x0 x1 x2 x3 x4 x5 x6 x7 x8
    x10 = add x0 x1
    x11 = add x10 x2
    x12 = add x11 x3
    x13 = add x12 x4
    x14 = add x13 x5
    x15 = add x14 x6
    x16 = add x15 x7
    x17 = add x16 x8
    x18 = simple_inc_4 x17
    ret x18
"""

TARGET_CODE_4 = """
.section .text

.global simple_inc_4
.global simple_test_4

simple_inc_4:
mov rsi, rdi
add rsi, 1
mov rax, rsi
ret

simple_test_4:
sub rsp, 96
mov [rsp], rbx
mov [rsp + 8], r12
mov [rsp + 16], r13
mov [rsp + 24], r14
mov [rsp + 32], r15
mov rbx, rdi
add rbx, rsi
mov r12, rbx
add r12, rdx
mov r13, r12
add r13, rcx
mov r14, r13
add r14, r8
mov r15, r14
add r15, r9
mov r11, [rsp + 104]
mov rbx, r15
add rbx, r11
mov r11, [rsp + 112]
mov rdi, rbx
add rdi, r11
mov r11, [rsp + 120]
mov rbx, rdi
add rbx, r11
mov [rsp + 40], rdi
mov [rsp + 48], rsi
mov [rsp + 56], rdx
mov [rsp + 64], rcx
mov [rsp + 72], r8
mov [rsp + 80], r9
mov rdi, rbx
call simple_inc_4
mov rdi, [rsp + 40]
mov rsi, [rsp + 48]
mov rdx, [rsp + 56]
mov rcx, [rsp + 64]
mov r8, [rsp + 72]
mov r9, [rsp + 80]
mov rdi, rax
mov rbx, [rsp]
mov r12, [rsp + 8]
mov r13, [rsp + 16]
mov r14, [rsp + 24]
mov r15, [rsp + 32]
add rsp, 96
ret
"""

SOURCE_CODE_5 = """
pro simple_args_5 x0 x1 x2 x3 x4 x5 x6 x7 x8
    x10 = add x0 x1
    x11 = add x10 x2
    x12 = add x11 x3
    x13 = add x12 x4
    x14 = add x13 x5
    x15 = add x14 x6
    x16 = add x15 x7
    x17 = add x16 x8
    ret x17

pro simple_test_5 x0
    x1 = 1
    x2 = 2
    x3 = 3
    x4 = 4
    x5 = 5
    x6 = 6
    x7 = 7
    x8 = 8
    x9 = simple_args_5 x0 x1 x2 x3 x4 x5 x6 x7 x8
    ret x9
"""

TARGET_CODE_5 = """
.section .text

.global simple_args_5
.global simple_test_5

simple_args_5:
sub rsp, 48
mov [rsp], rbx
mov [rsp + 8], r12
mov [rsp + 16], r13
mov [rsp + 24], r14
mov [rsp + 32], r15
mov rbx, rdi
add rbx, rsi
mov r12, rbx
add r12, rdx
mov r13, r12
add r13, rcx
mov r14, r13
add r14, r8
mov r15, r14
add r15, r9
mov r11, [rsp + 56]
mov rbx, r15
add rbx, r11
mov r11, [rsp + 64]
mov rdi, rbx
add rdi, r11
mov r11, [rsp + 72]
mov rbx, rdi
add rbx, r11
mov rax, rbx
mov rbx, [rsp]
mov r12, [rsp + 8]
mov r13, [rsp + 16]
mov r14, [rsp + 24]
mov r15, [rsp + 32]
add rsp, 48
ret

simple_test_5:
sub rsp, 80
mov [rsp], rbx
mov [rsp + 8], r12
mov [rsp + 16], r13
mov [rsp + 24], r14
mov rsi, 1
mov rdx, 2
mov rcx, 3
mov r8, 4
mov r9, 5
mov rbx, 6
mov r12, 7
mov r13, 8
mov [rsp + 32], rdi
mov [rsp + 40], rsi
mov [rsp + 48], rdx
mov [rsp + 56], rcx
mov [rsp + 64], r8
mov [rsp + 72], r9
mov rdi, [rsp + 32]
mov rsi, [rsp + 40]
mov rdx, [rsp + 48]
mov rcx, [rsp + 56]
mov r8, [rsp + 64]
mov r9, [rsp + 72]
push r13
push r12
push rbx
call simple_args_5
add rsp, 24
mov rdi, [rsp + 32]
mov rsi, [rsp + 40]
mov rdx, [rsp + 48]
mov rcx, [rsp + 56]
mov r8, [rsp + 64]
mov r9, [rsp + 72]
mov r14, rax
mov rbx, [rsp]
mov r12, [rsp + 8]
mov r13, [rsp + 16]
mov r14, [rsp + 24]
add rsp, 80
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
    asmap = asm.GasIntelX8664SystemVMap()

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
        print('all combination code generation tests passed')
    else:
        print('at least one combination code generation test failed')
