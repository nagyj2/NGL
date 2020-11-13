# NGL Speed 1.0 Symbol Table

from ngl_s_sc import mark

# str: str
# Variable in NGL Speed: Variable in NGL Bytecode
varTab = {}
varnum = 0

def newVar(name):
    global varTab, varnum
    if name not in varTab:
        varTab[name] = 'var' + str(varnum)
        varnum += 1
    else:
        mark('variable already exists')

def getVar(name):
    global varTab, varnum
    if name in varTab:
        return varTab[name]
    else:
        mark('variable not declared')
