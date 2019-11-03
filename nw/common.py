# -*- coding: utf-8 -*-
"""novelWriter Common Functions

 novelWriter – Common Functions
================================
 Various functions used multiple places

 File History:
 Created: 2019-05-12 [0.1.0]

"""

import logging
import nw

logger = logging.getLogger(__name__)

def checkString(checkValue, defaultValue, allowNone=False):
    if allowNone:
        if checkValue == None:
            return None
        if checkValue == "None":
            return None
    if isinstance(checkValue,str):
        return str(checkValue)
    return defaultValue

def checkInt(checkValue, defaultValue, allowNone=False):
    if allowNone:
        if checkValue == None:
            return None
        if checkValue == "None":
            return None
    try:
        return int(checkValue)
    except:
        return defaultValue

def checkBool(checkValue, defaultValue, allowNone=False):
    if allowNone:
        if checkValue == None:
            return None
        if checkValue == "None":
            return None
    if isinstance(checkValue, str):
        if checkValue == "True":
            return True
        elif checkValue == "False":
            return False
        else:
            return defaultValue
    elif isinstance(checkValue, int):
        if checkValue == 1:
            return True
        elif checkValue == 0:
            return False
        else:
            return defaultValue
    return defaultValue

def colRange(rgbStart, rgbEnd, nStep):

    if len(rgbStart) != 3 and len(rgbEnd) != 3 and nStep < 1:
        logger.error("Cannot create colour range from given parameters")
        return None

    if nStep == 1:
        return rgbStart
    elif nStep == 2:
        return [rgbStart, rgbEnd]

    dC = [0,0,0]
    for c in range(3):
        cA = rgbStart[c]
        cB = rgbEnd[c]
        dC[c] = (cB-cA)/(nStep-1)
    print(dC)
    retCol = [rgbStart]
    for n in range(nStep):
        if n > 0 and n < nStep:
            retCol.append([
                int(retCol[n-1][0] + dC[0]),
                int(retCol[n-1][1] + dC[1]),
                int(retCol[n-1][2] + dC[2]),
            ])
    retCol[-1] = rgbEnd
    print(retCol)

    return retCol

def splitVersionNumber(vString):
    """ Splits a version string on the form aa.bb.cc into major, minor
    and patch, and computes an integer value aabbcc.
    """

    vMajor = 0
    vMinor = 0
    vPatch = 0
    vInt   = 0

    vBits = vString.split(".")
    nBits = len(vBits)

    if nBits > 0:
        vMajor = checkInt(vBits[0],0)
    if nBits > 1:
        vMinor = checkInt(vBits[1],0)
    if nBits > 2:
        vPatch = checkInt(vBits[2],0)

    vInt = vMajor*10000 + vMinor*100 + vPatch

    return [vMajor, vMinor, vPatch, vInt]

def packageRefURL(packName):
    from nw.constants import nwDependencies
    if packName in nwDependencies.PACKS.keys():
        return "<a href=\"%s\">%s</a>" % (
            nwDependencies.PACKS[packName]["site"], packName
        )
    return packName
