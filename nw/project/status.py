# -*- coding: utf-8 -*-
"""novelWriter Item Status

 novelWriter – Item Status
===========================
 Class holding the project's item statuses

 File History:
 Created: 2019-05-19 [0.1.3]

"""

import logging
import nw

from lxml import etree

from nw.common import checkInt

logger = logging.getLogger(__name__)

class NWStatus():

    def __init__(self):
        self.theLabels  = []
        self.theColours = []
        self.theCounts  = []
        self.theMap     = {}
        self.theLength  = 0
        self.theIndex   = 0
        return

    def addEntry(self, theLabel, theColours):
        theLabel = theLabel.strip()
        if self.lookupEntry(theLabel) is None:
            self.theLabels.append(theLabel)
            self.theColours.append(theColours)
            self.theCounts.append(0)
            self.theMap[theLabel] = self.theLength
            self.theLength += 1
        return True

    def lookupEntry(self, theLabel):
        theLabel = theLabel.strip()
        if theLabel in self.theMap.keys():
            return self.theMap[theLabel]
        return None

    def checkEntry(self, theStatus):
        if isinstance(theStatus, str):
            theStatus = theStatus.strip()
            if self.lookupEntry(theStatus) is not None:
                return theStatus
        theStatus = checkInt(theStatus, 0, False)
        if theStatus >= 0 and theStatus < self.theLength:
            return self.theLabels[theStatus]

    def setNewEntries(self, newList):

        replaceMap = {}

        if newList is not None:

            self.theLabels  = []
            self.theColours = []
            self.theCounts  = []
            self.theMap     = {}
            self.theLength  = 0
            self.theIndex   = 0

            for nName, nR, nG, nB, oName in newList:
                self.addEntry(nName, (nR, nG, nB))
                if nName != oName and oName is not None:
                    replaceMap[oName] = nName

        return replaceMap

    def resetCounts(self):
        self.theCounts = [0]*self.theLength
        return

    def countEntry(self, theLabel):
        theIndex = self.lookupEntry(theLabel)
        if theIndex is not None:
            self.theCounts[theIndex] += 1
        return

    def packEntries(self, xParent):
        for n in range(self.theLength):
            xSub = etree.SubElement(xParent,"entry",attrib={
                "blue"  : str(self.theColours[n][2]),
                "green" : str(self.theColours[n][1]),
                "red"   : str(self.theColours[n][0]),
            })
            xSub.text = self.theLabels[n]
        return True

    def unpackEntries(self, xParent):

        theLabels  = []
        theColours = []

        for xChild in xParent:
            theLabels.append(xChild.text)
            if "red" in xChild.attrib:
                cR = checkInt(xChild.attrib["red"],0,False)
            else:
                cR = 0
            if "green" in xChild.attrib:
                cG = checkInt(xChild.attrib["green"],0,False)
            else:
                cG = 0
            if "blue" in xChild.attrib:
                cB = checkInt(xChild.attrib["blue"],0,False)
            else:
                cB = 0
            theColours.append((cR,cG,cB))

        if len(theLabels) > 0:
            self.theLabels  = []
            self.theColours = []
            self.theCounts  = []
            self.theMap     = {}
            self.theLength  = 0
            self.theIndex   = 0

            for n in range(len(theLabels)):
                self.addEntry(theLabels[n], theColours[n])

        return True

    ##
    #  Iterator Bits
    ##

    def __getitem__(self, n):
        if n >= 0 and n < self.theLength:
            return self.theLabels[n], self.theColours[n], self.theCounts[n]
        return None, None, None

    def __iter__(self):
        self.theIndex = 0
        return self

    def __next__(self):
        if self.theIndex < self.theLength:
            theLabel, theColour, theCount = self.__getitem__(self.theIndex)
            self.theIndex += 1
            return theLabel, theColour, theCount
        else:
            raise StopIteration

# END Class NWStatus
