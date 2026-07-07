"""
novelWriter – Test Suite Helpers
================================

This file is a part of novelWriter
Copyright (C) 2019 Veronica Berglyd Olsen and novelWriter contributors

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
"""  # noqa

from __future__ import annotations

import difflib
import shutil
import xml.etree.ElementTree as ET

from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget

from novelwriter import logger

XML_IGNORE = ("<novelWriterXML", "<project")
ODT_IGNORE = ("<meta:generator", "<meta:creation-date", "<dc:date", "<meta:editing")
EPUB_IGNORE = ('<meta property="dcterms:date">', '<meta property="dcterms:modified">', "<dc:date>")
NWD_IGNORE = ("%%~date:",)
DOCX_IGNORE = ("<dcterms:created", "<dcterms:modified", "<ns0:Application")
MOCK_TIME = datetime(2019, 5, 10, 18, 52, 0).timestamp()


class C:
    # Import and status items from test project when random generator is mocked
    sNew = "s000000"
    sNote = "s000001"
    sDraft = "s000002"
    sFinished = "s000003"

    iNew = "i000004"
    iMinor = "i000005"
    iMajor = "i000006"
    iMain = "i000007"

    # Handles from test project when random generator is mocked
    hInvalid = "0000000000000"
    hNovelRoot = "0000000000008"
    hPlotRoot = "0000000000009"
    hTrashRoot = "0000000000010"
    hCharRoot = "000000000000a"
    hWorldRoot = "000000000000b"
    hTitlePage = "000000000000c"
    hChapterDir = "000000000000d"
    hChapterDoc = "000000000000e"
    hSceneDoc = "000000000000f"


def cmpFiles(
    fromFile: str | Path,
    toFile: str | Path,
    ignoreLines: list[int] | None = None,
    ignoreStart: tuple | None = None,
) -> bool:
    """Compare two files, with optional line ignore by line number, or
    by matching the start of a line, ignoring leading whitespace.
    """
    ignoreLines = ignoreLines or []

    def loadLines(path: str | Path) -> list[str] | None:
        try:
            with open(path, mode="r", encoding="utf-8") as fo:
                lines = fo.read().strip().splitlines()
        except Exception as exc:
            print(str(exc))
            return None
        result = []
        for n, line in enumerate(lines):
            text = line.strip()
            if n + 1 in ignoreLines or (ignoreStart is not None and text.startswith(ignoreStart)):
                continue
            result.append(text)
        return result

    def colourDiffLine(line: str) -> str:
        """Add bright ANSI colours to a line of a unified diff."""
        if line.startswith(("+++", "---")):
            return f"\033[1m{line}\033[0m"
        elif line.startswith("+"):
            return f"\033[92m{line}\033[0m"
        elif line.startswith("-"):
            return f"\033[91m{line}\033[0m"
        elif line.startswith("@@"):
            return f"\033[96m{line}\033[0m"
        return line

    txtOne = loadLines(fromFile)
    txtTwo = loadLines(toFile)
    if txtOne is None or txtTwo is None:
        return False

    if txtOne == txtTwo:
        return True

    diff = difflib.unified_diff(txtOne, txtTwo, fromfile=str(fromFile), tofile=str(toFile), lineterm="")
    print("\n".join(colourDiffLine(line) for line in diff))

    return False


def xmlToText(xElem):
    """Get the text content of an XML element."""
    text = ET.tostring(xElem, encoding="utf-8", xml_declaration=False).decode()
    bits = text.partition(">")
    node = bits[0].partition(" ")
    rest = " ".join(x for x in node[2].split() if not x.startswith("xmlns")).replace("/", " /")
    return f"{node[0]}{rest}{bits[1]}{bits[2]}"


def readFile(fileName: str | Path):
    """Return the content of a file as a string."""
    with open(fileName, mode="r", encoding="utf-8") as inFile:
        return inFile.read()


def writeFile(fileName: str | Path, fileData: str):
    """Write the contents of a string to a file."""
    with open(fileName, mode="w", encoding="utf-8") as outFile:
        outFile.write(fileData)


def cleanProject(path: str | Path):
    """Delete all generated files in a project."""
    path = Path(path)
    cacheDir = path / "cache"
    if cacheDir.is_dir():
        shutil.rmtree(cacheDir)

    metaDir = path / "meta"
    if metaDir.is_dir():
        shutil.rmtree(metaDir)

    bakFile = path / "nwProject.bak"
    if bakFile.is_file():
        bakFile.unlink()

    tocFile = path / "ToC.txt"
    if tocFile.is_file():
        tocFile.unlink()


def clearLogHandlers():
    """Clear all log handlers."""
    for handler in logger.handlers:
        logger.removeHandler(handler)


def buildTestProject(obj: object, projPath: Path) -> None:
    """Build a standard test project in projPath using the project
    object as the parent.
    """
    from novelwriter.core.project import NWProject
    from novelwriter.enum import nwItemClass
    from novelwriter.guimain import GuiMain

    if isinstance(obj, NWProject):
        nwGUI = None
        project = obj
    elif isinstance(obj, GuiMain):
        from novelwriter import SHARED

        nwGUI = obj
        project = SHARED.project
    else:
        return

    project.storage.createNewProject(projPath)
    project.setDefaultStatusImport()

    project.data.setUuid("d0f3fe10-c6e6-4310-8bfd-181eb4224eed")
    project.data.setName("New Project")
    project.data.setAuthor("Jane Doe")

    # Creating a minimal project with a few root folders and a
    # single chapter folder with a single file.
    nrHandle = project.newRoot(nwItemClass.NOVEL)
    project.newRoot(nwItemClass.PLOT)
    project.newRoot(nwItemClass.CHARACTER)
    project.newRoot(nwItemClass.WORLD)

    tdHandle = project.newFile("Title Page", nrHandle)
    cfHandle = project.newFolder("New Folder", nrHandle) or ""
    cdHandle = project.newFile("New Chapter", cfHandle)
    sdHandle = project.newFile("New Scene", cfHandle)

    aDoc = project.storage.getDocument(tdHandle)
    aDoc.writeDocument("#! New Novel\n\n>> By Jane Doe <<\n")
    project.index.reIndexHandle(tdHandle)

    aDoc = project.storage.getDocument(cdHandle)
    aDoc.writeDocument("## {0}\n\n".format(project.tr("New Chapter")))
    project.index.reIndexHandle(cdHandle)

    aDoc = project.storage.getDocument(sdHandle)
    aDoc.writeDocument("### {0}\n\n".format(project.tr("New Scene")))
    project.index.reIndexHandle(sdHandle)

    project.session.startSession()
    project.setProjectChanged(True)
    project.saveProject(autoSave=True)
    project._valid = True
    project._tree._ready = True

    if nwGUI is not None:
        nwGUI.projView.openProjectTasks()
        nwGUI.novelView.openProjectTasks()

    return


class SimpleDialog(QDialog):
    def __init__(self, widget: QWidget | None = None) -> None:
        super().__init__()
        self._widget = widget
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        self.setLayout(layout)
        if widget:
            layout.addWidget(widget)

    @property
    def widget(self) -> QWidget | None:
        return self._widget

    def addWidget(self, widget: QWidget) -> None:
        self._widget = widget
        layout = self.layout()
        assert layout is not None
        layout.addWidget(widget)
