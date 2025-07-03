import argparse as arg
from pathlib import Path

import lib.grammar as gram
import lib.assembly_map as asm
import lib.gen_code as gen

X86_64_GAS_INTEL = 'x86-64-gas-Intel'

TARGETS = [X86_64_GAS_INTEL]

TARGETS_MAP = {
    X86_64_GAS_INTEL: lambda: asm.GasIntelX8664SystemVMap()
}

def doWork(target, source, destination):
    if target not in TARGETS_MAP:
        raise Exception('target architecture not found')
    
    asmap = TARGETS_MAP[target]()

    sourcePath = Path(source)

    if (not sourcePath.exists()) or (not sourcePath.is_file()):
        raise Exception('invalid source file path')
    
    codeText = ''
    with open(source, 'r') as file:
        lines = file.readlines()
        codeText = '\n'.join(lines)
    
    code = gen.generateCodeLinesFromText(codeText, asmap)

    with open(destination, 'w') as file:
        for line in code:
            file.write(f"{line}\n")
    
def main():
    parg = arg.ArgumentParser(description='basic compiler options')
    parg.add_argument('-t', '--target', type=str, help='target architecture (' + ', '.join(TARGETS) + ')')
    parg.add_argument('-s', '--source', type=str, help='source file')
    parg.add_argument('-d', '--destination', type=str, help='destination file')
    parg.add_argument('-de', '--description', type=str, help='description ()')

    pargs = parg.parse_args()

    if pargs.description == 'syntax':
        print(gram.DESCRIPTION_SYNTAX)
        return
    elif pargs.description == 'examples':
        print(gram.DESCRIPTION_EXAMPLES)
        return
    elif pargs.description == 'all':
        print(gram.DESCRIPTION_SYNTAX)
        print(gram.DESCRIPTION_EXAMPLES)
        return

    target = ''
    source = ''
    destination = ''

    if pargs.target:
        target = pargs.target
    else:
        target = X86_64_GAS_INTEL
    
    if pargs.source:
        source = pargs.source
    else:
        print('source file must be specified')
    
    if pargs.destination:
        destination = pargs.destination
    else:
        print('destination file must be specified')
    
    if target and source and destination:
        doWork(target, source, destination)
    else:
        parg.print_help()

if __name__ == '__main__':
    main()
