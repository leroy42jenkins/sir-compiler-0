import lib.parser as par

OVER = 'over'
SPILL = 'spill'

# useful for debugging
def printDict(di):
    for k in di:
        v = di[k]
        print('{ ' + str(k) + ' : ' + str(v) + ' }')

def getIntervals(expressions, varType):
    line = 0
    length = len(expressions)
    intervals = {}

    for line in range(length):
        exp = expressions[line]
        params = par.getParamsFromExpression(exp)

        for param in params:
            if isinstance(param, varType):
                name = param.name
                if name in intervals:
                    intervals[name][1] = line
                else:
                    intervals[name] = [line, line]

    return intervals

def getInitialAssignments(allRegs, pro, intervals, maxArgs, varType):
    assignments = {}

    ri = 0
    rend = len(allRegs)

    params = [p for p in pro.params if isinstance(p, varType)]
    pi = 0
    pend = len(params)

    while pi < pend:
        param = params[pi]
        
        if isinstance(param, varType):
            name = param.name
            if (pi >= maxArgs) or (ri >= rend):
                assignments[name] = OVER
            else:
                reg = allRegs[ri]
                assignments[name] = reg
                ri += 1

        pi += 1

    for name in intervals:
        if (name not in assignments):
            if ri < rend:
                reg = allRegs[ri]
                assignments[name] = reg
                ri += 1
            else:
                assignments[name] = SPILL

    return assignments

def isConcurrentInterval(a, b):
    f0 = a[0] >= b[0] and a[0] <= b[1]
    f1 = a[1] >= b[0] and a[1] <= b[1]
    f2 = a[0] <= b[0] and a[1] >= b[1]
    return f0 or f1 or f2

def getFirstFreeReg(intervals, assignments, name, interval):
    lowerIntervals = []
    concurrentIntervals = {}

    for n in intervals:
        if n != name:
            i = intervals[n]
            if i[1] < interval[0]:
                reg = assignments[n]
                if (reg != SPILL) and (reg != OVER):
                    lowerIntervals.append(reg)
            elif isConcurrentInterval(i, interval):
                reg = assignments[n]
                if (reg != SPILL) and (reg != OVER):
                    concurrentIntervals[reg] = True

    for reg in lowerIntervals:
        if (reg not in concurrentIntervals):
            return reg

    return SPILL

def getDictCopy(original):
    copy = {}
    for k in original:
        copy[k] = original[k]

    return copy

def getRefinedAssignments(intervals, assignments):
    refined = getDictCopy(assignments)
    for name in refined:
        reg = refined[name]
        if reg == SPILL:
            interval = intervals[name]
            freeReg = getFirstFreeReg(intervals, refined, name, interval)
            if freeReg != SPILL:
                refined[name] = freeReg

    return refined

def getAssignmentDict(allRegs, pro, maxArgs, varType):
    intervals = getIntervals(pro.expressions, varType)
    assignments = getInitialAssignments(allRegs, pro, intervals, maxArgs, varType)
    refined = getRefinedAssignments(intervals, assignments)
    return refined
