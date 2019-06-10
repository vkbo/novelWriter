# -*- coding: utf-8 -*-
"""novelWriter Constants

 novelWriter – Constants
=========================
 Constants for translating flags and enums to text

 File History:
 Created: 2019-04-28 [0.0.1]

"""

from nw.enum import nwItemClass, nwItemLayout

class nwFiles():

    APP_ICON   = "novelWriter.svg"
    PROJ_FILE  = "nwProject.nwx"
    PROJ_DICT  = "wordlist.txt"
    SESS_INFO  = "sessionInfo.log"
    INDEX_FILE = "tagsIndex.json"

# END Class nwFiles

class nwLabels():

    CLASS_NAME = {
        nwItemClass.NO_CLASS  : "None",
        nwItemClass.NOVEL     : "Novel",
        nwItemClass.PLOT      : "Plot",
        nwItemClass.CHARACTER : "Characters",
        nwItemClass.WORLD     : "Locations",
        nwItemClass.TIMELINE  : "Timeline",
        nwItemClass.OBJECT    : "Objects",
        nwItemClass.CUSTOM    : "Custom",
        nwItemClass.TRASH     : "Trash",
    }
    CLASS_FLAG = {
        nwItemClass.NO_CLASS  : "0",
        nwItemClass.NOVEL     : "N",
        nwItemClass.PLOT      : "P",
        nwItemClass.CHARACTER : "C",
        nwItemClass.WORLD     : "L",
        nwItemClass.TIMELINE  : "T",
        nwItemClass.OBJECT    : "O",
        nwItemClass.CUSTOM    : "X",
        nwItemClass.TRASH     : "R",
    }
    LAYOUT_NAME = {
        nwItemLayout.NO_LAYOUT  : "None",
        nwItemLayout.TITLE      : "Title Page",
        nwItemLayout.BOOK       : "Book",
        nwItemLayout.PAGE       : "Plain Page",
        nwItemLayout.PARTITION  : "Partition",
        nwItemLayout.UNNUMBERED : "Un-Numbered",
        nwItemLayout.CHAPTER    : "Chapter",
        nwItemLayout.SCENE      : "Scene",
        nwItemLayout.NOTE       : "Note",
    }
    LAYOUT_FLAG = {
        nwItemLayout.NO_LAYOUT  : "Xo",
        nwItemLayout.TITLE      : "Tt",
        nwItemLayout.BOOK       : "Bk",
        nwItemLayout.PAGE       : "Pg",
        nwItemLayout.PARTITION  : "Pt",
        nwItemLayout.UNNUMBERED : "Un",
        nwItemLayout.CHAPTER    : "Ch",
        nwItemLayout.SCENE      : "Sc",
        nwItemLayout.NOTE       : "Nt",
    }

# END Class nwLabels

class nwQuotes():

    SINGLE = [
        ("'",  "'",  "Straight"),
        ("‘",  "’",  "English"),
        ("‹",  "›",  "French"),
        ("›",  "‹",  "Danish"),
        ("’",  "’",  "Swedish"),
        ("‚",  "‘",  "German"),
        ("’",  "‚",  "Dutch"),
    ]
    DOUBLE = [
        ("\"", "\"", "Straight"),
        ("“",  "”",  "English"),
        ("«",  "»",  "French"),
        ("»",  "«",  "Danish"),
        ("”",  "”",  "Swedish"),
        ("„",  "“",  "German"),
        ("„",  "”",  "Dutch"),
    ]

# END Class nwQuotes
