import lib.grammar as gram
import lib.lexer as lex
import lib.parser as par
import lib.simple_allocator as sar
import lib.assembly_map as asm

#
# Assignment Helpers
#

OFFSET_STACK = "offset_stack"

def getOffsetVarKey(name):
    return 'v_' + name

def getOffsetRegKey(reg):
    return 'r_' + reg

def getGeneralRegUsed(generalDict):
    isRegUsed = {}

    for name in generalDict:
        reg = generalDict[name]
        if reg != sar.SPILL and reg != sar.OVER:
            isRegUsed[reg] = True

    return isRegUsed

def getOffsetDict(pro, asmap, generalDict):
    offsetDict = {}
    offsetCur = 0
    offsetMax = offsetCur
    offsetNeg = -8

    for name in generalDict:
        reg = generalDict[name]
        if reg == sar.SPILL:
            key = getOffsetVarKey(name)
            offsetDict[key] = offsetCur
            offsetCur += 8
        elif reg == sar.OVER:
            key = getOffsetVarKey(name)
            offsetDict[key] = offsetNeg
            offsetNeg -= 8

    if pro.usesInt:
        isRegUsed = getGeneralRegUsed(generalDict)
        
        callees = asmap.getCalleeSavedRegs()
        for reg in callees:
            if reg in isRegUsed:
                offsetDict[getOffsetRegKey(reg)] = offsetCur
                offsetCur += 8
        
        if not pro.isLeaf:
            callers = asmap.getCallerSavedRegs()
            for reg in callers:
                if reg in isRegUsed:
                    offsetDict[getOffsetRegKey(reg)] = offsetCur
                    offsetCur += 8

    offsetMax = offsetCur
    alignment = asmap.getByteAlignment()

    while (offsetMax % alignment) != 0:
        offsetMax += 8

    offsetDict[OFFSET_STACK] = offsetMax

    for name in offsetDict:
        if name != OFFSET_STACK:
            offset = offsetDict[name]
            if offset < 0:
                offsetDict[name] = offsetMax + abs(offset)

    return offsetDict

def getStackOffset(assignments):
    return assignments.offset[OFFSET_STACK]

#
# General Helpers
#

def getAsmPointerVal(param, assignments):
    name = param.name

    if name in assignments.generalReg:
        return assignments.generalReg[name]

    return name

def getAsmValWidth(asmap, val, width):
    match width:
        case 8:
            return val
        case 4:
            return asmap.getDoubleWordReg(val)
        case 2:
            return asmap.getWordReg(val)
        case 1:
            return asmap.getByteReg(val)
        case _:
            return val

def getAsmVal(param, asmap, assignments):
    # general registers
    if isinstance(param, lex.TVar) and (param.name in assignments.generalReg):
        val = assignments.generalReg[param.name]
        
        if val != sar.SPILL and val != sar.OVER:
            return getAsmValWidth(asmap, val, param.width)
        
        return val

    # literals
    if par.isValidTokenInTypeList(param, par.LITERAL_TYPES):
        return param.value
    
    return param.name

#
# Statement Functions
#

def getAsmLocalLabel(exp, proName, asmap):
    return asmap.emitLocalLabel(proName, exp.name)

def getAsmJump(exp, proName, asmap):
    return asmap.emitJump(exp.name, proName, exp.labelName)

def getAsmCoJump(exp, proName, asmap, assignments):
    code = []
    intermediate = asmap.getIntermediateRegs()
    left = getAsmVal(exp.left, asmap, assignments)
    right = getAsmVal(exp.right, asmap, assignments)
    
    if left == sar.SPILL or left == sar.OVER:
        leftName = exp.left.name
        leftOffset = assignments.offset[getOffsetVarKey(leftName)]
        left = getAsmValWidth(asmap, intermediate[0], exp.left.width)
        code.extend(asmap.emitStackLoad(left, leftOffset))

    if right == sar.SPILL or right == sar.OVER:
        rightName = exp.right.name
        rightOffset = assignments.offset[getOffsetVarKey(rightName)]
        right = getAsmValWidth(asmap, intermediate[1], exp.right.width)
        code.extend(asmap.emitStackLoad(right, rightOffset))

    code.extend(asmap.emitCoJump(exp.name, left, right, proName, exp.labelName))
    return code

# begin copy section

def getAsmCopyVars(exp, asmap, assignments):
    dest = ''
    source = ''

    if isinstance(exp.dest, lex.TPointer):
        dest = getAsmPointerVal(exp.dest, assignments)
        source = getAsmVal(exp.source, asmap, assignments)
    elif isinstance(exp.source, lex.TPointer):
        dest = getAsmVal(exp.dest, asmap, assignments)
        source = getAsmPointerVal(exp.source, assignments)
    else:
        dest = getAsmVal(exp.dest, asmap, assignments)
        source = getAsmVal(exp.source, asmap, assignments)

    return dest, source

def getAsmCopyPointerToVar(exp, asmap, assignments):
    code = []
    handleDestSpill = False
    intermediate = asmap.getIntermediateRegs()
    dest, source = getAsmCopyVars(exp, asmap, assignments)
    
    if dest == sar.SPILL or dest == sar.OVER:
        handleDestSpill = True
        dest = getAsmValWidth(asmap, intermediate[0], exp.dest.width)

    if source == sar.SPILL or source == sar.OVER:
        sourceName = exp.source.name
        sourceOffset = assignments.offset[getOffsetVarKey(sourceName)]
        source = intermediate[1]
        code.extend(asmap.emitStackLoad(source, sourceOffset))

    if asmap.isReg(source):
        pointer = asmap.getPointer(source)
        code.extend(asmap.emitCopy(dest, pointer))
    else:
        code.extend(asmap.emitCopyIdentifierValue(dest, source))
    
    if handleDestSpill:
        destName = exp.dest.name
        destOffset = assignments.offset[getOffsetVarKey(destName)]
        code.extend(asmap.emitStackStore(dest, destOffset))

    return code

def getAsmCopyVarToPointer(exp, asmap, assignments):
    code = []
    intermediate = asmap.getIntermediateRegs()
    dest, source = getAsmCopyVars(exp, asmap, assignments)
    
    if dest == sar.SPILL or dest == sar.OVER:
        destName = exp.dest.name
        destOffset = assignments.offset[getOffsetVarKey(destName)]
        dest = intermediate[0]
        code.extend(asmap.emitStackLoad(dest, destOffset))

    if source == sar.SPILL or source == sar.OVER:
        sourceName = exp.source.name
        sourceOffset = assignments.offset[getOffsetVarKey(sourceName)]
        source = getAsmValWidth(asmap, intermediate[1], exp.source.width)
        code.extend(asmap.emitStackLoad(source, sourceOffset))

    pointer = asmap.getPointer(dest)
    code.extend(asmap.emitCopy(pointer, source))
    
    return code

def getAsmCopyVarToVar(exp, asmap, assignments):
    code = []
    handleDestSpill = False
    intermediate = asmap.getIntermediateRegs()
    dest, source = getAsmCopyVars(exp, asmap, assignments)

    if dest == sar.SPILL or dest == sar.OVER:
        handleDestSpill = True
        dest = getAsmValWidth(asmap, intermediate[0], exp.dest.width)

    if source == sar.SPILL or source == sar.OVER:
        sourceName = exp.source.name
        sourceOffset = assignments.offset[getOffsetVarKey(sourceName)]
        source = getAsmValWidth(asmap, intermediate[1], exp.source.width)
        code.extend(asmap.emitStackLoad(source, sourceOffset))

    code.extend(asmap.emitCopy(dest, source))
    
    if handleDestSpill:
        destName = exp.dest.name
        destOffset = assignments.offset[getOffsetVarKey(destName)]
        code.extend(asmap.emitStackStore(dest, destOffset))

    return code

def getAsmCopyIdentifierAddressToVar(exp, asmap, assignments):
    code = []
    handleDestSpill = False
    intermediate = asmap.getIntermediateRegs()
    dest, source = getAsmCopyVars(exp, asmap, assignments)

    if dest == sar.SPILL or dest == sar.OVER:
        handleDestSpill = True
        dest = getAsmValWidth(asmap, intermediate[0], exp.dest.width)

    code.extend(asmap.emitCopyIdentifierAddress(dest, source))
    
    if handleDestSpill:
        destName = exp.dest.name
        destOffset = assignments.offset[getOffsetVarKey(destName)]
        code.extend(asmap.emitStackStore(dest, destOffset))

    return code

def getAsmCopy(exp, asmap, assignments):
    if isinstance(exp.dest, lex.TPointer):
        if par.isValidTokenInTypeList(exp.source, par.INTEGER_TYPES):
            return getAsmCopyVarToPointer(exp, asmap, assignments)
        else:
            raise Exception('source must be integer type')
    elif isinstance(exp.source, lex.TPointer):
        if isinstance(exp.dest, lex.TVar):
            return getAsmCopyPointerToVar(exp, asmap, assignments)
        else:
            raise Exception('destination must be integer variable')

    if isinstance(exp.dest, lex.TVar):
        if par.isValidTokenInTypeList(exp.source, par.INTEGER_TYPES):
            return getAsmCopyVarToVar(exp, asmap, assignments)
        elif isinstance(exp.source, lex.TIdentifier):
            return getAsmCopyIdentifierAddressToVar(exp, asmap, assignments)
        else:
            raise Exception('source must be integer or identifier type')

    raise Exception('invalid type for copy destination')

# end copy section

def getAsmUnOp(exp, asmap, assignments):
    code = []
    destSpill = False
    loadDestFromSpill = []
    intermediate = asmap.getIntermediateRegs()
    dest = getAsmVal(exp.dest, asmap, assignments)
    source = getAsmVal(exp.source, asmap,  assignments)

    if dest == sar.SPILL or dest == sar.OVER:
        destSpill = True
        destName = exp.dest.name
        destOffset = assignments.offset[getOffsetVarKey(destName)]
        dest = getAsmValWidth(asmap, intermediate[0], exp.dest.width)
        code.extend(asmap.emitStackLoad(dest, destOffset))
        loadDestFromSpill = asmap.emitStackStore(dest, destOffset)

    if source == sar.SPILL or source == sar.OVER:
        sourceName = exp.source.name
        sourceOffset = assignments.offset[getOffsetVarKey(sourceName)]
        source = getAsmValWidth(asmap, intermediate[1], exp.source.width)
        code.extend(asmap.emitStackLoad(source, sourceOffset))

    code.extend(asmap.emitUnOp(dest, exp.op, source))

    if destSpill:
        code.extend(loadDestFromSpill)

    return code

def getAsmBinOp(exp, asmap, assignments):
    code = []
    destSpill = False
    loadDestFromSpill = []
    intermediate = asmap.getIntermediateRegs()
    dest = getAsmVal(exp.dest, asmap, assignments)
    left = getAsmVal(exp.left, asmap, assignments)
    right = getAsmVal(exp.right, asmap, assignments)
    
    if dest == sar.SPILL or dest == sar.OVER:
        destSpill = True
        destName = exp.dest.name
        destOffset = assignments.offset[getOffsetVarKey(destName)]
        dest = getAsmValWidth(asmap, intermediate[0], exp.dest.width)
        code.extend(asmap.emitStackLoad(dest, destOffset))
        loadDestFromSpill = asmap.emitStackStore(dest, destOffset)

    if left == sar.SPILL or left == sar.OVER:
        leftName = exp.left.name
        leftOffset = assignments.offset[getOffsetVarKey(leftName)]
        left = getAsmValWidth(asmap, intermediate[1], exp.left.width)
        code.extend(asmap.emitStackLoad(left, leftOffset))

    if right == sar.SPILL or right == sar.OVER:
        rightName = exp.right.name
        rightOffset = assignments.offset[getOffsetVarKey(rightName)]
        right = getAsmValWidth(asmap, intermediate[2], exp.right.width)
        code.extend(asmap.emitStackLoad(right, rightOffset))

    code.extend(asmap.emitBinOp(dest, exp.op, left, right))

    if destSpill:
        code.extend(loadDestFromSpill)

    return code

# begin procedure call section

def getAsmProCallStackStatements(exp, asmap, assignments, props):
    store = []
    load = []

    id = exp.id
    usesInt = (id in props.usesInt) and props.usesInt[id]

    if usesInt:
        callerSaved = asmap.getCallerSavedRegs()
        for reg in callerSaved:
            key = getOffsetRegKey(reg)
            if key in assignments.offset:
                offset = assignments.offset[key]
                store.extend(asmap.emitStackStore(reg, offset))
                load.extend(asmap.emitStackLoad(reg, offset))

    return store, load

def getAsmProCallArguments(params, asmap, assignments):
    code = []
    pushes = []
    pops = []
    popTotal = 0

    intermediate = asmap.getIntermediateRegs()
    arguRegs = asmap.getArgumentRegs()
    destRegsUsed = {}

    pend = len(params)
    rend = len(arguRegs)
    pi = 0
    ri = 0

    while pi < pend:
        param = params[pi]
        destReg = ''

        if ri < rend:
            destReg = arguRegs[ri]
            ri += 1
            destRegsUsed[destReg] = True

            if isinstance(param, lex.TVar):
                sourceName = param.name
                sourceReg = assignments.generalReg[sourceName]

                if sourceReg in destRegsUsed:
                    key = getOffsetRegKey(sourceReg)
                    sourceOffset = assignments.offset[key]
                    code.extend(asmap.emitStackLoad(destReg, sourceOffset))
                elif destReg == sar.SPILL or destReg == sar.OVER:
                    key = getOffsetVarKey(sourceReg)
                    sourceOffset = assignments.offset[key]
                    code.extend(asmap.emitStackLoad(destReg, sourceOffset))
                else:
                    code.extend(asmap.emitCopy(destReg, sourceReg))
            elif isinstance(param, lex.TInt) or isinstance(param, lex.TChar):
                value = param.value
                code.extend(asmap.emitCopy(destReg, value))
            else:
                raise Exception('invalid type for argument')
        else:
            nextPush = []

            if isinstance(param, lex.TVar):
                paReg = getAsmVal(param, asmap, assignments)

                if paReg == sar.SPILL or paReg == sar.OVER:
                    sourceOffset = assignments.offset[getOffsetVarKey(sourceName)]
                    paReg = intermediate[0]
                    nextPush.extend(asmap.emitStackLoad(paReg, sourceOffset))                

                nextPush.extend(asmap.emitPush(paReg))
            elif isinstance(param, lex.TInt) or isinstance(param, lex.TChar):
                value = param.value
                paReg = intermediate[0]
                nextPush.extend(asmap.emitCopy(paReg, value))
                nextPush.extend(asmap.emitPush(paReg))
            else:
                raise Exception('invalid type for argument')
            
            pushes = nextPush + pushes
            popTotal += 8

        pi += 1

    if popTotal > 0:
        # pop all at once with a stack deallocation
        pops.extend(asmap.emitStackDeallocation(popTotal))

    return code, pushes, pops

def getAsmProCallReturn(dest, asmap, assignments):
    code = []
    retReg = asmap.getRetReg()
    destReg = getAsmVal(dest, asmap, assignments)

    if destReg == sar.SPILL or destReg == sar.OVER:
        destName = dest.name
        destOffset = assignments.offset[getOffsetVarKey(destName)]
        code.extend(asmap.emitStackStore(retReg, destOffset))
    else:
        code.extend(asmap.emitCopy(destReg, retReg))

    return code

def getAsmIdCall(exp, asmap, assignments):
    code = []
    id = exp.id

    if (len(id) > 1) and (id[0] == gram.PRO_VAR_CALL):
        sourceName = id[1:]
        intermediate = asmap.getIntermediateRegs()
        source = assignments.generalReg[sourceName]

        if source == sar.SPILL or source == sar.OVER:
            sourceOffset = assignments.offset[getOffsetVarKey(sourceName)]
            source = getAsmValWidth(asmap, intermediate[0], 8)
            code.extend(asmap.emitStackLoad(source, sourceOffset))

        code.extend(asmap.emitCall(source))
    else:
        code.extend(asmap.emitCall(id))

    return code

def getAsmProCall(exp, asmap, assignments, props):
    store, load = getAsmProCallStackStatements(exp, asmap, assignments, props)    
    args, pushes, pops = getAsmProCallArguments(exp.params, asmap, assignments)
    proCall = getAsmIdCall(exp, asmap, assignments)
    proRet = getAsmProCallReturn(exp.dest, asmap, assignments)

    code = []

    code.extend(store)
    code.extend(args)
    code.extend(pushes)
    code.extend(proCall)
    code.extend(pops)
    code.extend(load)
    code.extend(proRet)

    return code

# end procedure call section

###

# begin procedure composition section

def getAsmStatementsFromExp(exp, proName, asmap, assignments, props):
    if isinstance(exp, par.ELabel):
        return getAsmLocalLabel(exp, proName, asmap)
    elif isinstance(exp, par.EJump):
        return getAsmJump(exp, proName, asmap)
    elif isinstance(exp, par.ECoJump):
        return getAsmCoJump(exp, proName, asmap, assignments)
    elif isinstance(exp, par.ECopy):
        return getAsmCopy(exp, asmap, assignments)
    elif isinstance(exp, par.EUnOp):
        return getAsmUnOp(exp, asmap, assignments)
    elif isinstance(exp, par.EBinOp):
        return getAsmBinOp(exp, asmap, assignments)
    elif isinstance(exp, par.EProCall):
        return getAsmProCall(exp,  asmap, assignments, props)

    return []

def getAsmProStackAllocations(asmap, maxOffset):
    prologue = []

    if maxOffset > 0:
        prologue.extend(asmap.emitStackAllocation(maxOffset))

    epilogue = []

    if maxOffset > 0:
        epilogue.extend(asmap.emitStackDeallocation(maxOffset))
    
    epilogue.extend(asmap.emitRet())

    return prologue, epilogue

def getAsmProStackStatements(name, asmap, assignments, props):
    store = []
    load = []
    usesInt = (name in props.usesInt) and props.usesInt[name]

    if usesInt:
        calleeSaved = asmap.getCalleeSavedRegs()
        for reg in calleeSaved:
            key = getOffsetRegKey(reg)
            if key in assignments.offset:
                offset = assignments.offset[key]
                store.extend(asmap.emitStackStore(reg, offset))
                load.extend(asmap.emitStackLoad(reg, offset))

    return store, load

def getAsmProExpressionStatements(exps, proName, asmap, assignments, props):
    statements = []

    for exp in exps:
        statement = getAsmStatementsFromExp(exp, proName, asmap, assignments, props)
        statements.extend(statement)

    return statements

def getAsmProRetStatement(retVar, asmap, assignments):
    code = []
    retSource = getAsmVal(retVar, asmap, assignments)
    retDest = asmap.getRetReg()

    if isinstance(retVar, lex.TVar):
        if retSource == sar.SPILL or retSource == sar.OVER:
            sourceName = retVar.name
            sourceOffset = assignments.offset[getOffsetVarKey(sourceName)]
            code.extend(asmap.emitStackLoad(retDest, sourceOffset))
        else:
            code.extend(asmap.emitCopy(retDest, retSource))
    elif isinstance(retVar, lex.TInt):
        code.extend(asmap.emitCopy(retDest, retSource))

    return code

def getAsmPro(pro, asmap, assignments, props):
    maxOffset = getStackOffset(assignments)
    prologue, epilogue = getAsmProStackAllocations(asmap, maxOffset)
    store, load = getAsmProStackStatements(pro.name, asmap, assignments, props)
    expStatements = getAsmProExpressionStatements(pro.expressions, pro.name, asmap, assignments, props)
    retStatement = getAsmProRetStatement(pro.ret, asmap, assignments)

    code = asmap.emitProName(pro.name)
    code.extend(prologue)
    code.extend(store)
    code.extend(expStatements)
    code.extend(retStatement)
    code.extend(load)
    code.extend(epilogue)

    optimized = asmap.emitOptimized(code)
    return optimized

# end procedure composition section

###

# begin memory block section

def getAsmMemCollection(mem, asmap):
    return asmap.emitMemCollection(mem.name, mem.collection)

def getAsmMemSize(mem, asmap):
    return asmap.emitMemSize(mem.name, mem.size)

# end memory block section

###

# begin code generation section

class AssignmentCollection:
    def __init__(self, generalReg, offset):
        self.generalReg = generalReg
        self.offset = offset

def generateProcedures(asmap, pros, props):
    code = []
    maxArgs = len(asmap.getArgumentRegs())
    allRegs = asmap.getRegistersToMap()
    
    for pro in pros:
        if len(code) > 0:
            code.extend([''])

        generalDict = sar.getAssignmentDict(allRegs, pro, maxArgs, lex.TVar)
        offsetDict = getOffsetDict(pro, asmap, generalDict)
        assignments = AssignmentCollection(generalDict, offsetDict)
        code.extend(getAsmPro(pro, asmap, assignments, props))
        
    return code

def generateMemories(asmap, mems):
    code = []
    
    for mem in mems:
        if len(code) > 0:
            code.extend([''])

        if isinstance(mem, par.EMemCollection):
            code.extend(getAsmMemCollection(mem, asmap))
        elif isinstance(mem, par.EMemSize):
            code.extend(getAsmMemSize(mem, asmap))
        
    return code

def generateSectionText(asmap, pros, props):
    proCode = generateProcedures(asmap, pros, props)

    if len(proCode) < 1:
        return []
    
    code = []
    code.extend(asmap.emitSectionText())
    code.extend([''])

    for pro in pros:
        code.extend(asmap.emitGlobal(pro.name))

    code.extend([''])
    code.extend(proCode)
    code.extend([''])

    return code

def generateSectionData(asmap, mems):
    memCode = generateMemories(asmap, mems)

    if len(memCode) < 1:
        return []
    
    code = []
    code.extend(asmap.emitSectionData())
    code.extend([''])
    code.extend(memCode)
    code.extend([''])

    return code

def generateSections(exps):
    memories = []
    procedures = []

    for exp in exps:
        if isinstance(exp, par.EPro):
            procedures.append(exp)
        else:
            memories.append(exp)

    return memories, procedures

def generateCodeLinesFromText(text, asmap):
    segments = lex.getSegments(text)
    tokens = lex.getCodeTokens(segments)
    exps = par.getExpressions(tokens)
    mems, pros = generateSections(exps)
    props = par.getProcedureProperties(pros)

    code = []
    code.extend(generateSectionText(asmap, pros, props))
    code.extend(generateSectionData(asmap, mems))

    return code

# end code generation section
