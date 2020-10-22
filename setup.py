#!/usr/bin/env python3
"""
The main setup script for novelWeiter.

It runs the standard setuptool.setup() with all options taken from the
setup.cfg file.

In addtion, a few speicalised commands are available:

 * sample: Will build a sample.zip file, which is the way the sample project is
   included into distributable packages.
 * qthelp: Will build a QtAssistant readable version of the novelWriter
   documentation. This should also be a part of distributed packages. It allows
   for reading the help offline. Otherwise, the F1 button redirects to the
   online documentation only.
 * launcher: Will attempt to install novelWriter icons, mime type and create a
   launcher for the application.

"""
import os
import sys
import shutil
import subprocess
import setuptools

# =============================================================================================== #
#  Qt Assistant Documentation Builder
# =============================================================================================== #

def buildQtDocs():
    """This function will build the documentation as a Qt help file. The
    file is then copied into the nw/assets/help directory and can be
    included in builds.

    Depends on packages:
     * pip install sphinx
     * pip install sphinx-rtd-theme
     * pip install sphinxcontrib-qthelp

    It also requires the qhelpgenerator to be available on the system.
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
        sys.exit(1)
    else:
        print("Documentation build: OK")
    print("")

    return

# =============================================================================================== #
#  Sample Project ZIP File Builder
# =============================================================================================== #

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
#  Create Launcher
# =============================================================================================== #

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
    with open(os.path.join("setup", "novelwriter.desktop"), mode="r") as inFile:
        desktopData = inFile.read()

    desktopData = desktopData.replace(r"%%exec%%", useExec)

    desktopFile = os.path.join(os.getcwd(), "novelwriter.desktop")
    with open(desktopFile, mode="w+") as outFile:
        outFile.write(desktopData)

    exCode = subprocess.call(
        ["xdg-desktop-menu", "install", "--novendor", "./novelwriter.desktop"]
    )
    if exCode == 0:
        print("Installed menu desktop file")
    else:
        print(f"Error {exCode}: Could not install menu desktop file")

    exCode = subprocess.call(
        ["xdg-desktop-icon", "install", "--novendor", "./novelwriter.desktop"]
    )
    if exCode == 0:
        print("Installed icon desktop file")
    else:
        print(f"Error {exCode}: Could not install icon desktop file")

    print("")

    # Install MimeType
    # ================

    exCode = subprocess.call([
        "xdg-mime", "install",
        "setup/mime/x-novelwriter-project.xml"
    ])
    if exCode == 0:
        print("Installed mimetype")
    else:
        print(f"Error {exCode}: Could not install mimetype")

    print("")

    # Install Icons
    # =============

    sizeArr = ["16", "22", "24", "32", "48", "96", "128", "256", "512"]

    # App Icon
    for aSize in sizeArr:
        exCode = subprocess.call([
            "xdg-icon-resource", "install",
            "--novendor", "--noupdate",
            "--context", "apps",
            "--size", aSize,
            f"setup/icons/scaled/icon-novelwriter-{aSize}.png",
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
            f"setup/icons/scaled/mime-novelwriter-{aSize}.png",
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
        print("Error {exCode}: Could not update icon cache")

    print("")
    print("Done!")
    print("")

    return

# =============================================================================================== #
#  Process Jobs
# =============================================================================================== #

if __name__ == "__main__":

    helpMsg = (
        "\n"
        "novelWriter Setup Tool\n"
        "======================\n"
        "This tool provides some additional setup commands for novelWriter.\n"
        "\n"
        "help         Print the help message.\n"
        "qthelp       Build the help documentation for use with the QtAssistant.\n"
        "sample       Build the sample project as a zip file.\n"
        "xdg-install  Install launcher and icons for freedesktop systems.\n"
    )

    if "help" in sys.argv:
        sys.argv.remove("help")
        print(helpMsg)
        sys.exit(0)

    if "qthelp" in sys.argv:
        sys.argv.remove("qthelp")
        buildQtDocs()

    if "sample" in sys.argv:
        sys.argv.remove("sample")
        buildSampleZip()

    if "xdg-install" in sys.argv:
        sys.argv.remove("xdg-install")
        if not sys.platform.startswith("win32"):
            xdgInstall()
        else:
            print("ERROR: xdg-install cannot be used on Windows")
            sys.exit(1)

    if len(sys.argv) <= 1:
        # Nothing more to do
        sys.exit(0)

    # Run the standard setup
    setuptools.setup()

# END Main
