# Simple Intermediate Representation (SIR) Compiler

## Purpose
- To explore and implement compiler concepts. These include mappings of intermediate representation code to assembly code, register allocation and basic optimization.

## Prerequisites
- **Python 3.x**: Source code for compiler written in Python 3.
- **GNU Assembler (as)**: Used to assemble the generated `.asm` file into an object file (`.o`).
  - Part of the GNU Binutils package.
  - Install on Linux: `sudo apt-get install binutils` (Ubuntu/Debian) or `sudo dnf install binutils` (Fedora).
- **GCC**: Used to compile the C file (`.c`) and link object files into an executable (`.out`).
  - Install on Linux: `sudo apt-get install gcc` (Ubuntu/Debian) or `sudo dnf install gcc` (Fedora).
- **Operating System**: A Unix-like system (e.g., Linux, macOS) with support for the above tools.
  - ```run_integration_tests.py``` uses `subprocess.run` to execute `as` and `gcc`, which are typically available on Unix-like systems.

## Command-Line Interface
```compiler.py``` uses `argparse` to handle command-line arguments for configuring the compilation process.

### Basic Command
```bash
python compiler.py -t <target> -s <source> -d <destination>
```

### Arguments
**`-t, --target`**  
- Specifies the target architecture for code generation.  
- Supported value: `x86-64-gas-Intel` (default if not specified).  
- Example: `-t x86-64-gas-Intel`

**`-s, --source`**  
- Path to the input source file (required).  
- The file must exist and be a valid file.  
- Example: `-s input.src`

**`-d, --destination`**  
- Path to the output file where generated assembly code will be written (required).  
- Example: `-d output.asm`

**`-de, --description`**  
- Displays syntax or example information without performing compilation.  
- Options:
  - `syntax`: Prints the syntax description from `lib.grammar.DESCRIPTION_SYNTAX`.
  - `examples`: Prints example usage from `lib.grammar.DESCRIPTION_EXAMPLES`.
  - `all`: Prints both syntax and examples.
- Example: `-de syntax`

### Example Commands
- Compile a source file to assembly for x86-64 (Intel syntax):  
  ```bash
  python compiler.py -t x86-64-gas-Intel -s source.src -d output.asm
  ```

- View syntax description:  
  ```bash
  python compiler.py -de syntax
  ```

- View both syntax and examples:  
  ```bash
  python compiler.py -de all
  ```

## Behavior
1. **Argument Validation**:
   - If `--target` is not provided, defaults to `x86-64-gas-Intel`.
   - If `--source` or `--destination` is missing, the script prints an error message and displays help.
   - If the source file does not exist or is invalid, an exception is raised.
   - If the target architecture is not supported, an exception is raised.

2. **Compilation Process**:
   - Reads the source file content.
   - Uses `lib.gen_code.generateCodeLinesFromText` to generate assembly code based on the target architecture's mapping (from `lib.assembly_map`).
   - Writes the generated code to the destination file, with each line followed by a newline.

3. **Description Mode**:
   - If `--description` is specified, the script outputs the requested information (syntax, examples, or both) and exits without compiling.

## Basic Syntax

**procedures**
- `pro` &rarr; define name
- `ret` &rarr; return value
- `!` &rarr; call procedure

**static memory**
- `mem` &rarr; define name
- `{` &rarr; left brace
- `}` &rarr; right brace

**pointers**
- `[` &rarr; left bracket
- `]` &rarr; right bracket

**unconditional jump**
- `jump`

**conditional jumps**
- `jil` &rarr; less than
- `jile` &rarr; less than or equal to
- `jie` &rarr; equal to
- `jin` &rarr; not equal to
- `jige` &rarr; greater than or equal to
- `jig` &rarr; greater than

**assignment**
- `=` &rarr; set a variable

**unary operators**
- `not` &rarr; logical not

**binary operators**
- `or` &rarr; logical or
- `and` &rarr; logical and
- `xor` &rarr; logical exclusive or
- `add` &rarr; add integers
- `sub` &rarr; subtract integers
- `mul` &rarr; multiply integers
- `div` &rarr; divide integers
- `mod` &rarr; modulus of integers

## Code Examples

```
    pro simple_inc x0
        x1 = add x0 1
        ret x1

    pro simple_inc_test x0
        x1 = simple_inc x0
        ret x1

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
```