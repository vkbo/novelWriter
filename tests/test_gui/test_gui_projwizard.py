# -*- coding: utf-8 -*-
"""
novelWriter – New Project Wizard Class Tester
=============================================

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

import pytest
import os
import sys

from tools import getGuiItem

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QWizard, QMessageBox

from nw.gui import GuiProjectWizard
from nw.constants import nwItemClass
from nw.gui.projwizard import (
    ProjWizardIntroPage, ProjWizardFolderPage, ProjWizardPopulatePage,
    ProjWizardCustomPage, ProjWizardFinalPage
)

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testGuiProjectWizard_Main(qtbot, monkeypatch, nwGUI, nwMinimal):
    """Test the new project wizard.
    """
    # Block message box
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.Yes)

    if sys.platform.startswith("darwin"):
        # Disable for macOS because the test segfaults on QWizard.show()
        return

    ##
    #  Test New Project Function
    ##

    # New with a project open should cause an error
    assert nwGUI.openProject(nwMinimal)
    assert not nwGUI.newProject()

    # Close project, but call with invalid path
    assert nwGUI.closeProject()
    monkeypatch.setattr(nwGUI, "showNewProjectDialog", lambda *args: None)
    assert not nwGUI.newProject()

    # Now, with an empty dictionary
    monkeypatch.setattr(nwGUI, "showNewProjectDialog", lambda *args: {})
    assert not nwGUI.newProject()

    # Now, with a non-empty folder
    monkeypatch.setattr(nwGUI, "showNewProjectDialog", lambda *args: {"projPath": nwMinimal})
    assert not nwGUI.newProject()

    monkeypatch.undo()

    ##
    #  Test the Wizard
    ##

    monkeypatch.setattr(GuiProjectWizard, "exec_", lambda *args: None)
    nwGUI.mainConf.lastPath = " "

    nwGUI.closeProject()
    nwGUI.showNewProjectDialog()
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectWizard") is not None, timeout=1000)

    nwWiz = getGuiItem("GuiProjectWizard")
    assert isinstance(nwWiz, GuiProjectWizard)
    nwWiz.show()
    qtbot.wait(stepDelay)

    for wStep in range(4):
        # This does not actually create the project, it just generates the
        # dictionary that defines it.

        # Intro Page
        introPage = nwWiz.currentPage()
        assert isinstance(introPage, ProjWizardIntroPage)
        assert not nwWiz.button(QWizard.NextButton).isEnabled()

        qtbot.wait(stepDelay)
        for c in ("Test Minimal %d" % wStep):
            qtbot.keyClick(introPage.projName, c, delay=typeDelay)

        qtbot.wait(stepDelay)
        for c in "Minimal Novel":
            qtbot.keyClick(introPage.projTitle, c, delay=typeDelay)

        qtbot.wait(stepDelay)
        for c in "Jane Doe":
            qtbot.keyClick(introPage.projAuthors, c, delay=typeDelay)

        # Setting projName should activate the button
        assert nwWiz.button(QWizard.NextButton).isEnabled()

        qtbot.wait(stepDelay)
        qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

        # Folder Page
        storagePage = nwWiz.currentPage()
        assert isinstance(storagePage, ProjWizardFolderPage)
        assert not nwWiz.button(QWizard.NextButton).isEnabled()

        if wStep == 0:
            # Check invalid path first, the first time we reach here
            monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **kw: "")
            qtbot.wait(stepDelay)
            qtbot.mouseClick(storagePage.browseButton, Qt.LeftButton, delay=100)
            assert storagePage.projPath.text() == ""

            # Then, we always return nwMinimal as path
            monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *a, **kw: nwMinimal)

        qtbot.wait(stepDelay)
        qtbot.mouseClick(storagePage.browseButton, Qt.LeftButton, delay=100)
        projPath = os.path.join(nwMinimal, "Test Minimal %d" % wStep)
        assert storagePage.projPath.text() == projPath

        # Setting projPath should activate the button
        assert nwWiz.button(QWizard.NextButton).isEnabled()

        qtbot.wait(stepDelay)
        qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

        # Populate Page
        popPage = nwWiz.currentPage()
        assert isinstance(popPage, ProjWizardPopulatePage)
        assert nwWiz.button(QWizard.NextButton).isEnabled()

        qtbot.wait(stepDelay)
        if wStep == 0:
            popPage.popMinimal.setChecked(True)
        elif wStep == 1:
            popPage.popCustom.setChecked(True)
        elif wStep == 2:
            popPage.popCustom.setChecked(True)
        elif wStep == 3:
            popPage.popSample.setChecked(True)

        qtbot.wait(stepDelay)
        qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

        # Custom Page
        if wStep == 1 or wStep == 2:
            customPage = nwWiz.currentPage()
            assert isinstance(customPage, ProjWizardCustomPage)
            assert nwWiz.button(QWizard.NextButton).isEnabled()

            customPage.addPlot.setChecked(True)
            customPage.addChar.setChecked(True)
            customPage.addWorld.setChecked(True)
            customPage.addTime.setChecked(True)
            customPage.addObject.setChecked(True)
            customPage.addEntity.setChecked(True)

            if wStep == 2:
                customPage.numChapters.setValue(0)
                customPage.numScenes.setValue(10)
                customPage.chFolders.setChecked(False)

            qtbot.wait(stepDelay)
            qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

        # Final Page
        finalPage = nwWiz.currentPage()
        assert isinstance(finalPage, ProjWizardFinalPage)
        assert nwWiz.button(QWizard.FinishButton).isEnabled() # But we don't click it

        # Check Data
        projData = nwGUI._assembleProjectWizardData(nwWiz)
        assert projData["projName"]    == "Test Minimal %d" % wStep
        assert projData["projTitle"]   == "Minimal Novel"
        assert projData["projAuthors"] == "Jane Doe"
        assert projData["projPath"]    == projPath
        assert projData["popMinimal"]  == (wStep == 0)
        assert projData["popCustom"]   == (wStep == 1 or wStep == 2)
        assert projData["popSample"]   == (wStep == 3)
        if wStep == 1 or wStep == 2:
            assert projData["addRoots"] == [
                nwItemClass.PLOT,
                nwItemClass.CHARACTER,
                nwItemClass.WORLD,
                nwItemClass.TIMELINE,
                nwItemClass.OBJECT,
                nwItemClass.ENTITY,
            ]
            if wStep == 1:
                assert projData["numChapters"] == 5
                assert projData["numScenes"] == 5
                assert projData["chFolders"]
            else:
                assert projData["numChapters"] == 0
                assert projData["numScenes"] == 10
                assert not projData["chFolders"]
        else:
            assert projData["addRoots"] == []
            assert projData["numChapters"] == 0
            assert projData["numScenes"] == 0
            assert not projData["chFolders"]

        # Restart the wizard for next iteration
        nwWiz.restart()

    nwWiz.reject()
    nwWiz.close()

    # qtbot.stopForInteraction()

# END Test testGuiProjectWizard_Main
