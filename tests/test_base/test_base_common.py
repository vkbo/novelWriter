# -*- coding: utf-8 -*-
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

import time
import pytest

from nw.common import (
    checkString, checkBool, checkInt, colRange, formatInt, transferCase,
    fuzzyTime, checkHandle, formatTimeStamp, formatTime, hexToInt,
    makeFileNameSafe
)
from tools import cmpList

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
    assert checkBool("True", False, False)
    assert not checkBool("False", True, False)
    assert checkBool("Boo", None, False) is None
    assert not checkBool(0, None, False)
    assert checkBool(1, None, False)
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
def testBaseCommon_ColRange():
    """Test the colRange function.
    """
    assert colRange([0, 0], [0, 0], 0) is None
    assert cmpList(
        colRange([200, 50, 0], [50, 200, 0], 1),
        [200, 50, 0]
    )
    assert cmpList(
        colRange([200, 50, 0], [50, 200, 0], 2),
        [[200, 50, 0], [50, 200, 0]]
    )
    assert cmpList(
        colRange([200, 50, 0], [50, 200, 0], 3),
        [[200, 50, 0], [125, 125, 0], [50, 200, 0]]
    )
    assert cmpList(
        colRange([200, 50, 0], [50, 200, 0], 4),
        [[200, 50, 0], [150, 100, 0], [100, 150, 0], [50, 200, 0]]
    )
    assert cmpList(
        colRange([200, 50, 0], [50, 200, 0], 5),
        [[200, 50, 0], [162, 87, 0], [124, 124, 0], [86, 161, 0], [50, 200, 0]]
    )

# END Test testBaseCommon_ColRange

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
def testBaseCommon_FormatInt():
    """Test the formatInt function.
    """
    assert formatInt(1000) == "1000"
    assert formatInt(1234) == "1.23\u2009k"
    assert formatInt(12345) == "12.3\u2009k"
    assert formatInt(123456) == "123\u2009k"
    assert formatInt(1234567) == "1.23\u2009M"
    assert formatInt(12345678) == "12.3\u2009M"
    assert formatInt(123456789) == "123\u2009M"
    assert formatInt(1234567890) == "1.23\u2009G"

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
