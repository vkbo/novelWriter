# -*- coding: utf-8 -*-
"""novelWriter Test Tools
"""

from itertools import chain

from PyQt5.QtWidgets import qApp

def cmpFiles(fileOne, fileTwo, ignoreLines=None):
    """Compare two files, but optionally ignore lines given by a list.
    """
    if ignoreLines is None:
        ignoreLines = []

    try:
        foOne = open(fileOne, mode="r", encoding="utf8")
    except Exception as e:
        print(str(e))
        return False

    try:
        foTwo = open(fileTwo, mode="r", encoding="utf8")
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
    """Compare two iterable objects.
    """
    flatOne = list(chain.from_iterable([listOne]))
    flatTwo = list(chain.from_iterable([listTwo]))
    if len(flatOne) != len(flatTwo):
        return False
    for i in range(len(flatOne)):
        if flatOne[i] != flatTwo[i]:
            return False
    return True

def getGuiItem(theName):
    """Returns a QtWidget based on its objectName.
    """
    for qWidget in qApp.topLevelWidgets():
        if qWidget.objectName() == theName:
            return qWidget
    return None
