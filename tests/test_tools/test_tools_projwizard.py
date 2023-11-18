"""
novelWriter – New Project Wizard Class Tester
=============================================

This file is a part of novelWriter
Copyright 2018–2023, Veronica Berglyd Olsen

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

import sys
import pytest

from tools import buildTestProject, getGuiItem

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QWizard, QDialog

from novelwriter.enum import nwItemClass
from novelwriter.tools.projwizard import (
    GuiProjectWizard, ProjWizardIntroPage, ProjWizardFolderPage,
    ProjWizardPopulatePage, ProjWizardCustomPage, ProjWizardFinalPage
)


@pytest.mark.gui
@pytest.mark.skipif(sys.platform.startswith("darwin"), reason="Not running on Darwin")
def testToolProjectWizard_Handling(qtbot, monkeypatch, nwGUI, projPath):
    """Test the launch of the project wizard.
    Disabled for macOS because the test segfaults on QWizard.show()
    """
    # Test New Project Function
    # ========================

    # New with a project open should cause an error
    buildTestProject(nwGUI, projPath)
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI, "closeProject", lambda *a: False)
        assert nwGUI.newProject() is False

    # Close project, but call with invalid path
    assert nwGUI.closeProject()
    with monkeypatch.context() as mp:
        mp.setattr(nwGUI, "showNewProjectDialog", lambda *a: None)
        assert nwGUI.newProject() is False

        # Now, with an empty dictionary
        mp.setattr(nwGUI, "showNewProjectDialog", lambda *a: {})
        assert nwGUI.newProject() is False

        # Now, with a non-empty folder
        mp.setattr(nwGUI, "showNewProjectDialog", lambda *a: {"projPath": projPath})
        assert nwGUI.newProject() is False

    # Test the Wizard Launching
    # =========================

    monkeypatch.setattr(GuiProjectWizard, "exec_", lambda *a: None)

    result = nwGUI.showNewProjectDialog()
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectWizard") is not None, timeout=1000)

    nwWiz = getGuiItem("GuiProjectWizard")
    assert isinstance(nwWiz, GuiProjectWizard)
    nwWiz.show()

    qtbot.mouseClick(nwWiz.button(QWizard.CancelButton), Qt.LeftButton)
    assert result is None

    with monkeypatch.context() as mp:
        mp.setattr(GuiProjectWizard, "result", lambda *a: QDialog.Accepted)
        result = nwGUI.showNewProjectDialog()
        nwWiz.button(QWizard.CancelButton).click()
        assert isinstance(result, dict)

    nwWiz.reject()
    nwWiz.close()

    # qtbot.stop()

# END Test testToolProjectWizard_Handling


@pytest.mark.gui
@pytest.mark.parametrize("prjType", ["minimal", "custom1", "custom2", "sample"])
@pytest.mark.skipif(sys.platform.startswith("darwin"), reason="Not running on Darwin")
def testToolProjectWizard_Run(qtbot, monkeypatch, nwGUI, fncPath, prjType):
    """Test the new project wizard with a set of selection scenarios.
    """
    monkeypatch.setattr(GuiProjectWizard, "exec_", lambda *a: None)

    nwWiz = GuiProjectWizard(nwGUI)
    nwWiz.show()
    qtbot.addWidget(nwWiz)

    # Intro Page
    # ==========

    introPage = nwWiz.currentPage()
    assert isinstance(introPage, ProjWizardIntroPage)
    assert not nwWiz.button(QWizard.NextButton).isEnabled()

    introPage.projName.setText("Test Wizard")
    introPage.projTitle.setText("My Novel")
    introPage.projAuthor.setText("Jane Doe")

    # Setting projName should activate the button
    assert nwWiz.button(QWizard.NextButton).isEnabled()

    qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

    # Folder Page
    # ===========

    storagePage = nwWiz.currentPage()
    assert isinstance(storagePage, ProjWizardFolderPage)
    assert storagePage.errLabel.text() == ""

    # Set an invalid path
    storagePage.projPath.setText(str(fncPath / "not" / "a" / "path"))
    assert not nwWiz.button(QWizard.NextButton).isEnabled()
    assert storagePage.errLabel.text().startswith("Error")

    # Set an existing path
    storagePage.projPath.setText(str(fncPath))
    assert not nwWiz.button(QWizard.NextButton).isEnabled()
    assert storagePage.errLabel.text().startswith("Error")

    # Return a non-result from browse
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: "")
        qtbot.mouseClick(storagePage.browseButton, Qt.LeftButton, delay=100)
        assert storagePage.errLabel.text() == ""

    # Let the browse feature handle it
    projPath = fncPath / "Test Wizard"
    with monkeypatch.context() as mp:
        mp.setattr(QFileDialog, "getExistingDirectory", lambda *a, **k: str(fncPath))
        qtbot.mouseClick(storagePage.browseButton, Qt.LeftButton, delay=100)

    assert storagePage.projPath.text() == str(projPath)
    assert storagePage.errLabel.text() == ""

    # Setting projPath should activate the button
    assert nwWiz.button(QWizard.NextButton).isEnabled()

    qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

    # Populate Page
    # =============

    popPage = nwWiz.currentPage()
    assert isinstance(popPage, ProjWizardPopulatePage)
    assert nwWiz.button(QWizard.NextButton).isEnabled()

    if prjType.startswith("minimal"):
        popPage.popMinimal.setChecked(True)
    elif prjType.startswith("custom"):
        popPage.popCustom.setChecked(True)
    elif prjType.startswith("sample"):
        popPage.popSample.setChecked(True)

    qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

    # Custom Page
    # ===========
    if prjType.startswith("custom"):

        customPage = nwWiz.currentPage()
        assert isinstance(customPage, ProjWizardCustomPage)
        assert nwWiz.button(QWizard.NextButton).isEnabled()

        # Make sure the fourth option is also turned off
        customPage.addPlot.setChecked(False)
        customPage.addChar.setChecked(False)
        customPage.addWorld.setChecked(False)
        customPage._syncSwitches()
        assert not customPage.addNotes.isChecked()

        # Switch everything back on again
        customPage.addPlot.setChecked(True)
        customPage.addChar.setChecked(True)
        customPage.addWorld.setChecked(True)
        customPage.addNotes.setChecked(True)

        if prjType == "custom2":
            customPage.numChapters.setValue(0)
            customPage.numScenes.setValue(10)

        qtbot.mouseClick(nwWiz.button(QWizard.NextButton), Qt.LeftButton)

    # Final Page
    # ==========

    finalPage = nwWiz.currentPage()
    assert isinstance(finalPage, ProjWizardFinalPage)
    assert nwWiz.button(QWizard.FinishButton).isEnabled()  # But we don't click it

    # Check Data
    # ==========

    projData = nwGUI._assembleProjectWizardData(nwWiz)
    assert projData["projName"] == "Test Wizard"
    assert projData["projTitle"] == "My Novel"
    assert projData["projAuthor"] == "Jane Doe"
    assert projData["projPath"] == str(projPath)
    assert projData["popMinimal"] == prjType.startswith("minimal")
    assert projData["popCustom"] == prjType.startswith("custom")
    assert projData["popSample"] == prjType.startswith("sample")
    if prjType.startswith("custom"):
        assert projData["addRoots"] == [
            nwItemClass.PLOT,
            nwItemClass.CHARACTER,
            nwItemClass.WORLD,
        ]
        if prjType == "custom1":
            assert projData["numChapters"] == 5
            assert projData["numScenes"] == 5
            assert projData["addNotes"] is True
        else:
            assert projData["numChapters"] == 0
            assert projData["numScenes"] == 10
            assert projData["addNotes"] is True
    else:
        assert projData["addRoots"] == []
        assert projData["numChapters"] == 0
        assert projData["numScenes"] == 0
        assert projData["addNotes"] is False

    # Cleanup
    nwWiz.reject()
    nwWiz.close()

    # qtbot.stop()

# END Test testToolProjectWizard_Run
