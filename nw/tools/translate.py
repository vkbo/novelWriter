# -*- coding: utf-8 -*-
"""novelWriter Translate Tools

 novelWriter – Translate Tools
===============================
 Various translate tools

 File History:
 Created: 2019-10-13 [0.2.3]

"""

import logging
import nw

logger = logging.getLogger(__name__)

def numberToWord(numVal, theLanguage):
    numWord = ""
    if theLanguage == "en":
        numWord = _numberToWordEN(numVal)
    else:
        numWord = _numberToWordEN(numVal)
    # print("%4d : %s" % (numVal, numWord))
    return numWord

def _numberToWordEN(numVal):

    numWord = ""
    oneWord = ""
    tenWord = ""
    hunWord = ""

    if numVal == 0:
        return "Zero"

    oneVal = numVal % 10
    tenVal = (numVal-oneVal) % 100
    hunVal = (numVal-tenVal-oneVal) % 1000

    if hunVal == 100: hunWord = "One Hundred"
    if hunVal == 200: hunWord = "Two Hundred"
    if hunVal == 300: hunWord = "Three Hundred"
    if hunVal == 400: hunWord = "Four Hundred"
    if hunVal == 500: hunWord = "Five Hundred"
    if hunVal == 600: hunWord = "Six Hundred"
    if hunVal == 700: hunWord = "Seven Hundred"
    if hunVal == 800: hunWord = "Eight Hundred"
    if hunVal == 900: hunWord = "Nine Hundred"

    if tenVal == 20: tenWord = "Twenty"
    if tenVal == 30: tenWord = "Thirty"
    if tenVal == 40: tenWord = "Forty"
    if tenVal == 50: tenWord = "Fifty"
    if tenVal == 60: tenWord = "Sixty"
    if tenVal == 70: tenWord = "Seventy"
    if tenVal == 80: tenWord = "Eighty"
    if tenVal == 90: tenWord = "Ninety"

    if tenVal == 10:
        if oneVal == 0: oneWord = "Ten"
        if oneVal == 1: oneWord = "Eleven"
        if oneVal == 2: oneWord = "Twelve"
        if oneVal == 3: oneWord = "Thirteen"
        if oneVal == 4: oneWord = "Fourteen"
        if oneVal == 5: oneWord = "Fifteen"
        if oneVal == 6: oneWord = "Sixteen"
        if oneVal == 7: oneWord = "Seventeen"
        if oneVal == 8: oneWord = "Eighteen"
        if oneVal == 9: oneWord = "Nineteen"
        numWord = ("%s %s" % (hunWord, oneWord)).strip()
    else:
        if oneVal == 0: oneWord = ""
        if oneVal == 1: oneWord = "One"
        if oneVal == 2: oneWord = "Two"
        if oneVal == 3: oneWord = "Three"
        if oneVal == 4: oneWord = "Four"
        if oneVal == 5: oneWord = "Five"
        if oneVal == 6: oneWord = "Six"
        if oneVal == 7: oneWord = "Seven"
        if oneVal == 8: oneWord = "Eight"
        if oneVal == 9: oneWord = "Nine"
        if tenVal == 0:
            numWord = ("%s %s" % (hunWord, oneWord)).strip()
        else:
            if oneVal == 0:
                numWord = ("%s %s" % (hunWord, tenWord)).strip()
            else:
                numWord = ("%s %s-%s" % (hunWord, tenWord, oneWord)).strip()

    return numWord
