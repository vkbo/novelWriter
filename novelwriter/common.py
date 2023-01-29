"""
novelWriter – Common Functions
==============================
Various common functions

File History:
Created: 2019-05-12 [0.1]

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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
import uuid
import hashlib
import logging

from pathlib import Path
from datetime import datetime
from configparser import ConfigParser

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import qApp

from novelwriter.enum import nwItemClass, nwItemType, nwItemLayout
from novelwriter.error import logException
from novelwriter.constants import nwConst, nwUnicode

logger = logging.getLogger(__name__)


# =============================================================================================== #
#  Checker Functions
# =============================================================================================== #

def checkStringNone(value, default):
    """Check if a variable is a string or a None.
    """
    if value is None or value == "None":
        return None
    if isinstance(value, str):
        return str(value)
    return default


def checkString(value, default):
    """Check if a variable is a string.
    """
    if isinstance(value, str):
        return str(value)
    return default


def checkInt(value, default):
    """Check if a variable is an integer.
    """
    try:
        return int(value)
    except Exception:
        return default


def checkFloat(value, default):
    """Check if a variable is a float.
    """
    try:
        return float(value)
    except Exception:
        return default


def checkBool(value, default):
    """Check if a variable is a boolean.
    """
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        check = value.lower()
        if check in ("true", "yes", "on"):
            return True
        elif check in ("false", "no", "off"):
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


def checkUuid(value, default):
    """Try to process a value as an uuid, or return a default.
    """
    try:
        return str(uuid.UUID(value))
    except Exception:
        return default


def checkPath(value, default):
    """Check if a value is a valid path. Non-empty strings are accepted.
    """
    if isinstance(value, Path):
        return value
    elif isinstance(value, str):
        if value.strip():
            return Path(value)
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
    """Check if a string is a valid title tag string.
    """
    if not isinstance(value, str):
        return False
    if len(value) != 5:
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


def minmax(value, minVal, maxVal):
    """Make sure an integer is between min and max value (inclusive).
    """
    return min(maxVal, max(minVal, value))


def checkIntTuple(value, valid, default):
    """Check that an int is an element of a tuple. If it isn't, return
    the default value.
    """
    if isinstance(value, int):
        if value in valid:
            return value
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


def formatTimeStamp(value, fileSafe=False):
    """Take a number (on the format returned by time.time()) and convert
    it to a timestamp string.
    """
    if fileSafe:
        return datetime.fromtimestamp(value).strftime(nwConst.FMT_FSTAMP)
    else:
        return datetime.fromtimestamp(value).strftime(nwConst.FMT_TSTAMP)


def formatTime(t):
    """Format a time in seconds in HH:MM:SS format or d-HH:MM:SS format
    if a full day or longer.
    """
    if isinstance(t, int):
        if t >= 86400:
            return f"{t//86400:d}-{t%86400//3600:02d}:{t%3600//60:02d}:{t%60:02d}"
        else:
            return f"{t//3600:02d}:{t%3600//60:02d}:{t%60:02d}"
    return "ERROR"


# =============================================================================================== #
#  String Functions
# =============================================================================================== #

def simplified(string):
    """Take a string an strip leading and trailing whitespaces, and
    replace all occurences of (multiple) whitespaces with a 0x20 space.
    """
    return " ".join(str(string).strip().split())


def yesNo(value):
    """Convert a boolean evaluated variable to a yes or no.
    """
    return "yes" if value else "no"


def transferCase(source, target):
    """Transfers the case of the source word to the target word. This
    will consider all upper or lower, and first char capitalisation.
    """
    theResult = target

    if not isinstance(source, str) or not isinstance(target, str):
        return theResult
    if len(target) < 1 or len(source) < 1:
        return theResult

    if source.istitle():
        theResult = target.title()

    if source.isupper():
        theResult = target.upper()
    elif source.islower():
        theResult = target.lower()

    return theResult


def fuzzyTime(seconds):
    """Converts a time difference in seconds into a fuzzy time string.
    """
    if seconds < 0:
        return QCoreApplication.translate(
            "Common", "in the future"
        )
    elif seconds < 30:
        return QCoreApplication.translate(
            "Common", "just now"
        )
    elif seconds < 90:
        return QCoreApplication.translate(
            "Common", "a minute ago"
        )
    elif seconds < 3300:  # 55 minutes
        return QCoreApplication.translate(
            "Common", "{0} minutes ago"
        ).format(int(round(seconds/60)))
    elif seconds < 5400:  # 90 minutes
        return QCoreApplication.translate(
            "Common", "an hour ago"
        )
    elif seconds < 84600:  # 23.5 hours
        return QCoreApplication.translate(
            "Common", "{0} hours ago"
        ).format(int(round(seconds/3600)))
    elif seconds < 129600:  # 1.5 days
        return QCoreApplication.translate(
            "Common", "a day ago"
        )
    elif seconds < 561600:  # 6.5 days
        return QCoreApplication.translate(
            "Common", "{0} days ago"
        ).format(int(round(seconds/86400)))
    elif seconds < 907200:  # 10.5 days
        return QCoreApplication.translate(
            "Common", "a week ago"
        )
    elif seconds < 2419200:  # 28 days
        return QCoreApplication.translate(
            "Common", "{0} weeks ago"
        ).format(int(round(seconds/604800)))
    elif seconds < 3888000:  # 45 days
        return QCoreApplication.translate(
            "Common", "a month ago"
        )
    elif seconds < 29808000:  # 345 days
        return QCoreApplication.translate(
            "Common", "{0} months ago"
        ).format(int(round(seconds/2592000)))
    elif seconds < 47336400:  # 1.5 years
        return QCoreApplication.translate(
            "Common", "a year ago"
        )
    else:
        return QCoreApplication.translate(
            "Common", "{0} years ago"
        ).format(int(round(seconds/31557600)))


def numberToRoman(value, toLower=False):
    """Convert an integer to a Roman number.
    """
    if not isinstance(value, int):
        return "NAN"
    if value < 1 or value > 4999:
        return "OOR"

    lookup = [
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
        (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    ]

    roman = ""
    for divisor, symbol in lookup:
        n = value//divisor
        roman += n*symbol
        value -= n*divisor
        if value <= 0:
            break

    return roman.lower() if toLower else roman


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
#  File and File System Functions
# =============================================================================================== #

def readTextFile(path):
    """Read the content of a text file in a robust manner.
    """
    path = Path(path)
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        logger.error("Could not read file: %s", path)
        logException()
        return ""


def makeFileNameSafe(value):
    """Returns a filename safe string of the value.
    """
    clean = ""
    for c in str(value).strip():
        if c.isalpha() or c.isdigit() or c == " ":
            clean += c
    return clean


def sha256sum(path):
    """Make a shasum of a file using a buffer.
    Based on: https://stackoverflow.com/a/44873382/5825851
    """
    digest = hashlib.sha256()
    bData = bytearray(65536)
    mData = memoryview(bData)
    try:
        with open(path, mode="rb", buffering=0) as inFile:
            for n in iter(lambda: inFile.readinto(mData), 0):
                digest.update(mData[:n])
    except Exception:
        logger.error("Could not create sha256sum of: %s", path)
        logException()
        return None

    return digest.hexdigest()


# =============================================================================================== #
#  Other Functions
# =============================================================================================== #

def getGuiItem(objName):
    """Returns a QtWidget based on its objectName.
    """
    for qWidget in qApp.topLevelWidgets():
        if qWidget.objectName() == objName:
            return qWidget
    return None


# =============================================================================================== #
#  Classes
# =============================================================================================== #

class NWConfigParser(ConfigParser):

    def __init__(self):
        super().__init__()

    def rdStr(self, section, option, default):
        """Read string value.
        """
        return self.get(section, option, fallback=default)

    def rdInt(self, section, option, default):
        """Read integer value.
        """
        try:
            return self.getint(section, option, fallback=default)
        except ValueError:
            logger.error("Could not read '%s':'%s' from config", section, option)
        return default

    def rdFlt(self, section, option, default):
        """Read float value.
        """
        try:
            return self.getfloat(section, option, fallback=default)
        except ValueError:
            logger.error("Could not read '%s':'%s' from config", section, option)
        return default

    def rdBool(self, section, option, default):
        """Read boolean value.
        """
        try:
            return self.getboolean(section, option, fallback=default)
        except ValueError:
            logger.error("Could not read '%s':'%s' from config", section, option)
        return default

    def rdPath(self, section, option, default):
        """Read a path value.
        """
        return checkPath(self.get(section, option, fallback=default), default)

    def rdStrList(self, section, option, default):
        """Read string list.
        """
        result = default.copy() if isinstance(default, list) else []
        if self.has_option(section, option):
            data = self.get(section, option, fallback="").split(",")
            for i in range(min(len(data), len(result))):
                result[i] = data[i].strip()
        return result

    def rdIntList(self, section, option, default):
        """Read integer list.
        """
        result = default.copy() if isinstance(default, list) else []
        if self.has_option(section, option):
            data = self.get(section, option, fallback="").split(",")
            for i in range(min(len(data), len(result))):
                result[i] = checkInt(data[i].strip(), result[i])
        return result

# END Class NWConfigParser
