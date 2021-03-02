import bc3_symboltable as ST
from bc3_scanner import GOARROW1, GOARROW2, RETARROW1, RETARROW2, INT, FLOAT, STR, BOOL
from bc3_data import Int, Float, Str, Bool, Func, Lab, Ref, Arr, Lst
from bc3_data import Const, Var, Array, List, Function, Label

def test_initialize():
    ST.init()

    assert ST.symTab == [{}]
    assert GOARROW1 in ST.spcTab[0]
    assert GOARROW2 in ST.spcTab[0]
    assert RETARROW1 in ST.spcTab[0]
    assert RETARROW2 in ST.spcTab[0]

    assert ST.size == 1
    assert len(ST.symTab) == 1
    assert len(ST.spcTab) == 1

def test_newScope():
    ST.init()
    ST.newScope()

    assert ST.symTab == [{},{}]
    assert GOARROW1 in ST.spcTab[0]
    assert GOARROW2 in ST.spcTab[0]
    assert RETARROW1 in ST.spcTab[0]
    assert RETARROW2 in ST.spcTab[0]
    assert GOARROW1 in ST.spcTab[1]
    assert GOARROW2 in ST.spcTab[1]
    assert RETARROW1 in ST.spcTab[1]
    assert RETARROW2 in ST.spcTab[1]

    assert ST.size == 2
    assert len(ST.symTab) == 2
    assert len(ST.spcTab) == 2

def test_collapseScope():
    ST.init()
    ST.newScope()

    assert ST.size == 2
    assert len(ST.symTab) == 2
    assert len(ST.spcTab) == 2

    ST.collapse()

    assert ST.size == 1
    assert len(ST.symTab) == 1
    assert len(ST.spcTab) == 1

def test_sym():
    ST.init()

    ST.newSym('var1', Const(INT,3))
    ST.newSym('var2', Const(STR,'3'))

    assert ST.getSym('var1') == Const(INT,3)
    assert ST.getSym('var2') == Const(STR,'3')

    ST.newScope()

    ST.newSym('var2', Const(STR,'5'))
    ST.newSym('var3', Const(FLOAT,5))

    assert ST.getSym('var1') == None
    assert ST.getSym('var2') == Const(STR,'5')
    assert ST.getSym('var3') == Const(FLOAT,5)
    assert ST.getSym('var1', burrow=True) == Const(INT,3)
    assert ST.getSym('var2', burrow=True) == Const(STR,'5')

    ST.setSym('var2', Const(FLOAT,3.0))
    assert ST.getSym('var2') == Const(FLOAT,3.0)

    ST.collapse('drop')

    assert ST.getSym('var1') == Const(INT,3)
    assert ST.getSym('var2') == Const(STR,'3')
    assert ST.getSym('var3') == None

    ST.delSym('var1')

    assert ST.getSym('var1') == None
    assert ST.getSym('var2') == Const(STR,'3')
    assert ST.getSym('var3') == None

    ST.newScope()
    ST.newSym('var1', Const(INT,1))
    ST.newSym('var2', Const(INT,2))
    ST.newSym('var4', Const(BOOL,False))

    assert ST.getSym('var4') == Const(BOOL,False)

    ST.newScope()
    ST.newSym('var4', Const(INT,9))
    ST.newSym('var5', Const(BOOL,True),-3)

    assert ST.getSym('var4') == Const(INT,9)
    assert ST.getSym('var5') == None

    ST.collapse('override')

    assert ST.getSym('var4') == Const(INT,9)
    assert ST.getSym('var5') == None

    ST.collapse('merge')

    assert ST.getSym('var1') == Const(INT,1)
    assert ST.getSym('var2') == Const(STR,'3')
    assert ST.getSym('var3') == None
    assert ST.getSym('var4') == Const(INT,9)
    assert ST.getSym('var5') == Const(BOOL,True)

def test_spc():
    ST.init()

    ST.setSpc(RETARROW1, 5)
    ST.setSpc(RETARROW1, 20)
    ST.setSpc(RETARROW1, 10)
    ST.setSpc(RETARROW2, 7)
    ST.setSpc(RETARROW2, 15)

    ST.setSpc(GOARROW1, 1)
    ST.setSpc(GOARROW1, 9)
    ST.setSpc(GOARROW2, 6)
    ST.setSpc(GOARROW2, 3)
    ST.setSpc(GOARROW2, 12)

    ST.setSpc(GOARROW2, 12)
    ST.setSpc(GOARROW2, -11)

    assert ST.getSpc(RETARROW1) == [5,10,20]
    assert ST.getSpc(RETARROW2) == [7,15]
    assert ST.getSpc(GOARROW1) == [1,9]
    assert ST.getSpc(GOARROW2) == [3,6,12]

    ST.newScope()

    ST.setSpc(RETARROW1, 7)
    ST.setSpc(RETARROW2, 7)
    ST.setSpc(GOARROW1, 7)
    ST.setSpc(GOARROW2, 7)

    assert ST.getSpc(RETARROW1) == [7]
    assert ST.getSpc(RETARROW2) == [7]
    assert ST.getSpc(GOARROW1) == [7]
    assert ST.getSpc(GOARROW2) == [7]

    ST.collapse()

    assert ST.getSpc(RETARROW1) == [5,10,20]
    assert ST.getSpc(RETARROW2) == [7,15]
    assert ST.getSpc(GOARROW1) == [1,9]
    assert ST.getSpc(GOARROW2) == [3,6,12]

    assert ST.getNextArrow(RETARROW1,6) == 10
    assert ST.getNextArrow(RETARROW2,6) == 7
    assert ST.getNextArrow(GOARROW1,6) == 1
    assert ST.getNextArrow(GOARROW2,6) == 3

    assert ST.getNextArrow(RETARROW1,6,1) == 20
    assert ST.getNextArrow(RETARROW2,6,2) == 6
    assert ST.getNextArrow(GOARROW1,6,1) == 6
    assert ST.getNextArrow(GOARROW2,7,1) == 3
