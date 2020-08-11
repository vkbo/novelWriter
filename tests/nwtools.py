# -*- coding: utf-8 -*-
"""novelWriter Test Tools
"""

from os import path, mkdir
from itertools import chain

from PyQt5.QtWidgets import qApp

def ensureDir(theDir):
    if not path.isdir(theDir):
        mkdir(theDir)
    return

def cmpFiles(fileOne, fileTwo, ignoreLines=[]):

    try:
        foOne = open(fileOne,mode="r",encoding="utf8")
    except Exception as e:
        print(str(e))
        return False

    try:
        foTwo = open(fileTwo,mode="r",encoding="utf8")
    except Exception as e:
        print(str(e))
        return False

    txtOne = foOne.readlines()
    txtTwo = foTwo.readlines()

    if len(txtOne) != len(txtTwo):
        print("Files are not the same length")
        return False

    diffFound = False
    for n in range(len(txtOne)):
        lnOne = txtOne[n].strip()
        lnTwo = txtTwo[n].strip()

        if n+1 in ignoreLines:
            print("Ignoring line %d" % (n+1))
            continue

        if lnOne != lnTwo:
            print("Diff on line %d:" % (n+1))
            print(" << '%s'" % lnOne)
            print(" >> '%s'" % lnTwo)
            diffFound = True

    foOne.close()
    foTwo.close()

    return not diffFound

def cmpList(listOne, listTwo):
    flatOne = list(chain.from_iterable([listOne]))
    flatTwo = list(chain.from_iterable([listTwo]))
    if len(flatOne) != len(flatTwo):
        return False
    for i in range(len(flatOne)):
        if flatOne[i] != flatTwo[i]:
            return False
    return True

def getGuiItem(theName):
    for qWidget in qApp.topLevelWidgets():
        if qWidget.objectName() == theName:
            return qWidget
