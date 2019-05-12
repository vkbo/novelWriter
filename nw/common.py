# -*- coding: utf-8 -*-
"""novelWriter Common Functions

 novelWriter – Common Functions
================================
 Various functions used multiple places

 File History:
 Created: 2019-05-12 [0.1.0]

"""

import logging
import nw

logger = logging.getLogger(__name__)

def checkString(checkValue, defaultValue, allowNone=False):
    if allowNone:
        if checkValue == None:   return None
        if checkValue == "None": return None
    if isinstance(checkValue,str): return str(checkValue)
    return defaultValue

def checkInt(checkValue, defaultValue, allowNone=False):
    if allowNone:
        if checkValue == None:   return None
        if checkValue == "None": return None
    try:
        return int(checkValue)
    except:
        return defaultValue

def checkBool(checkValue, defaultValue, allowNone=False):
    if allowNone:
        if checkValue == None:   return None
        if checkValue == "None": return None
    if isinstance(checkValue, str):
        if checkValue == "True":
            return True
        elif checkValue == "False":
            return False
        else:
            return defaultValue
    elif isinstance(checkValue, int):
        if checkValue == 1:
            return True
        elif checkValue == 0:
            return False
        else:
            return defaultValue
    return defaultValue
