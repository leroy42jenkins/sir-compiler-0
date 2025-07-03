import test.ut_lexer as lex
import test.ut_parser as par
import test.ut_assembly_map as asm
import test.ut_simple_allocator as sar
import test.ut_gen_code as gen
import test.ut_gen_pro_code as pro
import test.ut_gen_combo_code as combo

lex.runAllTests()
par.runAllTests()
asm.runAllTests()
sar.runAllTests()
gen.runAllTests()
pro.runAllTests()
combo.runAllTests()