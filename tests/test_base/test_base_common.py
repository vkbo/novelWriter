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

import hashlib
import os
import time
import pytest

from datetime import datetime

from mock import causeOSError
from tools import writeFile

from novelwriter.guimain import GuiMain
from novelwriter.common import (
    checkString, checkInt, checkFloat, checkBool, checkHandle, isHandle,
    isTitleTag, isItemClass, isItemType, isItemLayout, hexToInt, formatInt,
    formatTimeStamp, formatTime, parseTimeStamp, splitVersionNumber,
    transferCase, fuzzyTime, numberToRoman, jsonEncode, readTextFile,
    makeFileNameSafe, sha256sum, getGuiItem, NWConfigParser
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
def testBaseCommon_CheckFloat():
    """Test the checkFloat function.
    """
    assert checkFloat(None, 3.0, True) is None
    assert checkFloat("None", 3.0, True) is None
    assert checkFloat(None, 3.0, False) == 3.0
    assert checkFloat(1, 3.0, False) == 1.0
    assert checkFloat(1.0, 3.0, False) == 1.0
    assert checkFloat(True, 3.0, False) == 1.0

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
    assert isItemLayout("DOCUMENT") is True
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
def testBaseCommon_SplitVersionNumber():
    """Test the splitVersionNumber function.
    """
    # OK Values
    assert splitVersionNumber("1") == [1, 0, 0, 10000]
    assert splitVersionNumber("1.2") == [1, 2, 0, 10200]
    assert splitVersionNumber("1.2.3") == [1, 2, 3, 10203]
    assert splitVersionNumber("1.2.3.4") == [1, 2, 3, 10203]
    assert splitVersionNumber("99.99.99") == [99, 99, 99, 999999]

    # Failed Values
    assert splitVersionNumber(None) == [0, 0, 0, 0]
    assert splitVersionNumber(1234) == [0, 0, 0, 0]
    assert splitVersionNumber("1.2abc") == [1, 0, 0, 10000]

# END Test testBaseCommon_SplitVersionNumber


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
def testBaseCommon_JsonEncode():
    """Test the jsonEncode function.
    """
    # Wrong type
    assert jsonEncode(None) == "[]"

    # Correct types
    assert jsonEncode([1, 2]) == "[\n  1,\n  2\n]"
    assert jsonEncode((1, 2)) == "[\n  1,\n  2\n]"
    assert jsonEncode({1: 2}) == "{\n  \"1\": 2\n}"

    tstDict = {
        "null": None,
        "one": 1,
        "two": "2",
        "three": 3.0,
        "four": False,
        "five": (1, 2),
        "six": {"a": 1, "b": 2},
        "seven": [],
        "eight": {},
    }

    # Complex Structure
    assert jsonEncode(tstDict) == (
        '{\n'
        '  "null": null,\n'
        '  "one": 1,\n'
        '  "two": "2",\n'
        '  "three": 3.0,\n'
        '  "four": false,\n'
        '  "five": [\n'
        '    1,\n'
        '    2\n'
        '  ],\n'
        '  "six": {\n'
        '    "a": 1,\n'
        '    "b": 2\n'
        '  },\n'
        '  "seven": [],\n'
        '  "eight": {}\n'
        '}'
    )

    # Additional Indent
    assert jsonEncode(tstDict, n=2) == (
        '{\n'
        '      "null": null,\n'
        '      "one": 1,\n'
        '      "two": "2",\n'
        '      "three": 3.0,\n'
        '      "four": false,\n'
        '      "five": [\n'
        '        1,\n'
        '        2\n'
        '      ],\n'
        '      "six": {\n'
        '        "a": 1,\n'
        '        "b": 2\n'
        '      },\n'
        '      "seven": [],\n'
        '      "eight": {}\n'
        '    }'
    )

    # Max Indent
    assert jsonEncode(tstDict, n=0, nmax=1) == (
        '{\n'
        '  "null": null,\n'
        '  "one": 1,\n'
        '  "two": "2",\n'
        '  "three": 3.0,\n'
        '  "four": false,\n'
        '  "five": [1, 2],\n'
        '  "six": {"a": 1, "b": 2},\n'
        '  "seven": [],\n'
        '  "eight": {}\n'
        '}'
    )

# END Test testBaseCommon_JsonEncode


@pytest.mark.base
def testBaseCommon_ReadTextFile(monkeypatch, fncDir, ipsumText):
    """Test the readTextFile function.
    """
    testText = "\n\n".join(ipsumText) + "\n"
    testFile = os.path.join(fncDir, "ipsum.txt")
    writeFile(testFile, testText)

    assert readTextFile(os.path.join(fncDir, "not_a_file.txt")) == ""
    assert readTextFile(testFile) == testText

    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert readTextFile(testFile) == ""

# END Test testBaseCommon_ReadTextFile


@pytest.mark.base
def testBaseCommon_MakeFileNameSafe():
    """Test the makeFileNameSafe function.
    """
    assert makeFileNameSafe(" aaaa ") == "aaaa"
    assert makeFileNameSafe("aaaa,bbbb") == "aaaabbbb"
    assert makeFileNameSafe("aaaa\tbbbb") == "aaaabbbb"
    assert makeFileNameSafe("aaaa bbbb") == "aaaa bbbb"

# END Test testBaseCommon_MakeFileNameSafe


@pytest.mark.base
def testBaseCommon_Sha256Sum(monkeypatch, fncDir, ipsumText):
    """Test the sha256sum function.
    """
    longText = 50*(" ".join(ipsumText) + " ")
    shortText = "This is a short file"
    noneText = ""

    assert len(longText) == 175650

    longFile = os.path.join(fncDir, "long_file.txt")
    shortFile = os.path.join(fncDir, "short_file.txt")
    noneFile = os.path.join(fncDir, "none_file.txt")

    writeFile(longFile, longText)
    writeFile(shortFile, shortText)
    writeFile(noneFile, noneText)

    # Taken with sha256sum command on command line
    longHash = "9b22aee35660da4fae204acbe96aec7f563022746ca2b7a3831f5e44544765eb"
    shortHash = "6d7c9b2722364c471b8a8666bcb35d18500272d05b23b3427288e2e34c6618f0"
    noneHash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    assert sha256sum(longFile) == longHash
    assert sha256sum(shortFile) == shortHash
    assert sha256sum(noneFile) == noneHash

    assert hashlib.sha256(longText.encode("utf-8")).hexdigest() == longHash
    assert hashlib.sha256(shortText.encode("utf-8")).hexdigest() == shortHash
    assert hashlib.sha256(noneText.encode("utf-8")).hexdigest() == noneHash

    with monkeypatch.context() as mp:
        mp.setattr("builtins.open", causeOSError)
        assert sha256sum(longFile) is None
        assert sha256sum(shortFile) is None
        assert sha256sum(noneFile) is None

# END Test testBaseCommon_Sha256Sum


@pytest.mark.base
def testBaseCommon_GetGuiItem(nwGUI):
    """Check the GUI item function.
    """
    assert getGuiItem("gibberish") is None
    assert isinstance(getGuiItem("GuiMain"), GuiMain)

# END Test testBaseCommon_GetGuiItem


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
        "float1 = 4.2\n"
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

    # Read Float
    assert cfgParser.rdFlt("main", "intopt1", 13.0) == 42.0
    assert cfgParser.rdFlt("main", "float1",  13.0) == 4.2
    assert cfgParser.rdInt("main", "stropt",  13.0) == 13.0

    assert cfgParser.rdInt("nope", "intopt1", 13.0) == 13.0
    assert cfgParser.rdInt("main", "blabla",  13.0) == 13.0

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
