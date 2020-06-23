# -*- coding: utf-8 -*-
"""novelWriter Common Functions

 novelWriter – Common Functions
================================
 Various functions used multiple places

 File History:
 Created: 2019-05-12 [0.1.0]

 This file is a part of novelWriter
 Copyright 2020, Veronica Berglyd Olsen

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import logging
import nw

from datetime import datetime

from nw.constants import nwConst

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

def isHandle(theString):
    """Check if a string is a valid novelWriter handle.
    Note: This is case sensitive. Must be lower case!
    """
    if not isinstance(theString, str):
        return False
    if len(theString) != 13:
        return False
    invalidChar = False
    for c in theString:
        if c not in "0123456789abcdef":
            invalidChar = True
    return not invalidChar

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

def formatInt(theInt):
    """Formats an integer with k, M, G etc.
    """
    postFix = ["k","M","G","T","P","E"]
    theVal = float(theInt)

    if theVal > 1000.0:
        for pF in postFix:
            theVal /= 1000.0
            if theVal < 1000.0:
                if theVal < 10.0:
                    return "%4.2f%s" % (theVal,pF)
                elif theVal < 100.0:
                    return "%4.1f%s" % (theVal,pF)
                else:
                    return "%3.0f%s" % (theVal,pF)

    return "%d" % theInt

def formatTimeStamp(theTime, fileSafe=False):
    """Take a number (on the format returned by time.time()) and convert
    it to a timestamp string.
    """
    if fileSafe:
        return datetime.fromtimestamp(theTime).strftime(nwConst.fStampFmt)
    else:
        return datetime.fromtimestamp(theTime).strftime(nwConst.tStampFmt)

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

def transferCase(theSource, theTarget):
    """Transfers the case of the source word to the target word. This
    will consider all upper or lower, and first char capitalisation.
    """
    theResult = theTarget

    if not isinstance(theSource, str) or not isinstance(theTarget, str):
        return theResult
    if len(theTarget) < 1 or len(theSource) < 1:
        return theResult

    if theSource[0] == theSource[0].upper():
        theResult = theTarget[0].upper() + theTarget[1:]

    if theSource == theSource.upper():
        theResult = theTarget.upper()
    elif theSource == theSource.lower():
        theResult = theTarget.lower()

    return theResult

def fuzzyTime(secDiff):
    """Converts a time difference in seconds into a fuzzy time string.
    """
    if secDiff < 0:
        return "in the future"
    elif secDiff < 30:
        return "just now"
    elif secDiff < 90:
        return "a minute ago"
    elif secDiff < 3300: # 55 minutes
        return "%d minutes ago" % int(round(secDiff/60))
    elif secDiff < 5400: # 90 minutes
        return "an hour ago"
    elif secDiff < 84600: # 23.5 hours
        return "%d hours ago" % int(round(secDiff/3600))
    elif secDiff < 129600: # 1.5 days
        return "a day ago"
    elif secDiff < 561600: # 6.5 days
        return "%d days ago" % int(round(secDiff/86400))
    elif secDiff < 907200: # 10.5 days
        return "a week ago"
    elif secDiff < 2419200: # 28 days
        return "%d weeks ago" % int(round(secDiff/604800))
    elif secDiff < 3888000: # 45 days
        return "a month ago"
    elif secDiff < 31104000: # 360 days
        return "%d months ago" % int(round(secDiff/2592000))
    elif secDiff < 47304000: # 1.5 years
        return "a year ago"
    else:
        return "%d years ago" % int(round(secDiff/31557600))

    return "beyond time and space"
