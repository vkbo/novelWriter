# -*- coding: utf-8 -*-
"""novelWriter Common Class Tester
"""

import pytest
from nw.common import (
    checkString, checkBool, checkInt, colRange, formatInt, transferCase,
    fuzzyTime
)
from nwtools import cmpList

@pytest.mark.core
def testCheckString():
    assert checkString(None, "NotNone", True) is None
    assert checkString("None", "NotNone", True) is None
    assert checkString("None", "NotNone", False) == "None"
    assert checkString(None, "NotNone", False) == "NotNone"
    assert checkString(1, "NotNone", False) == "NotNone"
    assert checkString(1.0, "NotNone", False) == "NotNone"
    assert checkString(True, "NotNone", False) == "NotNone"

@pytest.mark.core
def testCheckInt():
    assert checkInt(None, 3, True) is None
    assert checkInt("None", 3, True) is None
    assert checkInt(None, 3, False) == 3
    assert checkInt(1, 3, False) == 1
    assert checkInt(1.0, 3, False) == 1
    assert checkInt(True, 3, False) == 1

@pytest.mark.core
def testCheckBool():
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

@pytest.mark.core
def testColRange():
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

@pytest.mark.core
def testFormatInt():
    assert formatInt(1000) == "1000"
    assert formatInt(1234) == "1.23k"
    assert formatInt(12345) == "12.3k"
    assert formatInt(123456) == "123k"
    assert formatInt(1234567) == "1.23M"
    assert formatInt(12345678) == "12.3M"
    assert formatInt(123456789) == "123M"
    assert formatInt(1234567890) == "1.23G"

@pytest.mark.core
def testTransferCase():
    assert transferCase(1, "TaRgEt") == "TaRgEt"
    assert transferCase("source", 1) == 1
    assert transferCase("", "TaRgEt") == "TaRgEt"
    assert transferCase("source", "") == ""
    assert transferCase("Source", "target") == "Target"
    assert transferCase("SOURCE", "target") == "TARGET"
    assert transferCase("source", "TARGET") == "target"

@pytest.mark.core
def testFuzzyTime():
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
