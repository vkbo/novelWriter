# -*- coding: utf-8 -*-
"""novelWriter Common Class Tester
"""

import nw, pytest
from nw.common import *
from nwtools import cmpList

@pytest.mark.core
def testCheckString():
    assert checkString(None,  "NotNone",True)  is None
    assert checkString("None","NotNone",True)  is None
    assert checkString("None","NotNone",False) == "None"
    assert checkString(None,  "NotNone",False) == "NotNone"
    assert checkString(1,     "NotNone",False) == "NotNone"
    assert checkString(1.0,   "NotNone",False) == "NotNone"
    assert checkString(True,  "NotNone",False) == "NotNone"

@pytest.mark.core
def testCheckInt():
    assert checkInt(None,  3,True)  is None
    assert checkInt("None",3,True)  is None
    assert checkInt(None,  3,False) == 3
    assert checkInt(1,     3,False) == 1
    assert checkInt(1.0,   3,False) == 1
    assert checkInt(True,  3,False) == 1

@pytest.mark.core
def testCheckBool():
    assert checkBool(None,   3,    True)  is None
    assert checkBool("None", 3,    True)  is None
    assert checkBool("True", False,False) == True
    assert checkBool("False",True, False) == False
    assert checkBool("Boo",  None, False) is None
    assert checkBool(0,      None, False) == False
    assert checkBool(1,      None, False) == True
    assert checkBool(2,      None, False) is None
    assert checkBool(0.0,    None, False) is None
    assert checkBool(1.0,    None, False) is None
    assert checkBool(2.0,    None, False) is None

@pytest.mark.core
def testColRange():
    assert colRange([0,0], [0,0], 0) is None
    assert cmpList(colRange([200,50,0], [50,200,0], 1), [200,50,0])
    assert cmpList(colRange([200,50,0], [50,200,0], 2), [[200,50,0],[50,200,0]])
    assert cmpList(colRange([200,50,0], [50,200,0], 3), [[200,50,0],[125,125,0],[50,200,0]])
    assert cmpList(colRange([200,50,0], [50,200,0], 4), [[200,50,0],[150,100,0],[100,150,0],[50,200,0]])
    assert cmpList(colRange([200,50,0], [50,200,0], 5), [[200,50,0],[162,87,0],[124,124,0],[86,161,0],[50,200,0]])
