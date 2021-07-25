"""
novelWriter – Common Functions Tester
=====================================

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

import os
import time
import pytest

from datetime import datetime

from tools import writeFile

from nw.common import (
    checkString, checkBool, checkInt, formatInt, transferCase, fuzzyTime,
    checkHandle, formatTimeStamp, parseTimeStamp, formatTime, hexToInt,
    makeFileNameSafe, isHandle, isTitleTag, isItemClass, isItemType,
    isItemLayout, numberToRoman, NWConfigParser
)


@pytest.mark.base
def testBaseCommon_CheckString():
    """Test the checkString function.
    """
    assert checkString(None, "NotNone", True) is None
    assert checkString("None", "NotNone", True) is None
    assert checkString("None", "NotNone", False) == "None"
    assert checkString(None, "NotNone", False) == "NotNone"
    assert checkString(1, "NotNone", False) == "NotNone"
    assert checkString(1.0, "NotNone", False) == "NotNone"
    assert checkString(True, "NotNone", False) == "NotNone"

# END Test testBaseCommon_CheckString


@pytest.mark.base
def testBaseCommon_CheckInt():
    """Test the checkInt function.
    """
    assert checkInt(None, 3, True) is None
    assert checkInt("None", 3, True) is None
    assert checkInt(None, 3, False) == 3
    assert checkInt(1, 3, False) == 1
    assert checkInt(1.0, 3, False) == 1
    assert checkInt(True, 3, False) == 1

# END Test testBaseCommon_CheckInt


@pytest.mark.base
def testBaseCommon_CheckBool():
    """Test the checkBool function.
    """
    assert checkBool(None, 3, True) is None
    assert checkBool("None", 3, True) is None
    assert checkBool("True", False, False) is True
    assert checkBool("False", True, False) is False
    assert checkBool("Boo", None, False) is None
    assert checkBool(0, None, False) is False
    assert checkBool(1, None, False) is True
    assert checkBool(2, None, False) is None
    assert checkBool(0.0, None, False) is None
    assert checkBool(1.0, None, False) is None
    assert checkBool(2.0, None, False) is None

# END Test testBaseCommon_CheckBool


@pytest.mark.base
def testBaseCommon_CheckHandle():
    """Test the checkHandle function.
    """
    assert checkHandle("None", 1, True) is None
    assert checkHandle("None", 1, False) == 1
    assert checkHandle(None, 1, True) is None
    assert checkHandle(None, 1, False) == 1
    assert checkHandle("47666c91c7ccf", None, False) == "47666c91c7ccf"
    assert checkHandle("h7666c91c7ccf", None, False) is None

# END Test testBaseCommon_CheckHandle


@pytest.mark.base
def testBaseCommon_IsHandle():
    """Test the isHandle function.
    """
    assert isHandle("47666c91c7ccf") is True
    assert isHandle("47666C91C7CCF") is False
    assert isHandle("h7666c91c7ccf") is False
    assert isHandle("None") is False
    assert isHandle(None) is False
    assert isHandle("STUFF") is False

# END Test testBaseCommon_IsHandle


@pytest.mark.base
def testBaseCommon_IsTitleTag():
    """Test the isItemClass function.
    """
    assert isTitleTag("T123456") is True

    assert isTitleTag("t123456") is False
    assert isTitleTag("S123456") is False
    assert isTitleTag("T12345A") is False
    assert isTitleTag("T1234567") is False

    assert isTitleTag("None") is False
    assert isTitleTag(None) is False
    assert isTitleTag("STUFF") is False

# END Test testBaseCommon_IsTitleTag


@pytest.mark.base
def testBaseCommon_IsItemClass():
    """Test the isItemClass function.
    """
    assert isItemClass("NO_CLASS") is True
    assert isItemClass("NOVEL") is True
    assert isItemClass("PLOT") is True
    assert isItemClass("CHARACTER") is True
    assert isItemClass("WORLD") is True
    assert isItemClass("TIMELINE") is True
    assert isItemClass("OBJECT") is True
    assert isItemClass("ENTITY") is True
    assert isItemClass("CUSTOM") is True
    assert isItemClass("ARCHIVE") is True
    assert isItemClass("TRASH") is True

    assert isItemClass("None") is False
    assert isItemClass(None) is False
    assert isItemClass("STUFF") is False

# END Test testBaseCommon_IsItemClass


@pytest.mark.base
def testBaseCommon_IsItemType():
    """Test the isItemType function.
    """
    assert isItemType("NO_TYPE") is True
    assert isItemType("ROOT") is True
    assert isItemType("FOLDER") is True
    assert isItemType("FILE") is True
    assert isItemType("TRASH") is True

    assert isItemType("None") is False
    assert isItemType(None) is False
    assert isItemType("STUFF") is False

# END Test testBaseCommon_IsItemType


@pytest.mark.base
def testBaseCommon_IsItemLayout():
    """Test the isItemLayout function.
    """
    assert isItemLayout("NO_LAYOUT") is True
    assert isItemLayout("TITLE") is True
    assert isItemLayout("BOOK") is True
    assert isItemLayout("PAGE") is True
    assert isItemLayout("PARTITION") is True
    assert isItemLayout("UNNUMBERED") is True
    assert isItemLayout("CHAPTER") is True
    assert isItemLayout("SCENE") is True
    assert isItemLayout("NOTE") is True

    assert isItemLayout("None") is False
    assert isItemLayout(None) is False
    assert isItemLayout("STUFF") is False

# END Test testBaseCommon_IsItemLayout


@pytest.mark.base
def testBaseCommon_HexToInt():
    """Test the hexToInt function.
    """
    assert hexToInt(1) == 0
    assert hexToInt("1") == 1
    assert hexToInt("0xff") == 255
    assert hexToInt("0xffff") == 65535
    assert hexToInt("0xffffq") == 0
    assert hexToInt("0xffffq", 12) == 12

# END Test testBaseCommon_HexToInt


@pytest.mark.base
def testBaseCommon_FormatTimeStamp():
    """Test the formatTimeStamp function.
    """
    tTime = time.mktime(time.gmtime(0))
    assert formatTimeStamp(tTime, False) == "1970-01-01 00:00:00"
    assert formatTimeStamp(tTime, True) == "1970-01-01 00.00.00"

# END Test testBaseCommon_FormatTimeStamp


@pytest.mark.base
def testBaseCommon_FormatTime():
    """Test the formatTime function.
    """
    assert formatTime("1") == "ERROR"
    assert formatTime(1.0) == "ERROR"
    assert formatTime(1) == "00:00:01"
    assert formatTime(59) == "00:00:59"
    assert formatTime(60) == "00:01:00"
    assert formatTime(180) == "00:03:00"
    assert formatTime(194) == "00:03:14"
    assert formatTime(3540) == "00:59:00"
    assert formatTime(3599) == "00:59:59"
    assert formatTime(3600) == "01:00:00"
    assert formatTime(11640) == "03:14:00"
    assert formatTime(11655) == "03:14:15"
    assert formatTime(86399) == "23:59:59"
    assert formatTime(86400) == "1-00:00:00"
    assert formatTime(360000) == "4-04:00:00"

# END Test testBaseCommon_FormatTime


@pytest.mark.base
def testBaseCommon_ParseTimeStamp():
    """Test the parseTimeStamp function.
    """
    localEpoch = datetime(2000, 1, 1).timestamp()
    assert parseTimeStamp(None, 0.0, allowNone=True) is None
    assert parseTimeStamp("None", 0.0, allowNone=True) is None
    assert parseTimeStamp("None", 0.0) == 0.0
    assert parseTimeStamp("2000-01-01 00:00:00", 123.0) == localEpoch
    assert parseTimeStamp("2000-13-01 00:00:00", 123.0) == 123.0
    assert parseTimeStamp("2000-01-32 00:00:00", 123.0) == 123.0

# END Test testBaseCommon_ParseTimeStamp


@pytest.mark.base
def testBaseCommon_FormatInt():
    """Test the formatInt function.
    """
    # Normal Cases
    assert formatInt(1) == "1"
    assert formatInt(12) == "12"
    assert formatInt(123) == "123"
    assert formatInt(1234) == "1.23\u2009k"
    assert formatInt(12345) == "12.3\u2009k"
    assert formatInt(123456) == "123\u2009k"
    assert formatInt(1234567) == "1.23\u2009M"
    assert formatInt(12345678) == "12.3\u2009M"
    assert formatInt(123456789) == "123\u2009M"
    assert formatInt(1234567890) == "1.23\u2009G"

    # Exceptions
    assert formatInt(12.3) == "ERR"
    assert formatInt(None) == "ERR"
    assert formatInt("42") == "ERR"

# END Test testBaseCommon_FormatInt


@pytest.mark.base
def testBaseCommon_TransferCase():
    """Test the transferCase function.
    """
    assert transferCase(1, "TaRgEt") == "TaRgEt"
    assert transferCase("source", 1) == 1
    assert transferCase("", "TaRgEt") == "TaRgEt"
    assert transferCase("source", "") == ""
    assert transferCase("Source", "target") == "Target"
    assert transferCase("SOURCE", "target") == "TARGET"
    assert transferCase("source", "TARGET") == "target"

# END Test testBaseCommon_TransferCase


@pytest.mark.base
def testBaseCommon_FuzzyTime():
    """Test the fuzzyTime function.
    """
    assert fuzzyTime(-1) == "in the future"
    assert fuzzyTime(0) == "just now"
    assert fuzzyTime(29) == "just now"
    assert fuzzyTime(30) == "a minute ago"
    assert fuzzyTime(89) == "a minute ago"
    assert fuzzyTime(90) == "2 minutes ago"
    assert fuzzyTime(149) == "2 minutes ago"
    assert fuzzyTime(151) == "3 minutes ago"
    assert fuzzyTime(3299) == "55 minutes ago"
    assert fuzzyTime(3300) == "an hour ago"
    assert fuzzyTime(5399) == "an hour ago"
    assert fuzzyTime(5400) == "2 hours ago"
    assert fuzzyTime(84599) == "23 hours ago"
    assert fuzzyTime(84600) == "a day ago"
    assert fuzzyTime(129599) == "a day ago"
    assert fuzzyTime(129600) == "2 days ago"
    assert fuzzyTime(561599) == "6 days ago"
    assert fuzzyTime(561600) == "a week ago"
    assert fuzzyTime(907199) == "a week ago"
    assert fuzzyTime(907200) == "2 weeks ago"
    assert fuzzyTime(2419199) == "4 weeks ago"
    assert fuzzyTime(2419200) == "a month ago"
    assert fuzzyTime(3887999) == "a month ago"
    assert fuzzyTime(3888000) == "2 months ago"
    assert fuzzyTime(29807999) == "11 months ago"
    assert fuzzyTime(29808000) == "a year ago"
    assert fuzzyTime(47336399) == "a year ago"
    assert fuzzyTime(47336400) == "2 years ago"

# END Test testBaseCommon_FuzzyTime


@pytest.mark.base
def testBaseCommon_MakeFileNameSafe():
    """Test the fuzzyTime function.
    """
    assert makeFileNameSafe(" aaaa ") == "aaaa"
    assert makeFileNameSafe("aaaa,bbbb") == "aaaabbbb"
    assert makeFileNameSafe("aaaa\tbbbb") == "aaaabbbb"
    assert makeFileNameSafe("aaaa bbbb") == "aaaa bbbb"

# END Test testBaseCommon_MakeFileNameSafe


@pytest.mark.core
def testBaseCommon_RomanNumbers():
    """Test conversion of integers to Roman numbers.
    """
    assert numberToRoman(None, False) == "NAN"
    assert numberToRoman(0, False) == "OOR"
    assert numberToRoman(1, False) == "I"
    assert numberToRoman(2, False) == "II"
    assert numberToRoman(3, False) == "III"
    assert numberToRoman(4, False) == "IV"
    assert numberToRoman(5, False) == "V"
    assert numberToRoman(6, False) == "VI"
    assert numberToRoman(7, False) == "VII"
    assert numberToRoman(8, False) == "VIII"
    assert numberToRoman(9, False) == "IX"
    assert numberToRoman(10, False) == "X"
    assert numberToRoman(14, False) == "XIV"
    assert numberToRoman(42, False) == "XLII"
    assert numberToRoman(99, False) == "XCIX"
    assert numberToRoman(142, False) == "CXLII"
    assert numberToRoman(542, False) == "DXLII"
    assert numberToRoman(999, False) == "CMXCIX"
    assert numberToRoman(2010, False) == "MMX"
    assert numberToRoman(999, True) == "cmxcix"

# END Test testBaseCommon_RomanNumbers


@pytest.mark.base
def testBaseCommon_NWConfigParser(fncDir):
    """Test the NWConfigParser subclass.
    """
    tstConf = os.path.join(fncDir, "test.cfg")
    writeFile(tstConf, (
        "[main]\n"
        "stropt = value\n"
        "intopt1 = 42\n"
        "intopt2 = 42.43\n"
        "boolopt1 = true\n"
        "boolopt2 = TRUE\n"
        "boolopt3 = 1\n"
        "boolopt4 = 0\n"
        "list1 = a, b, c\n"
        "list2 = 17, 18, 19\n"
    ))

    cfgParser = NWConfigParser()
    cfgParser.read(tstConf)

    # Readers
    # =======

    # Read String
    assert cfgParser.rdStr("main", "stropt",   "stuff") == "value"
    assert cfgParser.rdStr("main", "boolopt1", "stuff") == "true"
    assert cfgParser.rdStr("main", "intopt1",  "stuff") == "42"

    assert cfgParser.rdStr("nope", "stropt",   "stuff") == "stuff"
    assert cfgParser.rdStr("main", "blabla",   "stuff") == "stuff"

    # Read Boolean
    assert cfgParser.rdBool("main", "boolopt1", None) is True
    assert cfgParser.rdBool("main", "boolopt2", None) is True
    assert cfgParser.rdBool("main", "boolopt3", None) is True
    assert cfgParser.rdBool("main", "boolopt4", None) is False
    assert cfgParser.rdBool("main", "intopt1",  None) is None

    assert cfgParser.rdBool("nope", "boolopt1", None) is None
    assert cfgParser.rdBool("main", "blabla",   None) is None

    # Read Integer
    assert cfgParser.rdInt("main", "intopt1", 13) == 42
    assert cfgParser.rdInt("main", "intopt2", 13) == 13
    assert cfgParser.rdInt("main", "stropt",  13) == 13

    assert cfgParser.rdInt("nope", "intopt1", 13) == 13
    assert cfgParser.rdInt("main", "blabla",  13) == 13

    # Read String List
    assert cfgParser.rdStrList("main", "list1", []) == []
    assert cfgParser.rdStrList("main", "list1", ["x"]) == ["a"]
    assert cfgParser.rdStrList("main", "list1", ["x", "y"]) == ["a", "b"]
    assert cfgParser.rdStrList("main", "list1", ["x", "y", "z"]) == ["a", "b", "c"]
    assert cfgParser.rdStrList("main", "list1", ["x", "y", "z", "w"]) == ["a", "b", "c", "w"]

    assert cfgParser.rdStrList("main", "stropt", ["x"]) == ["value"]
    assert cfgParser.rdStrList("main", "intopt1", ["x"]) == ["42"]

    assert cfgParser.rdStrList("nope", "list1", ["x"]) == ["x"]
    assert cfgParser.rdStrList("main", "blabla", ["x"]) == ["x"]

    # Read Integer List
    assert cfgParser.rdIntList("main", "list2", []) == []
    assert cfgParser.rdIntList("main", "list2", [1]) == [17]
    assert cfgParser.rdIntList("main", "list2", [1, 2]) == [17, 18]
    assert cfgParser.rdIntList("main", "list2", [1, 2, 3]) == [17, 18, 19]
    assert cfgParser.rdIntList("main", "list2", [1, 2, 3, 4]) == [17, 18, 19, 4]

    assert cfgParser.rdIntList("main", "stropt", [1]) == [1]
    assert cfgParser.rdIntList("main", "boolopt1", [1]) == [1]

    assert cfgParser.rdIntList("nope", "list2", [1]) == [1]
    assert cfgParser.rdIntList("main", "blabla", [1]) == [1]

    # Internal
    # ========

    assert cfgParser._parseLine("main", "stropt", None, 999) is None

# END Test testBaseCommon_NWConfigParser
