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

from nw.enum   import nwItemClass
from nw.common import checkInt

logger = logging.getLogger(__name__)

class NWStatus():

    def __init__(self):
        self.theLabels  = []
        self.theColours = []
        self.theMap     = {}
        self.theCount   = 0
        self.theIndex   = 0
        return

    def addEntry(self, theLabel, theColours):
        theLabel = theLabel.strip()
        if self.lookupEntry(theLabel) is None:
            self.theLabels.append(theLabel)
            self.theColours.append(theColours)
            self.theMap[theLabel] = self.theCount
            self.theCount += 1
        return True

    def lookupEntry(self, theLabel):
        theLabel = theLabel.strip()
        if theLabel in self.theMap.keys():
            return self.theMap[theLabel]
        return None

    def checkEntry(self, theStatus):
        theStatus = theStatus.strip()
        if isinstance(theStatus, str):
            if self.lookupEntry(theStatus) is not None:
                return theStatus
        theStatus = checkInt(theStatus, None, False)
        if theStatus is None:
            return None
        if theStatus >= 0 and theStatus < self.theCount:
            return self.theLabels[theStatus]

    ##
    #  Iterator Bits
    ##

    def __getitem__(self, n):
        if n >= 0 and n < self.theCount:
            return self.theLabels[n], self.theColours[n]
        return None, None

    def __iter__(self):
        self.theIndex = 0
        return self

    def __next__(self):
        if self.theIndex < self.theCount:
            theLabel, theColour = self.__getitem__(self.theIndex)
            self.theIndex += 1
            return theLabel, theColour
        else:
            raise StopIteration

# END Class NWStatus
