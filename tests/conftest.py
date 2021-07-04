"""
novelWriter – Test Suite Configuration
======================================

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

import sys
import pytest
import shutil
import os

from mock import MockGuiMain
from tools import cleanProject

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import nw  # noqa: E402

from nw.config import Config  # noqa: E402


##
#  Core Test Folders
##

@pytest.fixture(scope="session")
def tmpDir():
    """A temporary folder for the test session. This folder is
    presistent after the test so that the status of generated files can
    be checked. The folder is instead cleared before a new test session.
    """
    testDir = os.path.dirname(__file__)
    theDir = os.path.join(testDir, "temp")
    if os.path.isdir(theDir):
        shutil.rmtree(theDir)
    if not os.path.isdir(theDir):
        os.mkdir(theDir)
    return theDir


@pytest.fixture(scope="session")
def refDir():
    """The folder where all the reference files are stored for verifying
    the results of tests.
    """
    testDir = os.path.dirname(__file__)
    theDir = os.path.join(testDir, "reference")
    return theDir


@pytest.fixture(scope="session")
def filesDir():
    """The folder where additional test files are stored.
    """
    testDir = os.path.dirname(__file__)
    theDir = os.path.join(testDir, "files")
    return theDir


@pytest.fixture(scope="session")
def outDir(tmpDir):
    """An output folder for test results
    """
    theDir = os.path.join(tmpDir, "results")
    if not os.path.isdir(theDir):
        os.mkdir(theDir)
    return theDir


@pytest.fixture(scope="function")
def fncDir(tmpDir):
    """A temporary folder for a single test function.
    """
    fncDir = os.path.join(tmpDir, "f_temp")
    if os.path.isdir(fncDir):
        shutil.rmtree(fncDir)
    if not os.path.isdir(fncDir):
        os.mkdir(fncDir)
    yield fncDir
    if os.path.isdir(fncDir):
        shutil.rmtree(fncDir)
    return


@pytest.fixture(scope="function")
def fncProj(fncDir):
    """A temporary folder for a single test function,
    with a project folder.
    """
    prjDir = os.path.join(fncDir, "project")
    if os.path.isdir(prjDir):
        shutil.rmtree(prjDir)
    if not os.path.isdir(prjDir):
        os.mkdir(prjDir)
    return prjDir


##
#  novelWriter Objects
##

@pytest.fixture(scope="function")
def tmpConf(tmpDir):
    """Create a temporary novelWriter configuration object.
    """
    confFile = os.path.join(tmpDir, "novelwriter.conf")
    if os.path.isfile(confFile):
        os.unlink(confFile)
    theConf = Config()
    theConf.initConfig(tmpDir, tmpDir)
    theConf.setLastPath("")
    theConf.guiLang = "en_GB"
    return theConf


@pytest.fixture(scope="function")
def fncConf(fncDir):
    """Create a temporary novelWriter configuration object.
    """
    confFile = os.path.join(fncDir, "novelwriter.conf")
    if os.path.isfile(confFile):
        os.unlink(confFile)
    theConf = Config()
    theConf.initConfig(fncDir, fncDir)
    theConf.setLastPath("")
    theConf.guiLang = "en_GB"
    return theConf


@pytest.fixture(scope="function")
def mockGUI(monkeypatch, tmpConf):
    """Create a mock instance of novelWriter's main GUI class.
    """
    monkeypatch.setattr("nw.CONFIG", tmpConf)
    theGui = MockGuiMain()
    theGui.mainConf = tmpConf
    return theGui


@pytest.fixture(scope="function")
def nwGUI(qtbot, monkeypatch, fncDir, fncConf):
    """Create an instance of the novelWriter GUI.
    """
    monkeypatch.setattr("nw.CONFIG", fncConf)
    nwGUI = nw.main(["--testmode", "--config=%s" % fncDir, "--data=%s" % fncDir])
    qtbot.addWidget(nwGUI)
    nwGUI.show()
    qtbot.waitForWindowShown(nwGUI)
    qtbot.wait(20)

    nwGUI.mainConf.lastPath = fncDir

    yield nwGUI

    qtbot.wait(20)
    nwGUI.closeMain()
    qtbot.wait(20)

    return


##
#  Temp Project Folders
##

@pytest.fixture(scope="function")
def nwMinimal(tmpDir):
    """A minimal novelWriter example project.
    """
    tstDir = os.path.dirname(__file__)
    srcDir = os.path.join(tstDir, "minimal")
    dstDir = os.path.join(tmpDir, "minimal")
    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    shutil.copytree(srcDir, dstDir)
    cleanProject(dstDir)

    yield dstDir

    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    return


@pytest.fixture(scope="function")
def nwLipsum(tmpDir):
    """A medium sized novelWriter example project with a lot of Lorem
    Ipsum text.
    """
    tstDir = os.path.dirname(__file__)
    srcDir = os.path.join(tstDir, "lipsum")
    dstDir = os.path.join(tmpDir, "lipsum")
    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    shutil.copytree(srcDir, dstDir)
    cleanProject(dstDir)

    yield dstDir

    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    return


@pytest.fixture(scope="function")
def nwOldProj(tmpDir):
    """A minimal movelWriter project using the old folder structure used
    for storage versions < 1.2.
    """
    tstDir = os.path.dirname(__file__)
    srcDir = os.path.join(tstDir, "oldproj")
    dstDir = os.path.join(tmpDir, "oldproj")
    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    shutil.copytree(srcDir, dstDir)

    yield dstDir

    if os.path.isdir(dstDir):
        shutil.rmtree(dstDir)

    return


##
#  Useful Fixtures
##

@pytest.fixture(scope="session")
def ipsumText():
    """Return five paragraphs of Lorem Ipsum text.
    """
    thatIpsum = [(
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc maximus justo non dictum co"
        "mmodo. Curabitur lacinia tempor orci vel luctus. Phasellus porta metus eu massa luctus, e"
        "get euismod risus rhoncus. Vestibulum sed arcu nisi. Maecenas pretium facilisis velit, ve"
        "l semper lacus aliquam sit amet. Vestibulum vulputate neque ligula, rhoncus blandit turpi"
        "s consequat id. Mauris sagittis vehicula imperdiet. Duis sed nunc pretium, ornare purus v"
        "el, sodales augue. Maecenas a suscipit risus. Quisque volutpat justo eleifend est ullamco"
        "rper fermentum. Donec ullamcorper et tortor a laoreet. Nam id risus nisi. Vivamus non imp"
        "erdiet erat, sit amet imperdiet felis. Mauris vitae neque et est aliquam scelerisque non "
        "non ipsum."
    ), (
        "Nullam laoreet lorem nec malesuada vehicula. Vivamus tempus sodales lectus sed viverra. A"
        "enean lacinia sollicitudin quam, quis tempus eros suscipit id. Duis sed rutrum nisi, ut p"
        "ulvinar magna. Nam et cursus tortor. Phasellus ac odio tellus. Nullam in iaculis ipsum. V"
        "ivamus ante sem, ultricies sed varius quis, tristique nec tellus. Nullam eu urna vitae la"
        "cus hendrerit gravida. Quisque pulvinar erat ex, id efficitur velit sodales vitae. Proin "
        "vestibulum, sapien eget mattis euismod, tortor quam viverra risus, at congue mauris torto"
        "r eu nunc. Mauris pellentesque elit leo, quis eleifend sem placerat a. Vivamus iaculis du"
        "i eget tellus volutpat, ac varius nisi facilisis."
    ), (
        "Nullam a nisl magna. Praesent commodo nec diam aliquet vestibulum. In sapien velit, sodal"
        "es feugiat porta ut, rhoncus a elit. Quisque egestas nisi eu eros laoreet, quis facilisis"
        " est pretium. Nullam bibendum sed tellus nec lobortis. Duis elit massa, volutpat a lacini"
        "a a, ullamcorper in dui. Suspendisse ac laoreet dui. Curabitur elementum, tortor elementu"
        "m ultricies laoreet, nunc massa vulputate augue, vitae tincidunt nunc enim eget nisl."
    ), (
        "Pellentesque nibh urna, volutpat et feugiat porta, rutrum sed lectus. Aliquam eget risus "
        "id orci tincidunt condimentum et sit amet purus. Curabitur tincidunt odio vel ante feugia"
        "t feugiat. Proin nunc lorem, molestie a sapien et, varius elementum nunc. Donec non ferme"
        "ntum nisl. In et massa placerat, faucibus felis eu, congue nisi. Proin sed tortor non lor"
        "em mattis cursus. Vestibulum magna neque, bibendum vel nibh et, tincidunt rhoncus nisi. D"
        "uis pulvinar mi a quam rutrum maximus. Nunc sollicitudin, urna in cursus facilisis, augue"
        " neque imperdiet metus, ac finibus lorem ante id nulla. Sed maximus eleifend justo id feu"
        "giat. Cras eget diam vel est blandit tempor nec a leo. Mauris risus est, fringilla in ali"
        "quam a, sagittis vel enim. Nullam sodales id erat placerat lobortis."
    ), (
        "Integer ac gravida quam. Quisque eleifend nisl nec pretium tincidunt. Quisque sollicitudi"
        "n nisi in hendrerit scelerisque. Sed ornare nisl lacus, sit amet consectetur lectus egest"
        "as et. Vivamus nec arcu lorem. Donec rhoncus, purus a porta accumsan, nunc lectus iaculis"
        " libero, et fringilla tellus augue et velit. Integer varius felis scelerisque, vulputate "
        "tellus eu, laoreet justo. Suspendisse sit amet sem vehicula, auctor odio sed, aliquet eni"
        "m. In ac tortor sed tortor fringilla elementum. Nulla non odio at magna vulputate sceleri"
        "sque. Nam elementum diam eu rutrum scelerisque. Sed fermentum, felis quis vulputate ferme"
        "ntum, libero metus sollicitudin est, in faucibus purus nulla non dolor. Ut vitae felis po"
        "rta, feugiat nunc et, bibendum neque. Nullam nec lorem nec metus ullamcorper malesuada ut"
        " a nisl. Etiam eget tristique dui. Nulla sed mi finibus, venenatis tellus non, maximus en"
        "im."
    )]
    return thatIpsum
