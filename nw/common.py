# -*- coding: utf-8 -*-
"""
novelWriter – Common Functions
==============================
Various common functions

File History:
Created: 2019-05-12 [0.1.0]

This file is a part of novelWriter
Copyright 2018–2021, Veronica Berglyd Olsen

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

from datetime import datetime

from PyQt5.QtWidgets import qApp
from PyQt5.QtCore import QCoreApplication

from nw.enum import nwItemClass, nwItemType, nwItemLayout
from nw.constants import nwConst, nwUnicode

logger = logging.getLogger(__name__)

def checkString(value, default, allowNone=False):
    """Check if a variable is a string or a none.
    """
    if allowNone:
        if value is None:
            return None
        if value == "None":
            return None
    if isinstance(value, str):
        return str(value)
    return default

def checkInt(value, default, allowNone=False):
    """Check if a variable is an integer or a none.
    """
    if allowNone:
        if value is None:
            return None
        if value == "None":
            return None
    try:
        return int(value)
    except Exception:
        return default

def checkBool(value, default, allowNone=False):
    """Check if a variable is a boolean or a none.
    """
    if allowNone:
        if value is None:
            return None
        if value == "None":
            return None
    if isinstance(value, str):
        if value == "True":
            return True
        elif value == "False":
            return False
        else:
            return default
    elif isinstance(value, int):
        if value == 1:
            return True
        elif value == 0:
            return False
        else:
            return default
    return default

def checkHandle(value, default, allowNone=False):
    """Check if a value is a handle.
    """
    if allowNone:
        if value is None:
            return None
        if value == "None":
            return None
    if isHandle(value):
        return str(value)
    return default

def isHandle(theString):
    """Check if a string is a valid novelWriter handle.
    Note: This is case sensitive. Must be lower case!
    """
    if not isinstance(theString, str):
        return False
    if len(theString) != 13:
        return False
    for c in theString:
        if c not in "0123456789abcdef":
            return False
    return True

def isTitleTag(theString):
    """Check if a string is a valid title string.
    """
    if not isinstance(theString, str):
        return False
    if len(theString) != 7:
        return False
    if not theString.startswith("T"):
        return False
    for c in theString[1:]:
        if c not in "0123456789":
            return False
    return True

def isItemClass(theString):
    """Check if an item is a calid nwItemClass identifier.
    """
    return theString in nwItemClass.__members__

def isItemType(theString):
    """Check if an item is a calid nwItemType identifier.
    """
    return theString in nwItemType.__members__

def isItemLayout(theString):
    """Check if an item is a calid nwItemLayout identifier.
    """
    return theString in nwItemLayout.__members__

def hexToInt(value, default=0):
    """Convert a hex string to an integer.
    """
    if isinstance(value, str):
        try:
            return int(value, 16)
        except Exception:
            return default
    return default

def formatInt(theInt):
    """Formats an integer with k, M, G etc.
    """
    postFix = ["k", "M", "G", "T", "P", "E"]
    theVal = float(theInt)

    if theVal > 1000.0:
        for pF in postFix:
            theVal /= 1000.0
            if theVal < 1000.0:
                if theVal < 10.0:
                    return f"{theVal:4.2f}{nwUnicode.U_THSP}{pF}"
                elif theVal < 100.0:
                    return f"{theVal:4.1f}{nwUnicode.U_THSP}{pF}"
                else:
                    return f"{theVal:3.0f}{nwUnicode.U_THSP}{pF}"

    return str(theInt)

def formatTimeStamp(theTime, fileSafe=False):
    """Take a number (on the format returned by time.time()) and convert
    it to a timestamp string.
    """
    if fileSafe:
        return datetime.fromtimestamp(theTime).strftime(nwConst.FMT_FSTAMP)
    else:
        return datetime.fromtimestamp(theTime).strftime(nwConst.FMT_TSTAMP)

def formatTime(tS):
    """Format a time in seconds in HH:MM:SS format or d-HH:MM:SS format
    if a full day or longer.
    """
    if isinstance(tS, int):
        if tS >= 86400:
            return f"{tS//86400:d}-{tS%86400//3600:02d}:{tS%3600//60:02d}:{tS%60:02d}"
        else:
            return f"{tS//3600:02d}:{tS%3600//60:02d}:{tS%60:02d}"
    return "ERROR"

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
        vMajor = checkInt(vBits[0], 0)
    if nBits > 1:
        vMinor = checkInt(vBits[1], 0)
    if nBits > 2:
        vPatch = checkInt(vBits[2], 0)

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

    if theSource.istitle():
        theResult = theTarget.title()

    if theSource.isupper():
        theResult = theTarget.upper()
    elif theSource.islower():
        theResult = theTarget.lower()

    return theResult

def fuzzyTime(secDiff):
    """Converts a time difference in seconds into a fuzzy time string.
    """
    if secDiff < 0:
        return QCoreApplication.translate(
            "Common", "in the future"
        )
    elif secDiff < 30:
        return QCoreApplication.translate(
            "Common", "just now"
        )
    elif secDiff < 90:
        return QCoreApplication.translate(
            "Common", "a minute ago"
        )
    elif secDiff < 3300: # 55 minutes
        return QCoreApplication.translate(
            "Common", "{0} minutes ago"
        ).format(int(round(secDiff/60)))
    elif secDiff < 5400: # 90 minutes
        return QCoreApplication.translate(
            "Common", "an hour ago"
        )
    elif secDiff < 84600: # 23.5 hours
        return QCoreApplication.translate(
            "Common", "{0} hours ago"
        ).format(int(round(secDiff/3600)))
    elif secDiff < 129600: # 1.5 days
        return QCoreApplication.translate(
            "Common", "a day ago"
        )
    elif secDiff < 561600: # 6.5 days
        return QCoreApplication.translate(
            "Common", "{0} days ago"
        ).format(int(round(secDiff/86400)))
    elif secDiff < 907200: # 10.5 days
        return QCoreApplication.translate(
            "Common", "a week ago"
        )
    elif secDiff < 2419200: # 28 days
        return QCoreApplication.translate(
            "Common", "{0} weeks ago"
        ).format(int(round(secDiff/604800)))
    elif secDiff < 3888000: # 45 days
        return QCoreApplication.translate(
            "Common", "a month ago"
        )
    elif secDiff < 29808000: # 345 days
        return QCoreApplication.translate(
            "Common", "{0} months ago"
        ).format(int(round(secDiff/2592000)))
    elif secDiff < 47336400: # 1.5 years
        return QCoreApplication.translate(
            "Common", "a year ago"
        )
    else:
        return QCoreApplication.translate(
            "Common", "{0} years ago"
        ).format(int(round(secDiff/31557600)))

def makeFileNameSafe(theText):
    """Returns a filename safe version of the text.
    """
    cleanName = ""
    for c in theText.strip():
        if c.isalpha() or c.isdigit() or c == " ":
            cleanName += c
    return cleanName

def getGuiItem(theName):
    """Returns a QtWidget based on its objectName.
    """
    for qWidget in qApp.topLevelWidgets():
        if qWidget.objectName() == theName:
            return qWidget
    return None

def numberToRoman(numVal, isLower=False):
    """Convert an integer to a roman number.
    """
    if not isinstance(numVal, int):
        return "NAN"
    if numVal < 1 or numVal > 4999:
        return "OOR"

    theValues = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
        (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]

    romNum = ""
    for theDiv, theSym in theValues:
        n = numVal//theDiv
        romNum += n*theSym
        numVal -= n*theDiv
        if numVal <= 0:
            break

    return romNum.lower() if isLower else romNum
