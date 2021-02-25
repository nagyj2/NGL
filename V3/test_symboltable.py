import bc3_symboltable as ST
from bc3_scanner import GOARROW1, GOARROW2, RETARROW1, RETARROW2, INT, FLOAT, STR, BOOL
from bc3_data import Constant, Variable, Array, List

def test_initialize():
    ST.init()

    assert ST.symTab == [{}]
    assert ST.jmpTab == [{}]
    assert GOARROW1 in ST.spcTab[0]
    assert GOARROW2 in ST.spcTab[0]
    assert RETARROW1 in ST.spcTab[0]
    assert RETARROW2 in ST.spcTab[0]

    assert ST.size == 1
    assert len(ST.symTab) == 1
    assert len(ST.jmpTab) == 1
    assert len(ST.spcTab) == 1

def test_newScope():
    ST.init()
    ST.newScope()

    assert ST.symTab == [{},{}]
    assert ST.jmpTab == [{},{}]
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
    assert len(ST.jmpTab) == 2
    assert len(ST.spcTab) == 2

def test_sym():
    ST.init()

    ST.newSym('var1', Constant(INT,3))
    ST.newSym('var2', Constant(STR,'3'))

    assert ST.getSym('var1') == Constant(INT,3)
    assert ST.getSym('var2') == Constant(STR,'3')

    ST.newScope()

    ST.newSym('var2', Constant(STR,'5'))
    ST.newSym('var3', Constant(FLOAT,5))

    assert ST.getSym('var1') == None
    assert ST.getSym('var2') == Constant(STR,'5')
    assert ST.getSym('var3') == Constant(FLOAT,5)
    assert ST.getSym('var1', burrow=True) == Constant(INT,3)
    assert ST.getSym('var2', burrow=True) == Constant(STR,'5')

    ST.setSym('var2', Constant(FLOAT,3.0))
    assert ST.getSym('var2') == Constant(FLOAT,3.0)

    ST.collapse('drop')

    assert ST.getSym('var1') == Constant(INT,3)
    assert ST.getSym('var2') == Constant(STR,'3')
    assert ST.getSym('var3') == None

    ST.delSym('var1')

    assert ST.getSym('var1') == None
    assert ST.getSym('var2') == Constant(STR,'3')
    assert ST.getSym('var3') == None

    ST.newScope()
    ST.newSym('var1', Constant(INT,1))
    ST.newSym('var2', Constant(INT,2))
    ST.newSym('var4', Constant(BOOL,False))

    assert ST.getSym('var4') == Constant(BOOL,False)

    ST.newScope()
    ST.newSym('var4', Constant(INT,9))
    ST.newSym('var5', Constant(BOOL,True),-3)

    assert ST.getSym('var4') == Constant(INT,9)
    assert ST.getSym('var5') == None

    ST.collapse('override')

    assert ST.getSym('var4') == Constant(INT,9)
    assert ST.getSym('var5') == None

    ST.collapse('merge')

    assert ST.getSym('var1') == Constant(INT,1)
    assert ST.getSym('var2') == Constant(STR,'3')
    assert ST.getSym('var3') == None
    assert ST.getSym('var4') == Constant(INT,9)
    assert ST.getSym('var5') == Constant(BOOL,True)

def test_jmp():
    ST.init()

    ST.newJmp('lab1', 5)
    ST.newJmp('lab2', 10)

    assert ST.getJmp('lab1') == 5
    assert ST.getJmp('lab2') == 10

    ST.newScope()

    ST.newJmp('lab2', 7)
    ST.newJmp('lab3', 15)
    ST.newJmp('lab4', 20, -2)

    assert ST.getJmp('lab1') == None
    assert ST.getJmp('lab2') == 7
    assert ST.getJmp('lab3') == 15
    assert ST.getJmp('lab4') == None
    assert ST.getJmp('lab1', burrow=True) == 5
    assert ST.getJmp('lab2', burrow=True) == 7

    ST.collapse()

    assert ST.getJmp('lab1') == 5
    assert ST.getJmp('lab2') == 10
    assert ST.getJmp('lab3') == None
    assert ST.getJmp('lab4') == 20

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
