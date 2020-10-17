#!/usr/bin/env python3
import os
import sys
import subprocess
import setuptools

# =========================================================================== #
#  Qt Assistant Documentation Builder
# =========================================================================== #

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

# =========================================================================== #
#  Sample Project ZIP File Builder
# =========================================================================== #

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

# =========================================================================== #
#  Process Jobs
# =========================================================================== #

if __name__ == "__main__":

    # Process non-standard jobs

    if "qthelp" in sys.argv:
        sys.argv.remove("qthelp")
        buildQtDocs()

    if "sample" in sys.argv:
        sys.argv.remove("sample")
        buildSampleZip()

    if len(sys.argv) == 1:
        # Nothing more to do
        sys.exit(0)

    # Run the standard setup
    setuptools.setup()

# END Main
