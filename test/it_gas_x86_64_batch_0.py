import os
import subprocess as sub

import lib.assembly_map as asm
import lib.gen_code as gen

codeText = """
pro add_2_ints x0 x1
    x2 = add x0 x1
    ret x2

pro simple_inc x0
    x1 = add x0 1
    ret x1

pro simple_inc_test x0
    x1 = simple_inc x0
    ret x1

pro sum_lots_of_args x0 x1 x2 x3 x4 x5 x6 x7
    x10 = add x0 x1
    x11 = add x10 x2
    x12 = add x11 x3
    x13 = add x12 x4
    x14 = add x13 x5
    x15 = add x14 x6
    x16 = add x15 x7
    ret x16

pro swap_chars x0 x1
    x2 = [x0]
    x3 = [x1]
    [x0] = x3b
    [x1] = x2b
    ret 0

pro reverse_char_array x0 x1
    @begin
    jige x0 x1 @end
    x2 = [x0]
    x3 = [x1]
    [x0] = x3b
    [x1] = x2b
    x0 = add x0 1
    x1 = sub x1 1
    jump @begin
    @end
    ret 0

mem internal_ar {1 2 3}

pro sum_internal_ar x0
    x1 = internal_ar
    x2 = add x1 16
    x3 = 0
    @begin
    jig x1 x2 @end
    x4 = [x1]
    x3 = add x3 x4
    x1 = add x1 8
    jump @begin
    @end
    ret x3
"""

curDir = os.getcwd()
codeFile = 'it_gas_x86_64_batch_0'
codeFileLoc = './test/' + codeFile

def generateAssembly():
    asmap = asm.GasIntelX8664SystemVMap()
    code = gen.generateCodeLinesFromText(codeText, asmap)
    with open(f"{codeFileLoc}.asm", 'w') as file:
        for line in code:
            file.write(f"{line}\n")

def clearArea():
    for ext in ['.asm', '_c.o', '.o', '.out']:
        name = f"{codeFileLoc}{ext}"
        if os.path.exists(name):
            os.remove(name)

def runCodeTest():
    try:
        generateAssembly()
        sub.run(['as', '-msyntax=intel', '-mnaked-reg', '-o', f"{codeFileLoc}.o", f"{codeFileLoc}.asm"])
        sub.run(['gcc', '-c', '-o', f"{codeFileLoc}_c.o", f"{codeFileLoc}.c"])
        sub.run(['gcc', '-z', 'noexecstack', '-o', f"{codeFileLoc}.out", f"{codeFileLoc}_c.o", f"{codeFileLoc}.o"])
        sub.run([f"{codeFileLoc}.out"])
        clearArea()
    except Exception as ex:
        print('error during code generation')
        print(ex)
