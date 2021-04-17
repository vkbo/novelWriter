#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
novelWriter – Main Setup Script
===============================
The main setup and install script for all operating systems

File History:
Created: 2019-05-16 [0.5.1]

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

import os
import sys
import shutil
import subprocess

OS_NONE   = 0
OS_LINUX  = 1
OS_WIN    = 2
OS_DARWIN = 3

# =============================================================================================== #
#  Utilities
# =============================================================================================== #

def extractVersion():
    """Extract the novelWriter version number without having to import
    anything else from the main package.
    """
    def getValue(theString):
        theBits = theString.partition("=")
        return theBits[2].strip().strip('"')

    numVers = "Unknown"
    hexVers = "Unknown"
    initFile = os.path.join("nw", "__init__.py")
    with open(initFile, mode="r") as inFile:
        for aLine in inFile:
            if aLine.startswith("__version__"):
                numVers = getValue((aLine))
            if aLine.startswith("__hexversion__"):
                hexVers = getValue((aLine))

    return numVers, hexVers

# =============================================================================================== #
#  General
# =============================================================================================== #

##
# Package Installer (pip)
##

def installPackages(hostOS):
    """Install package dependencies both for this script and for running
    novelWriter itself.
    """
    print("")
    print("Installing Dependencies")
    print("=======================")
    print("")

    installQueue = ["pip", "-r requirements.txt"]
    if hostOS == OS_DARWIN:
        installQueue.append("pyobjc")
    elif hostOS == OS_WIN:
        installQueue.append("pywin32")

    pyCmd = [sys.executable, "-m"]
    pipCmd = ["pip", "install", "--user", "--upgrade"]
    for stepCmd in installQueue:
        pkgCmd = stepCmd.split(" ")
        try:
            subprocess.call(pyCmd + pipCmd + pkgCmd)
        except Exception as e:
            print("Failed with error:")
            print(str(e))
            sys.exit(1)

    return

##
#  Clean Build and Dist Folders (clean)
##

def cleanInstall():
    """Recursively delete the 'build' and 'dist' folders.
    """
    print("")
    print("Cleaning up build environment ...")

    buildDir = os.path.join(os.getcwd(), "build")
    if os.path.isdir(buildDir):
        try:
            shutil.rmtree(buildDir)
            print("Deleted folder 'build'")
        except Exception as e:
            print("Error: Cannot delete 'build' folder.")
            print(str(e))
            sys.exit(1)
    else:
        print("Folder 'build' not found")

    distDir = os.path.join(os.getcwd(), "dist")
    if os.path.isdir(distDir):
        try:
            shutil.rmtree(distDir)
            print("Deleted folder 'dist'")
        except Exception as e:
            print("Error: Cannot delete 'dist' folder.")
            print(str(e))
            sys.exit(1)
    else:
        print("Folder 'dist' not found")

    print("")

    return

# =============================================================================================== #
#  Additional Buiilds
# =============================================================================================== #

##
#  Qt Assistant Documentation Builder (qthelp)
##

def buildQtDocs():
    """This function will build the documentation as a Qt help file. The
    file is then copied into the nw/assets/help directory and can be
    included in builds.
    """
    buildDir = os.path.join("docs", "build", "qthelp")
    helpDir  = os.path.join("nw", "assets", "help")

    inFile  = "novelWriter.qhcp"
    outFile = "novelWriter.qhc"
    datFile = "novelWriter.qch"

    print("")
    print("Building Documentation")
    print("======================")
    print("")

    buildFail = False
    try:
        subprocess.call(["make", "-C", "docs", "qthelp"])
    except Exception as e:
        print("QtHelp Build Error:")
        print(str(e))
        buildFail = True

    try:
        subprocess.call(["qhelpgenerator", os.path.join(buildDir, inFile)])
    except Exception as e:
        print("QtHelp Build Error:")
        print(str(e))
        buildFail = True

    if not os.path.isdir(helpDir):
        try:
            os.mkdir(helpDir)
        except Exception as e:
            print("QtHelp Build Error:")
            print(str(e))
            buildFail = True

    try:
        if os.path.isfile(os.path.join(helpDir, outFile)):
            os.unlink(os.path.join(helpDir, outFile))
        if os.path.isfile(os.path.join(helpDir, datFile)):
            os.unlink(os.path.join(helpDir, datFile))
        os.rename(os.path.join(buildDir, outFile), os.path.join(helpDir, outFile))
        os.rename(os.path.join(buildDir, datFile), os.path.join(helpDir, datFile))
    except Exception as e:
        print("QtHelp Build Error:")
        print(str(e))
        buildFail = True

    print("")
    if buildFail:
        print("Documentation build: FAILED")
        print("")
        print("Dependencies:")
        print(" * pip install sphinx")
        print(" * pip install sphinx-rtd-theme")
        print(" * pip install sphinxcontrib-qthelp")
        print("")
        print("It also requires the qhelpgenerator to be available on the system.")
        sys.exit(1)
    else:
        print("Documentation build: OK")
    print("")

    return

##
#  Sample Project ZIP File Builder (sample)
##

def buildSampleZip():
    """Bundle the sample project into a single zip file to be saved into
    the nw/assets folder for further bundling into builds.
    """
    print("")
    print("Building Sample ZIP File")
    print("========================")
    print("")

    srcSample = "sample"
    dstSample = os.path.join("nw", "assets", "sample.zip")

    if os.path.isdir(srcSample):
        if os.path.isfile(dstSample):
            os.unlink(dstSample)

        from zipfile import ZipFile

        with ZipFile(dstSample, "w") as zipObj:
            print("Compressing: nwProject.nwx")
            zipObj.write(os.path.join(srcSample, "nwProject.nwx"), "nwProject.nwx")
            for docFile in os.listdir(os.path.join(srcSample, "content")):
                print("Compressing: content/%s" % docFile)
                srcDoc = os.path.join(srcSample, "content", docFile)
                zipObj.write(srcDoc, "content/"+docFile)

    else:
        print("Error: Could not find sample project source directory.")
        sys.exit(1)

    print("")
    print("Built file: %s" % dstSample)
    print("")

    return

# =============================================================================================== #
#  Python Packaging
# =============================================================================================== #

##
#  Make Minimal Package (minimal-zip)
##

def makeMinimalPackage(targetOS):
    """Pack the core source file in a single zip file.
    """
    from zipfile import ZipFile, ZIP_DEFLATED

    # Get the version
    numVers, _ = extractVersion()

    # Make sample.zip first
    try:
        buildSampleZip()
    except Exception as e:
        print("Failed with error:")
        print(str(e))
        sys.exit(1)

    print("")
    print("Building Minimal ZIP File")
    print("=========================")

    if not os.path.isdir("dist"):
        os.mkdir("dist")

    if targetOS == OS_LINUX:
        targName = "-linux"
        print("Target OS: Linux")
    elif targetOS == OS_DARWIN:
        targName = "-darwin"
        print("Target OS: Darwin")
    elif targetOS == OS_WIN:
        targName = "-win"
        print("Target OS: Windows")
    else:
        targName = ""
    print("")

    zipFile = f"novelWriter-{numVers}-minimal{targName}.zip"
    outFile = os.path.join("dist", zipFile)
    if os.path.isfile(outFile):
        os.unlink(outFile)

    rootFiles = ["LICENSE.md", "README.md", "CHANGELOG.md", "requirements.txt", "setup.py"]

    with ZipFile(outFile, "w", compression=ZIP_DEFLATED, compresslevel=9) as zipObj:

        if targetOS != OS_WIN:
            for nRoot, _, nFiles in os.walk("setup"):
                print("Adding Folder: %s [%d files]" % (nRoot, len(nFiles)))
                for aFile in nFiles:
                    zipObj.write(os.path.join(nRoot, aFile))

        for nRoot, _, nFiles in os.walk("nw"):
            if nRoot.endswith("__pycache__"):
                print("Skipping Folder: %s" % nRoot)
                continue

            print("Adding Folder: %s [%d files]" % (nRoot, len(nFiles)))
            for aFile in nFiles:
                if aFile.endswith(".pyc"):
                    print("Skipping File: %s" % aFile)
                    continue
                zipObj.write(os.path.join(nRoot, aFile))

        if targetOS == OS_WIN:
            zipObj.write("novelWriter.py", "novelWriter.pyw")
            print("Adding File: novelWriter.pyw")
            zipObj.write(os.path.join("setup", "setup_windows.bat"), "setup_windows.bat")
            print("Adding File: setup_windows.bat")
            zipObj.write(os.path.join("setup", "uninstall_windows.bat"), "uninstall_windows.bat")
            print("Adding File: uninstall_windows.bat")
        else:
            zipObj.write("novelWriter.py")
            print("Adding File: novelWriter.py")

        for aFile in rootFiles:
            assert os.path.isfile(aFile)
            print("Adding File: %s" % aFile)
            zipObj.write(aFile)

    print("")
    print("Created File: %s" % outFile)

    try:
        shaFile = open(outFile+".sha256", mode="w")
        subprocess.call(["sha256sum", zipFile], stdout=shaFile, cwd="dist")
        shaFile.close()
        print("SHA256 Sum:   %s" % (outFile+".sha256"))
    except Exception as e:
        print("Could not generate sha256 file")
        print(str(e))

    print("")

    return

##
#  Make Simple Package (pack-pyz)
##

def makeSimplePackage(embedPython):
    """Run zipapp to freeze the packages. This assumes zipapp and pip
    are already installed.
    """
    import urllib.request
    import zipfile
    import zipapp

    # Set Up Folder
    # =============

    if not os.path.isdir("dist"):
        os.mkdir("dist")

    outDir = os.path.join("dist", "novelWriter")
    zipDir = os.path.join("dist", "zipapp_temp")
    libDir = os.path.join(outDir, "lib")
    if os.path.isdir(zipDir):
        shutil.rmtree(zipDir)
    if os.path.isdir(outDir):
        shutil.rmtree(outDir)

    os.mkdir(outDir)
    os.mkdir(libDir)

    # Download Python Embeddable
    # ==========================

    if embedPython:
        print("")
        print("# Adding Python Embeddable")
        print("# ========================")
        print("")

        pyVers = "%d.%d.%d" % (sys.version_info[:3])
        zipFile = "python-%s-embed-amd64.zip" % pyVers
        pyZip = os.path.join("dist", zipFile)
        if not os.path.isfile(pyZip):
            pyUrl = f"https://www.python.org/ftp/python/{pyVers}/{zipFile}"
            print("Downloading: %s" % pyUrl)
            urllib.request.urlretrieve(pyUrl, pyZip)

        print("Extracting ...")
        with zipfile.ZipFile(pyZip, "r") as inFile:
            inFile.extractall(outDir)

        print("Done")
        print("")

    # Make sample.zip
    # ===============

    try:
        buildSampleZip()
    except Exception as e:
        print("Failed with error:")
        print(str(e))
        sys.exit(1)

    # Copy Package Files
    # ==================

    print("")
    print("# Copying Package Files")
    print("# =====================")
    print("")

    copyList = ["CHANGELOG.md", "LICENSE.md", "requirements.txt"]
    iconList = ["novelwriter.ico", "x-novelwriter-project.ico"]
    cpIgnore = shutil.ignore_patterns("__pycache__")

    print("Copying: nw")
    shutil.copytree("nw", os.path.join(zipDir, "nw"), ignore=cpIgnore)
    for copyFile in copyList:
        print("Copying: %s" % copyFile)
        shutil.copy2(copyFile, os.path.join(outDir, copyFile))
    for iconFile in iconList:
        print("Copying: %s" % iconFile)
        shutil.copy2(os.path.join("setup", "icons", iconFile), os.path.join(outDir, iconFile))

    # Move assets to outDir as it should not be packed with the rest
    print("Copying: assets")
    os.rename(os.path.join(zipDir, "nw", "assets"), os.path.join(outDir, "assets"))

    print("Writing: __main__.py")
    with open(os.path.join(zipDir, "__main__.py"), mode="w") as outFile:
        outFile.write(
            "#!/usr/bin/env python3\n"
            "\n"
            "import os\n"
            "import sys\n"
            "\n"
            "sys.path.insert(\n"
            "    0, os.path.abspath(\n"
            "        os.path.join(os.path.dirname(__file__), os.path.pardir, \"lib\")\n"
            "    )\n"
            ")\n\n"
            "if __name__ == \"__main__\":\n"
            "    import nw\n"
            "    nw.main()\n"
        )
    print("")

    pyzFile = os.path.join(outDir, "novelWriter.pyz")
    zipapp.create_archive(zipDir, target=pyzFile, interpreter="/usr/bin/env python3")

    # Install Dependencies
    # ====================

    print("")
    print("# Installing Dependencies")
    print("# =======================")
    print("")

    sysCmd  = [sys.executable]
    sysCmd += "-m pip install -r requirements.txt --target".split()
    sysCmd += [libDir]
    try:
        subprocess.call(sysCmd)
    except Exception as e:
        print("Failed with error:")
        print(str(e))
        sys.exit(1)

    for subDir in os.listdir(libDir):
        chkDir = os.path.join(libDir, subDir)
        if os.path.isdir(chkDir) and chkDir.endswith(".dist-info"):
            shutil.rmtree(chkDir)

    print("")

    # Remove Unneeded Library Files
    # =============================

    delQtLibs = [
        "opengl32sw.dll",
        "Qt5DBus.dll",
        "Qt5Designer.dll",
        "Qt5Network.dll",
        "Qt5OpenGL.dll",
        "Qt5Qml.dll",
        "Qt5QmlModels.dll",
        "Qt5QmlWorkerScript.dll",
        "Qt5Quick.dll",
        "Qt5Quick3D.dll",
        "Qt5Quick3DAssetImport.dll",
        "Qt5Quick3DRender.dll",
        "Qt5Quick3DRuntimeRender.dll",
        "Qt5Quick3DUtils.dll",
        "Qt5QuickControls2.dll",
        "Qt5QuickParticles.dll",
        "Qt5QuickShapes.dll",
        "Qt5QuickTemplates2.dll",
        "Qt5QuickTest.dll",
        "Qt5QuickWidgets.dll",
        "Qt5Sql.dll",
    ]
    qtLibDir = os.path.join(libDir, "PyQt5", "Qt", "bin")
    for libName in delQtLibs:
        delFile = os.path.join(qtLibDir, libName)
        if os.path.isfile(delFile):
            print("Deleting: %s" % delFile)
            os.unlink(delFile)

    qmlDir = os.path.join(libDir, "PyQt5", "Qt", "qml")
    if os.path.isdir(qmlDir):
        shutil.rmtree(qmlDir)

    print("")
    print("Done!")
    print("")

    return

# =============================================================================================== #
#  General Installers
# =============================================================================================== #

##
#  XDG Installation (xdg-install)
##

def xdgInstall():
    """Will attempt to install icons and make a launcher.
    """
    print("")
    print("XDG Install")
    print("===========")
    print("")

    # Find Executable(s)
    # ==================

    exOpts = []

    testExec = shutil.which("novelWriter")
    if testExec is not None:
        exOpts.append(testExec)

    testExec = shutil.which("novelwriter")
    if testExec is not None:
        exOpts.append(testExec)

    testExec = os.path.join(os.getcwd(), "novelWriter.py")
    if os.path.isfile(testExec):
        exOpts.append(testExec)

    useExec = ""
    nOpts = len(exOpts)
    if nOpts == 0:
        print("Error: No executables for novelWriter found.")
        sys.exit(1)
    elif nOpts == 1:
        useExec = exOpts[0]
    else:
        print("Found multiple novelWriter executables:")
        print("")
        for iExec, anExec in enumerate(exOpts):
            print(" [%d] %s" % (iExec, anExec))
        print("")
        intVal = int(input("Please select which novelWriter executable to use: "))
        print("")

        if intVal >= 0 and intVal < nOpts:
            useExec = exOpts[intVal]
        else:
            print("Error: Invalid selection.")
            sys.exit(1)

    print("Using executable: %s " % useExec)
    print("")

    # Create and Install Launcher
    # ===========================

    desktopData = ""
    with open("./setup/novelwriter.desktop", mode="r") as inFile:
        desktopData = inFile.read()

    desktopData = desktopData.replace(r"%%exec%%", useExec)
    with open("./novelwriter.desktop", mode="w+") as outFile:
        outFile.write(desktopData)

    exCode = subprocess.call(
        ["xdg-desktop-menu", "install", "--novendor", "./novelwriter.desktop"]
    )
    if exCode == 0:
        print("Installed menu desktop file")
    else:
        print(f"Error {exCode}: Could not install menu desktop file")

    print("")

    # Install MimeType
    # ================

    exCode = subprocess.call([
        "xdg-mime", "install",
        "./setup/mime/x-novelwriter-project.xml"
    ])
    if exCode == 0:
        print("Installed mimetype")
    else:
        print(f"Error {exCode}: Could not install mimetype")

    print("")

    # Install Icons
    # =============

    sizeArr = ["16", "22", "24", "32", "48", "64", "96", "128", "256", "512"]

    # App Icon
    for aSize in sizeArr:
        exCode = subprocess.call([
            "xdg-icon-resource", "install",
            "--novendor", "--noupdate",
            "--context", "apps",
            "--size", aSize,
            f"./setup/icons/scaled/icon-novelwriter-{aSize}.png",
            "novelwriter"
        ])
        if exCode == 0:
            print(f"Installed app icon size {aSize}")
        else:
            print(f"Error {exCode}: Could not install app icon size {aSize}")

    # Mimetype
    for aSize in sizeArr:
        exCode = subprocess.call([
            "xdg-icon-resource", "install",
            "--noupdate",
            "--context", "mimetypes",
            "--size", aSize,
            f"./setup/icons/scaled/mime-novelwriter-{aSize}.png",
            "application-x-novelwriter-project"
        ])
        if exCode == 0:
            print(f"Installed mime icon size {aSize}")
        else:
            print(f"Error {exCode}: Could not install mime icon size {aSize}")

    # Update Cache
    exCode = subprocess.call(["xdg-icon-resource", "forceupdate"])
    if exCode == 0:
        print("Updated icon cache")
    else:
        print(f"Error {exCode}: Could not update icon cache")

    # Clean up
    if os.path.isfile("./novelwriter.desktop"):
        os.unlink("./novelwriter.desktop")

    print("")
    print("Done!")
    print("")

    return

##
#  XDG Uninstallation (xdg-uninstall)
##

def xdgUninstall():
    """Will attempt to uninstall icons and make a launcher.
    """
    print("")
    print("XDG Uninstall")
    print("=============")
    print("")

    exCode = subprocess.call(
        ["xdg-desktop-menu", "uninstall", "novelwriter.desktop"]
    )
    if exCode == 0:
        print("Uninstalled menu desktop file")
    else:
        print(f"Error {exCode}: Could not uninstall menu desktop file")

    sizeArr = ["16", "22", "24", "32", "48", "64", "96", "128", "256", "512"]

    # App Icon
    for aSize in sizeArr:
        exCode = subprocess.call([
            "xdg-icon-resource", "uninstall", "--noupdate",
            "--context", "apps", "--size", aSize, "novelwriter"
        ])
        if exCode == 0:
            print(f"Uninstalled app icon size {aSize}")
        else:
            print(f"Error {exCode}: Could not uninstall app icon size {aSize}")

    # Mimetype
    for aSize in sizeArr:
        exCode = subprocess.call([
            "xdg-icon-resource", "uninstall", "--noupdate",
            "--context", "mimetypes", "--size", aSize,
            "application-x-novelwriter-project"
        ])
        if exCode == 0:
            print(f"Uninstalled mime icon size {aSize}")
        else:
            print(f"Error {exCode}: Could not uninstall mime icon size {aSize}")

    # Update Cache
    exCode = subprocess.call(["xdg-icon-resource", "forceupdate"])
    if exCode == 0:
        print("Updated icon cache")
    else:
        print(f"Error {exCode}: Could not update icon cache")

    print("")
    print("Done!")
    print("")

    return

##
#  WIN Installation (win-install)
##

def winInstall():
    """Will attempt to install icons and make a launcher for Windows.
    """
    import winreg
    try:
        import win32com.client
    except ImportError:
        print(
            "ERROR: Package 'pywin32' is missing on this system.\n"
            "       Please run 'setup.py pip' to automatically install\n"
            "       dependecies, or run 'pip install --user pywin32'."
        )
        sys.exit(1)

    print("")
    print("Windows Install")
    print("===============")
    print("")

    numVers, hexVers = extractVersion()
    nwTesting = not hexVers[-2] == "f"
    wShell = win32com.client.Dispatch("WScript.Shell")

    if nwTesting:
        linkName = "novelWriter Testing %s.lnk" % numVers
    else:
        linkName = "novelWriter %s.lnk" % numVers

    desktopDir = wShell.SpecialFolders("Desktop")
    desktopIcon = os.path.join(desktopDir, linkName)

    startMenuDir = wShell.SpecialFolders("StartMenu")
    startMenuProg = os.path.join(startMenuDir, "Programs", "novelWriter")
    startMenuIcon = os.path.join(startMenuProg, linkName)

    pythonDir = os.path.dirname(sys.executable)
    pythonExe = os.path.join(pythonDir, "pythonw.exe")

    targetDir = os.path.abspath(os.path.dirname(__file__))
    targetPy = os.path.join(targetDir, "novelWriter.pyw")
    targetIcon = os.path.join(targetDir, "nw", "assets", "icons", "novelwriter.ico")

    if not os.path.isfile(targetPy):
        shutil.copy2(os.path.join(targetDir, "novelWriter.py"), targetPy)

    print("Collecting Info ...")
    print("Desktop Folder:    %s" % desktopDir)
    print("Start Menu Folder: %s" % startMenuDir)
    print("Python Executable: %s" % pythonExe)
    print("Target Executable: %s" % targetPy)
    print("Target Icon:       %s" % targetIcon)
    print("")

    print("Creating Links ...")
    if os.path.isfile(desktopIcon):
        os.unlink(desktopIcon)
        print("Deleted: %s" % desktopIcon)

    if os.path.isdir(startMenuProg):
        for oldIcon in os.listdir(startMenuProg):
            oldPath = os.path.join(startMenuProg, oldIcon)
            if not oldIcon.startswith("novelWriter"):
                continue

            isTesting = oldIcon.startswith("novelWriter Testing")
            if isTesting and nwTesting:
                os.unlink(oldPath)
                print("Deleted: %s" % oldPath)
            if not isTesting and not nwTesting:
                os.unlink(oldPath)
                print("Deleted: %s" % oldPath)

    else:
        os.mkdir(startMenuProg)
        print("Created: %s" % startMenuProg)

    wShortcut = wShell.CreateShortCut(desktopIcon)
    wShortcut.TargetPath = targetPy
    wShortcut.WorkingDirectory = targetDir
    wShortcut.IconLocation = targetIcon
    wShortcut.WindowStyle = 1
    wShortcut.save()
    print("Created: %s" % desktopIcon)

    wShortcut = wShell.CreateShortCut(startMenuIcon)
    wShortcut.TargetPath = targetPy
    wShortcut.WorkingDirectory = targetDir
    wShortcut.IconLocation = targetIcon
    wShortcut.WindowStyle = 1
    wShortcut.save()
    print("Created: %s" % startMenuIcon)

    print("")
    print("Creating registry keys ...")

    def setKey(kPath, kName, kVal):
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, kPath)
        regKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, kPath, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(regKey, kName, 0, winreg.REG_SZ, kVal)
        winreg.CloseKey(regKey)

    mimeIcon = os.path.join(targetDir, "nw", "assets", "icons", "x-novelwriter-project.ico")
    mimeExec = '"%s" "%s" "%%1"' % (pythonExe, targetPy)

    try:
        setKey(r"Software\Classes\.nwx\OpenWithProgids", "novelWriterProject.nwx", "")
        setKey(r"Software\Classes\novelWriterProject.nwx", "", "novelWriter Project File")
        setKey(r"Software\Classes\novelWriterProject.nwx\DefaultIcon", "", mimeIcon)
        setKey(r"Software\Classes\novelWriterProject.nwx\shell\open\command", "", mimeExec)
        setKey(r"Software\Classes\Applications\novelWriter.pyw\SupportedTypes", ".nwx", "")
    except WindowsError:
        print("ERROR: Failed to set registry keys.")
        print("")

    print("")
    print("Done!")
    print("")

    return

##
#  WIN Uninstallation (win-uninstall)
##

def winUninstall():
    """Will attempt to uninstall icons previously installed.
    """
    import winreg
    try:
        import win32com.client
    except ImportError:
        print(
            "ERROR: Package 'pywin32' is missing on this system.\n"
            "       Please run 'pip install --user pywin32' to install it."
        )
        sys.exit(1)

    print("")
    print("Windows Uninstall")
    print("=================")
    print("")

    numVers, hexVers = extractVersion()
    nwTesting = not hexVers[-2] == "f"
    wShell = win32com.client.Dispatch("WScript.Shell")

    if nwTesting:
        linkName = "novelWriter Testing %s.lnk" % numVers
    else:
        linkName = "novelWriter %s.lnk" % numVers

    desktopDir = wShell.SpecialFolders("Desktop")
    desktopIcon = os.path.join(desktopDir, linkName)

    startMenuDir = wShell.SpecialFolders("StartMenu")
    startMenuProg = os.path.join(startMenuDir, "Programs", "novelWriter")
    startMenuIcon = os.path.join(startMenuProg, linkName)

    print("Deleting Links ...")
    if os.path.isfile(desktopIcon):
        os.unlink(desktopIcon)
        print("Deleted: %s" % desktopIcon)
    else:
        print("Not Found: %s" % desktopIcon)

    if os.path.isfile(startMenuIcon):
        os.unlink(startMenuIcon)
        print("Deleted: %s" % startMenuIcon)
    else:
        print("Not Found: %s" % startMenuIcon)

    if os.path.isdir(startMenuProg):
        if not os.listdir(startMenuProg):
            os.rmdir(startMenuProg)
            print("Deleted: %s" % startMenuProg)
        else:
            print("Not Empty: %s" % startMenuProg)

    print("")
    print("Removing registry keys ...")

    theKeys = [
        r"Software\Classes\novelWriterProject.nwx\shell\open\command",
        r"Software\Classes\novelWriterProject.nwx\shell\open",
        r"Software\Classes\novelWriterProject.nwx\shell",
        r"Software\Classes\novelWriterProject.nwx\DefaultIcon",
        r"Software\Classes\novelWriterProject.nwx",
        r"Software\Classes\.nwx\OpenWithProgids",
        r"Software\Classes\.nwx",
        r"Software\Classes\Applications\novelWriter.pyw\SupportedTypes",
        r"Software\Classes\Applications\novelWriter.pyw",
    ]

    for aKey in theKeys:
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, aKey)
            print("Deleted: HKEY_CURRENT_USER\\%s" % aKey)
        except WindowsError:
            print("Not Found: HKEY_CURRENT_USER\\%s" % aKey)

    print("")
    print("Done!")
    print("")

    return

# =============================================================================================== #
#  Windows Installers
# =============================================================================================== #

##
#  Inno Setup Builder (setup-exe, setup-pyz)
##

def innoSetup():
    """Run the Inno Setup tool to build a setup.exe file for Windows based on the pyz package.
    """
    print("")
    print("Running Inno Setup")
    print("##################")
    print("")

    # Read the iss template
    issData = ""
    with open(os.path.join("setup", "win_setup_pyz.iss"), mode="r") as inFile:
        issData = inFile.read()

    numVers, _ = extractVersion()
    issData = issData.replace(r"%%version%%", numVers)
    issData = issData.replace(r"%%dir%%", os.getcwd())

    with open("setup.iss", mode="w+") as outFile:
        outFile.write(issData)

    try:
        subprocess.call(["iscc", "setup.iss"])
    except Exception as e:
        print("Inno Setup failed with error:")
        print(str(e))
        sys.exit(1)

    return

# =============================================================================================== #
#  Process Command Line
# =============================================================================================== #

if __name__ == "__main__":
    """Parse command line options and run the commands.
    """
    # Detect OS
    if sys.platform.startswith("linux"):
        hostOS = OS_LINUX
    elif sys.platform.startswith("darwin"):
        hostOS = OS_DARWIN
    elif sys.platform.startswith("win32"):
        hostOS = OS_WIN
    elif sys.platform.startswith("cygwin"):
        hostOS = OS_WIN
    else:
        hostOS = OS_NONE

    # Set Target OS
    if "--target-linux" in sys.argv:
        sys.argv.remove("--target-linux")
        targetOS = OS_LINUX
    elif "--target-darwin" in sys.argv:
        sys.argv.remove("--target-darwin")
        targetOS = OS_DARWIN
    elif "--target-win" in sys.argv:
        sys.argv.remove("--target-win")
        targetOS = OS_WIN
    else:
        targetOS = hostOS

    helpMsg = (
        "\n"
        "novelWriter Setup Tool\n"
        "======================\n"
        "\n"
        "This tool provides setup and build commands for installing or distibuting novelWriter\n"
        "as a package on Linux, Mac and Windows. The available options are as follows:\n"
        "\n"
        "Some of the commands can be targeted towards a different OS than the host OS. To target\n"
        "the command, add one of '--target-linux', '--target-darwin' or '--target-win'.\n"
        "\n"
        "General:\n"
        "\n"
        "    help         Print the help message.\n"
        "    pip          Install all package dependencies for novelWriter using pip.\n"
        "    clean        Will attempt to delete the 'build' and 'dist' folders.\n"
        "\n"
        "Additional Builds:\n"
        "\n"
        "    qthelp       Build the help documentation for use with the Qt Assistant. Run before\n"
        "                 install to have local help enable in the the installed version.\n"
        "    sample       Build the sample project as a zip file. Run before install to enable\n"
        "                 creating sample projects in the in-app New Project Wizard.\n"
        "\n"
        "Python Packaging:\n"
        "\n"
        "    minimal-zip  Creates a minimal zip file of the core application without all the\n"
        "                 other source files. Accepts a target OS flag.\n"
        "    pack-pyz     Creates a pyz package in a folder with all dependencies using the\n"
        "                 zipapp tool. On Windows, python embeddable is added to the folder.\n"
        "    setup-pyz    Build a Windows installer from a zipapp package using Inno Setup.\n"
        "\n"
        "System Install:\n"
        "\n"
        "    install      Installs novelWriter to the system's Python install location. Run as \n"
        "                 root or with sudo for system-wide install, or as user for single user \n"
        "                 install.\n"
        "    xdg-install  Install launcher and icons for freedesktop systems. Run as root or \n"
        "                 with sudo for system-wide install, or as user for single user install.\n"
        "                 Running 'xdg-uninstall' will remove the icons.\n"
        "    win-install  Install desktop and start menu icons for Windows systems.\n"
        "                 Running 'win-uninstall' will remove the icons.\n"
    )

    # Flags and Variables
    makeSetupPyz = False
    simplePack = False
    embedPython = False

    # General
    # =======

    if "help" in sys.argv:
        sys.argv.remove("help")
        print(helpMsg)
        sys.exit(0)

    if "version" in sys.argv:
        sys.argv.remove("version")
        numVers, hexVers = extractVersion()
        print("Semantic Version: %s" % numVers)
        print("Hexadecimal Version: %s" % hexVers)
        sys.exit(0)

    if "pip" in sys.argv:
        sys.argv.remove("pip")
        installPackages(hostOS)

    if "clean" in sys.argv:
        sys.argv.remove("clean")
        cleanInstall()

    # Additional Builds
    # =================

    if "qthelp" in sys.argv:
        sys.argv.remove("qthelp")
        buildQtDocs()

    if "sample" in sys.argv:
        sys.argv.remove("sample")
        buildSampleZip()

    # Python Packaging
    # ================

    if "minimal-zip" in sys.argv:
        sys.argv.remove("minimal-zip")
        makeMinimalPackage(targetOS)

    if "pack-pyz" in sys.argv:
        sys.argv.remove("pack-pyz")
        simplePack = True
        if hostOS == OS_WIN:
            embedPython = True

    # General Installers
    # ==================

    if "xdg-install" in sys.argv:
        sys.argv.remove("xdg-install")
        if hostOS == OS_WIN:
            print("ERROR: Command 'xdg-install' cannot be used on Windows")
            sys.exit(1)
        else:
            xdgInstall()

    if "xdg-uninstall" in sys.argv:
        sys.argv.remove("xdg-uninstall")
        if hostOS == OS_WIN:
            print("ERROR: Command 'xdg-uninstall' cannot be used on Windows")
            sys.exit(1)
        else:
            xdgUninstall()

    if "win-install" in sys.argv:
        sys.argv.remove("win-install")
        if hostOS == OS_WIN:
            winInstall()
        else:
            print("ERROR: Command 'win-install' can only be used on Windows")
            sys.exit(1)

    if "win-uninstall" in sys.argv:
        sys.argv.remove("win-uninstall")
        if hostOS == OS_WIN:
            winUninstall()
        else:
            print("ERROR: Command 'win-uninstall' can only be used on Windows")
            sys.exit(1)

    # Windows Setup Installer
    # =======================

    if "setup-pyz" in sys.argv:
        sys.argv.remove("setup-pyz")
        if hostOS == OS_WIN:
            makeSetupPyz = True
        else:
            print("Error: Command 'setup-pyz' for Inno Setup is Windows only.")
            sys.exit(1)

    # Actions
    # =======
    # For functions that are controlled by multiple flags, or need to be
    # run in a specific order.

    if simplePack:
        makeSimplePackage(embedPython)

    if makeSetupPyz:
        innoSetup()

    if len(sys.argv) <= 1:
        # Nothing more to do
        sys.exit(0)

    # Run the standard setup
    import setuptools # noqa: F401
    setuptools.setup()

# END Main
