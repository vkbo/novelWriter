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

import json
import logging

from datetime import datetime
from configparser import ConfigParser

from PyQt5.QtWidgets import qApp
from PyQt5.QtCore import QCoreApplication

from nw.enum import nwItemClass, nwItemType, nwItemLayout
from nw.error import logException
from nw.constants import nwConst, nwUnicode

logger = logging.getLogger(__name__)


# =============================================================================================== #
#  Checker Functions
# =============================================================================================== #

def checkString(value, default, allowNone=False):
    """Check if a variable is a string or a none.
    """
    if allowNone and (value is None or value == "None"):
        return None
    if isinstance(value, str):
        return str(value)
    return default


def checkInt(value, default, allowNone=False):
    """Check if a variable is an integer or a none.
    """
    if allowNone and (value is None or value == "None"):
        return None
    try:
        return int(value)
    except Exception:
        return default


def checkBool(value, default, allowNone=False):
    """Check if a variable is a boolean or a none.
    """
    if allowNone and (value is None or value == "None"):
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
    if allowNone and (value is None or value == "None"):
        return None
    if isHandle(value):
        return str(value)
    return default


# =============================================================================================== #
#  Validator Functions
# =============================================================================================== #

def isHandle(value):
    """Check if a string is a valid novelWriter handle.
    Note: This is case sensitive. Must be lower case!
    """
    if not isinstance(value, str):
        return False
    if len(value) != 13:
        return False
    for c in value:
        if c not in "0123456789abcdef":
            return False
    return True


def isTitleTag(value):
    """Check if a string is a valid title string.
    """
    if not isinstance(value, str):
        return False
    if len(value) != 7:
        return False
    if not value.startswith("T"):
        return False
    for c in value[1:]:
        if c not in "0123456789":
            return False
    return True


def isItemClass(value):
    """Check if a string is a valid nwItemClass identifier.
    """
    return value in nwItemClass.__members__


def isItemType(value):
    """Check if a string is a valid nwItemType identifier.
    """
    return value in nwItemType.__members__


def isItemLayout(value):
    """Check if a string is a valid nwItemLayout identifier.
    """
    return value in nwItemLayout.__members__


def hexToInt(value, default=0):
    """Convert a hex string to an integer.
    """
    if isinstance(value, str):
        try:
            return int(value, 16)
        except Exception:
            return default
    return default


# =============================================================================================== #
#  Formatting Functions
# =============================================================================================== #

def formatInt(value):
    """Formats an integer with k, M, G etc.
    """
    if not isinstance(value, int):
        return "ERR"

    theVal = float(value)
    if theVal > 1000.0:
        for pF in ["k", "M", "G", "T", "P", "E"]:
            theVal /= 1000.0
            if theVal < 1000.0:
                if theVal < 10.0:
                    return f"{theVal:4.2f}{nwUnicode.U_THSP}{pF}"
                elif theVal < 100.0:
                    return f"{theVal:4.1f}{nwUnicode.U_THSP}{pF}"
                else:
                    return f"{theVal:3.0f}{nwUnicode.U_THSP}{pF}"

    return str(value)


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


def parseTimeStamp(theStamp, default, allowNone=False):
    """Parses a text representation of a time stamp and converts it into
    a float. Note that negative timestamps cause an OSError on Windows.
    See https://bugs.python.org/issue29097
    """
    if str(theStamp).lower() == "none" and allowNone:
        return None
    try:
        return datetime.strptime(theStamp, nwConst.FMT_TSTAMP).timestamp()
    except Exception:
        return default


# =============================================================================================== #
#  String Functions
# =============================================================================================== #

def splitVersionNumber(value):
    """Splits a version string on the form aa.bb.cc into major, minor
    and patch, and computes an integer value aabbcc.
    """
    if not isinstance(value, str):
        return [0, 0, 0, 0]

    vMajor = 0
    vMinor = 0
    vPatch = 0
    vInt = 0

    vBits = value.split(".")
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
    elif secDiff < 3300:  # 55 minutes
        return QCoreApplication.translate(
            "Common", "{0} minutes ago"
        ).format(int(round(secDiff/60)))
    elif secDiff < 5400:  # 90 minutes
        return QCoreApplication.translate(
            "Common", "an hour ago"
        )
    elif secDiff < 84600:  # 23.5 hours
        return QCoreApplication.translate(
            "Common", "{0} hours ago"
        ).format(int(round(secDiff/3600)))
    elif secDiff < 129600:  # 1.5 days
        return QCoreApplication.translate(
            "Common", "a day ago"
        )
    elif secDiff < 561600:  # 6.5 days
        return QCoreApplication.translate(
            "Common", "{0} days ago"
        ).format(int(round(secDiff/86400)))
    elif secDiff < 907200:  # 10.5 days
        return QCoreApplication.translate(
            "Common", "a week ago"
        )
    elif secDiff < 2419200:  # 28 days
        return QCoreApplication.translate(
            "Common", "{0} weeks ago"
        ).format(int(round(secDiff/604800)))
    elif secDiff < 3888000:  # 45 days
        return QCoreApplication.translate(
            "Common", "a month ago"
        )
    elif secDiff < 29808000:  # 345 days
        return QCoreApplication.translate(
            "Common", "{0} months ago"
        ).format(int(round(secDiff/2592000)))
    elif secDiff < 47336400:  # 1.5 years
        return QCoreApplication.translate(
            "Common", "a year ago"
        )
    else:
        return QCoreApplication.translate(
            "Common", "{0} years ago"
        ).format(int(round(secDiff/31557600)))


def numberToRoman(numVal, isLower=False):
    """Convert an integer to a Roman number.
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


# =============================================================================================== #
#  Encoder Functions
# =============================================================================================== #

def jsonEncode(data, n=0, nmax=0):
    """Encode a dictionary, list or tuple as a json object or array, and
    indent from level n up to a max level nmax if nmax is larger than 0.
    """
    if not isinstance(data, (dict, list, tuple)):
        return "[]"

    buffer = []
    indent = ""

    for chunk in json.JSONEncoder().iterencode(data):
        if chunk == "":  # pragma: no cover
            # Just a precaution
            continue

        first = chunk[0]
        if chunk in ("{}", "[]"):
            buffer.append(chunk)

        elif first in ("{", "["):
            n += 1
            indent = "\n"+"  "*n
            if n > nmax and nmax > 0:
                buffer.append(chunk)
            else:
                buffer.append(chunk[0] + indent + chunk[1:])

        elif first in ("}", "]"):
            n -= 1
            indent = "\n"+"  "*n
            if n >= nmax and nmax > 0:
                buffer.append(chunk)
            else:
                buffer.append(indent + chunk)

        elif first == ",":
            if n > nmax and nmax > 0:
                buffer.append(chunk)
            else:
                buffer.append(chunk[0] + indent + chunk[1:].lstrip())

        else:
            buffer.append(chunk)

    return "".join(buffer)


# =============================================================================================== #
#  Other Functions
# =============================================================================================== #

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


# =============================================================================================== #
#  Classes
# =============================================================================================== #

class NWConfigParser(ConfigParser):

    CNF_STR   = 0
    CNF_INT   = 1
    CNF_BOOL  = 2
    CNF_S_LST = 3
    CNF_I_LST = 4

    def __init__(self):
        super().__init__()

    def rdStr(self, section, option, default):
        """Read string value.
        """
        return self._parseLine(section, option, default, self.CNF_STR)

    def rdInt(self, section, option, default):
        """Read integer value.
        """
        return self._parseLine(section, option, default, self.CNF_INT)

    def rdBool(self, section, option, default):
        """Read boolean value.
        """
        return self._parseLine(section, option, default, self.CNF_BOOL)

    def rdStrList(self, section, option, default):
        """Read string list.
        """
        return self._parseLine(section, option, default, self.CNF_S_LST)

    def rdIntList(self, section, option, default):
        """Read integer list.
        """
        return self._parseLine(section, option, default, self.CNF_I_LST)

    ##
    #  Internal Functions
    ##

    def _unpackList(self, value, default, type):
        """Unpack a comma-separated string of items into a list.
        """
        inList = value.split(",")
        outList = []
        if isinstance(default, list):
            outList = default.copy()
        for i in range(min(len(inList), len(outList))):
            try:
                if type == self.CNF_S_LST:
                    outList[i] = inList[i].strip()
                elif type == self.CNF_I_LST:
                    outList[i] = int(inList[i].strip())
            except Exception:
                continue
        return outList

    def _parseLine(self, section, option, default, type):
        """Parse a line and return the correct datatype.
        """
        if self.has_option(section, option):
            try:
                if type == self.CNF_STR:
                    return self.get(section, option)
                elif type == self.CNF_INT:
                    return self.getint(section, option)
                elif type == self.CNF_BOOL:
                    return self.getboolean(section, option)
                elif type in (self.CNF_I_LST, self.CNF_S_LST):
                    return self._unpackList(self.get(section, option), default, type)
            except ValueError:
                logger.error("Could not read '%s':'%s' from config", str(section), str(option))
                logException()
                return default

        return default

# END Class NWConfigParser
