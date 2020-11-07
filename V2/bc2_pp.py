# NGL Bytecode 2.0 Preprocessor

# import re
import bc2_sc as SC
from bc2_sc import GOARROW1, GOARROW2, RETARROW1, RETARROW2, mark
import bc2_st as ST
import bc2_sk as PPG

# TODO: Add grammar processing instead of re
#   Allows for preprocessor comands

workingfile = 'conf'

def init(src : str, subrun = False, debug = False):
    # Perform setup in one pass

    # Initialize tables
    SC.init(src)
    ST.init(src)

    # ARROW determination should occur at last step
    _firstpass(src, subrun, debug)

    # Reinitialize tables
    SC.init(src)

    # srcCopy, usrfuncCopy, errorCopy = SC.save()
    # symTabCopy, jmpTabCopy = ST.save()
    #
    # jmpTabList = []
    #
    # print('modules',SC.usrfunc)
    # try:
    #     for module in SC.usrfunc:
    #         src = ''
    #         with open(module+'.ngl','r') as reader:
    #             for src_line in reader.readlines():
    #                 src += src_line
    #
    #         init(src, True, True)
    #
    #         _, usrfuncMod, errorMod = SC.save()
    #         _, jmpTabCopy = ST.save()
    #
    #         jmpTabList.append(jmpTabCopy)
    #         if errorMod: errorCopy = errorMod
    #         for submod in usrfuncMod:
    #             usrfuncCopy.append(submod) # FIX: Will add duplicates?
    # except IOError:
    #     mark('module '+module+' could not be read')
    #
    # # Reinitialize
    # ST.load(symTabCopy, jmpTabCopy)
    #
    # for jmpTabMod in jmpTabList:
    #     for i, (name, value) in enumerate(jmpTabMod.items()):
    #         ST.newJump(name,value,True)
    #
    # SC.init(src)
    # SC.load(usrfuncCopy)
    # SC.usrfunc = usrfuncCopy
    #
    # if not SC.error:
    #     with open(workingfile+'.ngl', 'w') as f:
    #         f.write(srcCopy+'\n')
    #
    #         for module in SC.usrfunc:
    #             f.write('//writing '+module+'.ngl\n')
    #             include = open(module+'.ngl','r')
    #             text = include.readlines()
    #
    #             for line in text:
    #                 f.write(line)

    return SC.error

    # # Define individual re matches
    # re_label = ('[_]?[A-Za-z0-9]+[A-Za-z0-9_]*') # Labels
    # re_goarrow1 = ('->') # Go Arrow 1
    # re_goarrow2 = ('=>') # Go Arrow 2
    # re_retarrow1 = ('<-') # Return Arrow 1
    # re_retarrow2 = ('<=') # Return Arrow 2
    # # Put all matches together
    # re_all = ('^\s*('+re_label+')\s*:|^\s*('+re_goarrow1+')\s*|^\s*('+re_goarrow2+')\s*|^\s*('+re_retarrow1+')\s*|^\s*('+re_retarrow2+')\s*')
    #
    # for i,line in enumerate(src.splitlines()):
    #     line = line.lstrip()
    #
    #     match = re.compile(re_all).match(line)
    #     if match:
    #         if match.group(1): # Label
    #             ST.newJump(match.group(1),i)
    #         elif match.group(2): # ->
    #             ST.newJump(RETARROW1,i)
    #         elif match.group(3): # =>
    #             ST.newJump(RETARROW2,i)
    #         elif match.group(4): # <-
    #             ST.newJump(GOARROW1,i)
    #         elif match.group(5): # <=
    #             ST.newJump(GOARROW2,i)

def _firstpass(src : str, subrun = False, debug = False):
    if debug:   PPG.execute_debug(src, subrun)
    else:       PPG.execute()

    return SC.error

if __name__ == '__main__':
    src = ''
    with open('usr.ngl','r') as reader:
        for src_line in reader.readlines():
            src += src_line

    init(src, debug = True)
