# -*- coding: utf-8 -*-
"""novelWriter Dialog Class Tester
"""

import nw
import pytest
import os
import sys

from shutil import copyfile
from tools import cmpFiles, getGuiItem

from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtWidgets import (
    QDialogButtonBox, QTreeWidgetItem, QListWidgetItem, QDialog, QAction,
    QFileDialog, QFontDialog
)

from nw.gui import GuiProjectWizard, GuiProjectLoad, GuiPreferences
from nw.gui.custom import QuotesDialog
from nw.constants import nwItemClass

keyDelay = 2
typeDelay = 1
stepDelay = 20

@pytest.mark.gui
def testNewProjectWizard(qtbot, monkeypatch, yesToAll, nwMinimal, tmpDir):

    if sys.platform.startswith("darwin"):
        # Disable for macOS because the test segfaults on QWizard.show()
        return

    from PyQt5.QtWidgets import QWizard
    from nw.gui.projwizard import (
        ProjWizardIntroPage, ProjWizardFolderPage, ProjWizardPopulatePage,
        ProjWizardCustomPage, ProjWizardFinalPage
    )

    nwGUI = nw.main(["--testmode", "--config=%s" % tmpDir, "--data=%s" % tmpDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

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
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testLoadProject(qtbot, monkeypatch, yesToAll, nwMinimal, tmpDir):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % tmpDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    assert nwGUI.openProject(nwMinimal)
    assert nwGUI.closeProject()

    qtbot.wait(stepDelay)
    monkeypatch.setattr(GuiProjectLoad, "exec_", lambda *args: None)
    monkeypatch.setattr(GuiProjectLoad, "result", lambda *args: QDialog.Accepted)
    nwGUI.mainMenu.aOpenProject.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectLoad") is not None, timeout=1000)

    nwLoad = getGuiItem("GuiProjectLoad")
    assert isinstance(nwLoad, GuiProjectLoad)
    nwLoad.show()

    qtbot.wait(stepDelay)
    recentCount = nwLoad.listBox.topLevelItemCount()
    assert recentCount > 0

    qtbot.wait(stepDelay)
    selItem = nwLoad.listBox.topLevelItem(0)
    selPath = selItem.data(nwLoad.C_NAME, Qt.UserRole)
    assert isinstance(selItem, QTreeWidgetItem)

    qtbot.wait(stepDelay)
    nwLoad.selPath.setText("")
    nwLoad.listBox.setCurrentItem(selItem)
    nwLoad._doSelectRecent()
    assert nwLoad.selPath.text() == selPath

    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwLoad.buttonBox.button(QDialogButtonBox.Open), Qt.LeftButton)
    assert nwLoad.openPath == selPath
    assert nwLoad.openState == nwLoad.OPEN_STATE

    # Just create a new project load from scratch for the rest of the test
    del nwLoad

    qtbot.wait(stepDelay)
    nwGUI.mainMenu.aOpenProject.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiProjectLoad") is not None, timeout=1000)

    qtbot.wait(stepDelay)
    nwLoad = getGuiItem("GuiProjectLoad")
    assert isinstance(nwLoad, GuiProjectLoad)
    nwLoad.show()

    qtbot.wait(stepDelay)
    qtbot.mouseClick(nwLoad.buttonBox.button(QDialogButtonBox.Cancel), Qt.LeftButton)
    assert nwLoad.openPath is None
    assert nwLoad.openState == nwLoad.NONE_STATE

    qtbot.wait(stepDelay)
    nwLoad.show()
    qtbot.mouseClick(nwLoad.newButton, Qt.LeftButton)
    assert nwLoad.openPath is None
    assert nwLoad.openState == nwLoad.NEW_STATE

    qtbot.wait(stepDelay)
    nwLoad.show()
    nwLoad._keyPressDelete()
    assert nwLoad.listBox.topLevelItemCount() == recentCount - 1

    getFile = os.path.join(nwMinimal, "nwProject.nwx")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *args, **kwargs: (getFile, None))
    qtbot.mouseClick(nwLoad.browseButton, Qt.LeftButton)
    assert nwLoad.openPath == nwMinimal
    assert nwLoad.openState == nwLoad.OPEN_STATE
    # qtbot.stopForInteraction()

    nwLoad.close()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testPreferences(qtbot, monkeypatch, yesToAll, nwMinimal, tmpDir, refDir, tmpConf):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % tmpDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    assert nwGUI.openProject(nwMinimal)

    monkeypatch.setattr(GuiPreferences, "exec_", lambda *args: None)
    monkeypatch.setattr(GuiPreferences, "result", lambda *args: QDialog.Accepted)
    nwGUI.mainMenu.aPreferences.activate(QAction.Trigger)
    qtbot.waitUntil(lambda: getGuiItem("GuiPreferences") is not None, timeout=1000)

    nwPrefs = getGuiItem("GuiPreferences")
    assert isinstance(nwPrefs, GuiPreferences)
    nwPrefs.show()

    # Override Config
    tmpConf.confPath = nwMinimal
    tmpConf.showGUI = False
    nwGUI.mainConf = tmpConf
    nwPrefs.mainConf = tmpConf
    nwPrefs.tabGeneral.mainConf = tmpConf
    nwPrefs.tabProjects.mainConf = tmpConf
    nwPrefs.tabLayout.mainConf = tmpConf
    nwPrefs.tabEditing.mainConf = tmpConf
    nwPrefs.tabAutoRep.mainConf = tmpConf

    # General Settings
    qtbot.wait(keyDelay)
    tabGeneral = nwPrefs.tabGeneral
    nwPrefs._tabBox.setCurrentWidget(tabGeneral)

    qtbot.wait(keyDelay)
    assert not tabGeneral.preferDarkIcons.isChecked()
    qtbot.mouseClick(tabGeneral.preferDarkIcons, Qt.LeftButton)
    assert tabGeneral.preferDarkIcons.isChecked()

    qtbot.wait(keyDelay)
    assert tabGeneral.showFullPath.isChecked()
    qtbot.mouseClick(tabGeneral.showFullPath, Qt.LeftButton)
    assert not tabGeneral.showFullPath.isChecked()

    qtbot.wait(keyDelay)
    assert not tabGeneral.hideVScroll.isChecked()
    qtbot.mouseClick(tabGeneral.hideVScroll, Qt.LeftButton)
    assert tabGeneral.hideVScroll.isChecked()

    qtbot.wait(keyDelay)
    assert not tabGeneral.hideHScroll.isChecked()
    qtbot.mouseClick(tabGeneral.hideHScroll, Qt.LeftButton)
    assert tabGeneral.hideHScroll.isChecked()

    # Check font button
    monkeypatch.setattr(QFontDialog, "getFont", lambda font, obj: (font, True))
    qtbot.mouseClick(tabGeneral.fontButton, Qt.LeftButton)

    qtbot.wait(keyDelay)
    tabGeneral.guiFontSize.setValue(12)

    # Projects Settings
    qtbot.wait(keyDelay)
    tabProjects = nwPrefs.tabProjects
    nwPrefs._tabBox.setCurrentWidget(tabProjects)
    tabProjects.backupPath = "no/where"

    qtbot.wait(keyDelay)
    assert not tabProjects.backupOnClose.isChecked()
    qtbot.mouseClick(tabProjects.backupOnClose, Qt.LeftButton)
    assert tabProjects.backupOnClose.isChecked()

    # Check Browse button
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args, **kwargs: "")
    assert not tabProjects._backupFolder()
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args, **kwargs: "some/dir")
    qtbot.mouseClick(tabProjects.backupGetPath, Qt.LeftButton)

    qtbot.wait(keyDelay)
    tabProjects.autoSaveDoc.setValue(20)
    tabProjects.autoSaveProj.setValue(40)

    # Text Layout Settings
    qtbot.wait(keyDelay)
    tabLayout = nwPrefs.tabLayout
    nwPrefs._tabBox.setCurrentWidget(tabLayout)

    qtbot.wait(keyDelay)
    qtbot.mouseClick(tabLayout.fontButton, Qt.LeftButton)

    qtbot.wait(keyDelay)
    tabLayout.textStyleSize.setValue(13)
    tabLayout.textFlowMax.setValue(700)
    tabLayout.focusDocWidth.setValue(900)
    tabLayout.textMargin.setValue(45)
    tabLayout.tabWidth.setValue(45)

    qtbot.wait(keyDelay)
    assert not tabLayout.textFlowFixed.isChecked()
    qtbot.mouseClick(tabLayout.textFlowFixed, Qt.LeftButton)
    assert tabLayout.textFlowFixed.isChecked()

    qtbot.wait(keyDelay)
    assert not tabLayout.hideFocusFooter.isChecked()
    qtbot.mouseClick(tabLayout.hideFocusFooter, Qt.LeftButton)
    assert tabLayout.hideFocusFooter.isChecked()

    qtbot.wait(keyDelay)
    assert tabLayout.textJustify.isChecked()
    qtbot.mouseClick(tabLayout.textJustify, Qt.LeftButton)
    assert not tabLayout.textJustify.isChecked()

    qtbot.wait(keyDelay)
    assert tabLayout.scrollPastEnd.isChecked()
    qtbot.mouseClick(tabLayout.scrollPastEnd, Qt.LeftButton)
    assert not tabLayout.scrollPastEnd.isChecked()

    qtbot.wait(keyDelay)
    assert not tabLayout.autoScroll.isChecked()
    qtbot.mouseClick(tabLayout.autoScroll, Qt.LeftButton)
    assert tabLayout.autoScroll.isChecked()

    # Editor Settings
    qtbot.wait(keyDelay)
    tabEditing = nwPrefs.tabEditing
    nwPrefs._tabBox.setCurrentWidget(tabEditing)

    qtbot.wait(keyDelay)
    assert tabEditing.highlightQuotes.isChecked()
    qtbot.mouseClick(tabEditing.highlightQuotes, Qt.LeftButton)
    assert not tabEditing.highlightQuotes.isChecked()

    qtbot.wait(keyDelay)
    assert tabEditing.highlightEmph.isChecked()
    qtbot.mouseClick(tabEditing.highlightEmph, Qt.LeftButton)
    assert not tabEditing.highlightEmph.isChecked()

    qtbot.wait(keyDelay)
    assert not tabEditing.showTabsNSpaces.isChecked()
    qtbot.mouseClick(tabEditing.showTabsNSpaces, Qt.LeftButton)
    assert tabEditing.showTabsNSpaces.isChecked()

    qtbot.wait(keyDelay)
    assert not tabEditing.showLineEndings.isChecked()
    qtbot.mouseClick(tabEditing.showLineEndings, Qt.LeftButton)
    assert tabEditing.showLineEndings.isChecked()

    qtbot.wait(keyDelay)
    tabEditing.bigDocLimit.setValue(500)

    # Auto-Replace Settings
    qtbot.wait(keyDelay)
    tabAutoRep = nwPrefs.tabAutoRep
    nwPrefs._tabBox.setCurrentWidget(tabAutoRep)

    qtbot.wait(keyDelay)
    assert tabAutoRep.autoSelect.isChecked()
    qtbot.mouseClick(tabAutoRep.autoSelect, Qt.LeftButton)
    assert not tabAutoRep.autoSelect.isChecked()

    qtbot.wait(keyDelay)
    assert tabAutoRep.autoReplaceMain.isChecked()
    qtbot.mouseClick(tabAutoRep.autoReplaceMain, Qt.LeftButton)
    assert not tabAutoRep.autoReplaceMain.isChecked()

    qtbot.wait(keyDelay)
    assert not tabAutoRep.autoReplaceSQ.isEnabled()
    assert not tabAutoRep.autoReplaceDQ.isEnabled()
    assert not tabAutoRep.autoReplaceDash.isEnabled()
    assert not tabAutoRep.autoReplaceDots.isEnabled()

    monkeypatch.setattr(QuotesDialog, "selectedQuote", "'")
    monkeypatch.setattr(QuotesDialog, "exec_", lambda *args: QDialog.Accepted)
    qtbot.mouseClick(tabAutoRep.btnDoubleStyleC, Qt.LeftButton)

    # Save and Check Config
    qtbot.mouseClick(nwPrefs.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)

    assert tmpConf.confChanged
    tmpConf.lastPath = ""

    assert nwGUI.mainConf.saveConfig()

    # qtbot.stopForInteraction()
    nwGUI.closeMain()

    refConf = os.path.join(refDir, "novelwriter_prefs.conf")
    projConf = os.path.join(nwGUI.mainConf.confPath, "novelwriter.conf")
    testConf = os.path.join(tmpDir, "novelwriter_prefs.conf")
    copyfile(projConf, testConf)
    ignoreLines = [
        2,                          # Timestamp
        9,                          # Release Notes
        12, 13, 14, 15, 16, 17, 18, # Window sizes
        7, 28,                      # Fonts (depends on system default)
    ]
    assert cmpFiles(testConf, refConf, ignoreLines)

@pytest.mark.gui
def testQuotesDialog(qtbot, yesToAll, nwMinimal, tmpDir):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % tmpDir, nwMinimal])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    nwQuot = QuotesDialog(nwGUI)
    nwQuot.show()

    lastItem = ""
    for i in range(nwQuot.listBox.count()):
        anItem = nwQuot.listBox.item(i)
        assert isinstance(anItem, QListWidgetItem)
        nwQuot.listBox.clearSelection()
        nwQuot.listBox.setCurrentItem(anItem, QItemSelectionModel.Select)
        lastItem = anItem.text()[2]
        assert nwQuot.previewLabel.text() == lastItem

    nwQuot._doAccept()
    assert nwQuot.result() == QDialog.Accepted
    assert nwQuot.selectedQuote == lastItem

    # qtbot.stopForInteraction()
    nwQuot._doReject()
    nwQuot.close()
    nwGUI.closeMain()
    nwGUI.close()

@pytest.mark.gui
def testDialogsOpenClose(qtbot, monkeypatch, yesToAll, nwMinimal, tmpDir):
    nwGUI = nw.main(["--testmode", "--config=%s" % nwMinimal, "--data=%s" % tmpDir, nwMinimal])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(stepDelay)

    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args, **kwargs: tmpDir)
    assert nwGUI.selectProjectPath() == tmpDir

    # qtbot.stopForInteraction()
    nwGUI.closeMain()
    nwGUI.close()
