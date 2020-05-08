# -*- coding: utf-8 -*-

# Qt Additions
from nw.gui.additions.qconfiglayout import QConfigLayout
from nw.gui.additions.qswitch import QSwitch

# Main Window Elements
from nw.gui.icons import GuiIcons
from nw.gui.mainmenu import GuiMainMenu
from nw.gui.statusbar import GuiMainStatus
from nw.gui.theme import GuiTheme

# Dialogs
from nw.gui.dialogs.configeditor import GuiConfigEditor
from nw.gui.dialogs.docmerge import GuiDocMerge
from nw.gui.dialogs.docsplit import GuiDocSplit
from nw.gui.dialogs.export import GuiExport
from nw.gui.dialogs.itemeditor import GuiItemEditor
from nw.gui.dialogs.projecteditor import GuiProjectEditor
from nw.gui.dialogs.projectload import GuiProjectLoad
from nw.gui.dialogs.sessionlog import GuiSessionLogView

# GUI Elements
from nw.gui.elements.docdetails import GuiDocDetails
from nw.gui.elements.doceditor import GuiDocEditor
from nw.gui.elements.doctitlebar import GuiDocTitleBar
from nw.gui.elements.doctree import GuiDocTree
from nw.gui.elements.docviewer import GuiDocViewer
from nw.gui.elements.noticebar import GuiNoticeBar
from nw.gui.elements.outline import GuiProjectOutline
from nw.gui.elements.searchbar import GuiSearchBar
from nw.gui.elements.viewdetails import GuiDocViewDetails

# Tools
from nw.gui.tools.dochighlight import GuiDocHighlighter
from nw.gui.tools.optionstate import OptionState
from nw.gui.tools.wordcounter import WordCounter

__all__ = [
    "QConfigLayout",
    "QSwitch",
    "GuiIcons",
    "GuiMainMenu",
    "GuiMainStatus",
    "GuiTheme",
    "GuiConfigEditor",
    "GuiDocMerge",
    "GuiDocSplit",
    "GuiExport",
    "GuiItemEditor",
    "GuiProjectEditor",
    "GuiProjectLoad",
    "GuiSessionLogView",
    "GuiDocDetails",
    "GuiDocEditor",
    "GuiDocTitleBar",
    "GuiDocTree",
    "GuiDocViewer",
    "GuiNoticeBar",
    "GuiProjectOutline",
    "GuiSearchBar",
    "GuiDocViewDetails",
    "GuiDocHighlighter",
    "OptionState",
    "WordCounter",
]
