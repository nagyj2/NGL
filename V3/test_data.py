import bc3_data as D
from bc3_data import *
import bc3_scanner as SC
from bc3_scanner import *

def test_constant():
    int1 = D.Constant(INT,3)
    int2 = D.Constant(INT,3)
    int3 = D.Constant(INT,5)
    float1 = D.Constant(FLOAT,3)
    float2 = D.Constant(FLOAT,3.0)
    float3 = D.Constant(FLOAT,5)
    str1 = D.Constant(STR,'3')
    str2 = D.Constant(STR,"3")
    str3 = D.Constant(STR," ")
    bool1 = D.Constant(BOOL,True)
    bool2 = D.Constant(BOOL,False)
    bool3 = D.Constant(BOOL,True)

    assert int1 == int2
    assert int1 != int3
    assert int1 != float1
    assert int1 != float2
    assert int1 != float3
    assert int1 != str1
    assert int1 != bool1
    assert float1 == float2
    assert float1 != float3
    assert float1 != bool1
    assert str1 == str2
    assert str1 != str3
    assert str1 != bool1
    assert bool1 == bool3
    assert bool1 != bool2

def test_variable():
    int1 = D.Variable(INT,3)
    int2 = D.Variable(INT,3)
    int3 = D.Variable(INT,5)
    float1 = D.Variable(FLOAT,3)
    float2 = D.Variable(FLOAT,3.0)
    float3 = D.Variable(FLOAT,5)
    str1 = D.Variable(STR,'3')
    str2 = D.Variable(STR,"3")
    str3 = D.Variable(STR," ")
    bool1 = D.Variable(BOOL,True)
    bool2 = D.Variable(BOOL,True)
    bool3 = D.Variable(BOOL,False)

    assert int1 == int2
    assert int1 != int3
    assert int1 != float1
    assert int1 != float2
    assert int1 != float3
    assert int1 != str1
    assert int1 != bool1
    assert float1 == float2
    assert float1 != float3
    assert float1 != bool1
    assert str1 == str2
    assert str1 != str3
    assert str1 != bool1
    assert bool1 == bool2
    assert bool1 != bool3

    int3.setValue(3)
    assert int1 == int3
    float3.setValue(3)
    assert float1 == float3
    str3.setValue('3')
    assert str1 == str3
    bool3.setValue(True)
    assert bool1 == bool3

def test_array():
    int1 = D.Array(INT,(1,2,3))
    int2 = D.Array(INT,(1,2,3))
    int3 = D.Array(INT,(3,2,1))
    int4 = D.Array(INT,(1,2))
    float1 = D.Array(FLOAT,(1,2,3))
    str1 = D.Array(STR,('1','2','3'))
    bool1 = D.Array(BOOL,(True,False,True))

    assert int1 == int2
    assert int1 != int3
    assert int1 != int4
    assert int1 != float1
    assert int1 != str1
    assert int1 != bool1

def test_list():
    int1 = D.List(INT,(1,2,3))
    int2 = D.List(INT,(1,2,3))
    int3 = D.List(INT,(3,2,1))
    int4 = D.List(INT,(1,2))
    float1 = D.List(FLOAT,(1,2,3))
    float2 = D.List(FLOAT,(1,2,3))
    str1 = D.List(STR,('1','2','3'))
    str2 = D.List(STR,('1','2','3'))
    bool1 = D.List(BOOL,(True,False,True))
    bool2 = D.List(BOOL,(True,False,True))

    assert int1 == int2
    assert int1 != int3
    assert int1 != int4
    assert int1 != float1
    assert int1 != str1
    assert int1 != bool1
    assert float1 == float2
    assert str1 == str2
    assert bool1 == bool2

    float2.setValue(0,0)
    assert float1 != float2
    str2.setValue('0',1)
    assert str1 != str2
    bool2.setValue(False,2)
    assert bool1 != bool2

def test_invalid_constant():
    try:    D.Constant(INT,3.0)
    except: pass
    else:   assert False

    try:    D.Constant(INT,True)
    except: pass
    else:   assert False

    try:    D.Constant(FLOAT,3)
    except: pass
    else:   assert False

    try:    D.Constant(FLOAT,'3')
    except: pass
    else:   assert False

    try:    D.Constant(FLOAT,False)
    except: pass
    else:   assert False

    try:    D.Constant(STR,4)
    except: pass
    else:   assert False

    try:    D.Constant(STR,0.0)
    except: pass
    else:   assert False

    try:    D.Constant(STR,True)
    except: pass
    else:   assert False

    try:    D.Constant(BOOL,3)
    except: pass
    else:   assert False

    try:    D.Constant(BOOL,3.0)
    except: pass
    else:   assert False

    try:    D.Constant(BOOL,'3')
    except: pass
    else:   assert False

def test_invalid_variable():
    try:    D.Variable(INT,3.0)
    except: pass
    else:   assert False

    try:    D.Variable(INT,True)
    except: pass
    else:   assert False

    try:    D.Variable(FLOAT,3)
    except: pass
    else:   assert False

    try:    D.Variable(FLOAT,'3')
    except: pass
    else:   assert False

    try:    D.Variable(FLOAT,False)
    except: pass
    else:   assert False

    try:    D.Variable(STR,4)
    except: pass
    else:   assert False

    try:    D.Variable(STR,0.0)
    except: pass
    else:   assert False

    try:    D.Variable(STR,True)
    except: pass
    else:   assert False

    try:    D.Variable(BOOL,3)
    except: pass
    else:   assert False

    try:    D.Variable(BOOL,3.0)
    except: pass
    else:   assert False

    try:    D.Variable(BOOL,'3')
    except: pass
    else:   assert False

    int1 = D.Variable(INT,3)
    float1 = D.Variable(FLOAT,3.0)
    str1 = D.Variable(STR,'3')
    bool1 = D.Variable(BOOL,True)

    try:    int1.setVariable(3.0)
    except: pass
    else:   assert False

    try:    float1.setVariable('3.0')
    except: pass
    else:   assert False

    try:    str1.setVariable(None)
    except: pass
    else:   assert False

    try:    bool1.setVariable(3)
    except: pass
    else:   assert False

def test_invalid_array():
    try:    D.Array(INT,(1,2.0,3))
    except: pass
    else:   assert False

    try:    D.Array(BOOL,(1,'2',3))
    except: pass
    else:   assert False

    try:    D.Array(FLOAT,(1,True,3))
    except: pass
    else:   assert False

def test_invalid_list():
    try:    D.List(INT,(1,2.0,3))
    except: pass
    else:   assert False

    try:    D.List(STR,(1,'2',3))
    except: pass
    else:   assert False

    try:    D.List(BOOL,(1,True,3))
    except: pass
    else:   assert False

    int1 = D.List(INT,(1,2,3))
    float1 = D.List(FLOAT,(1,2,3))
    str1 = D.List(STR,('1','2','3'))
    bool1 = D.List(BOOL,(True,False))

    try:    int1.setValue(-1.0,0)
    except: pass
    else:   assert False

    try:    float1.setValue(-1,1)
    except: pass
    else:   assert False

    try:    str1.setValue(-1,2)
    except: pass
    else:   assert False

    try:    bool1.setValue('-1',1)
    except: pass
    else:   assert False

    try:    int1.setValue(-1,3)
    except: pass
    else:   assert False

    try:    int1.setValue(2,-1)
    except: pass
    else:   assert False
