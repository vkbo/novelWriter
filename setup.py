#!/usr/bin/env python3
import os
import sys
import subprocess
import setuptools

from nw import __version__, __url__, __docurl__, __issuesurl__, __sourceurl__

##
#  Build the Package
##

buildDocs = False
buildSample = False

if "qthelp" in sys.argv:
    buildDocs = True
    sys.argv.remove("qthelp")

if "sample" in sys.argv:
    buildSample = True
    sys.argv.remove("sample")

##
#  Qt Assistant Documentation
##

if buildDocs:

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
        print("Failed with error:")
        print(str(e))
        buildFail = True

    try:
        subprocess.call(["qhelpgenerator", os.path.join(buildDir, inFile)])
    except Exception as e:
        print("Failed with error:")
        print(str(e))
        buildFail = True

    if not os.path.isdir(helpDir):
        try:
            os.mkdir(helpDir)
        except Exception as e:
            print("Failed with error:")
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
        print("Failed with error:")
        print(str(e))
        buildFail = True

    print("")
    if buildFail:
        print("Documentation build: FAILED")
        sys.exit(1)
    else:
        print("Documentation build: OK")
    print("")

##
#  Sample Project ZIP file
##

if buildSample:

    srcSample = "sample"
    dstSample = os.path.join("nw", "assets", "sample.zip")

    if os.path.isdir(srcSample):
        if os.path.isfile(dstSample):
            os.unlink(dstSample)

        from zipfile import ZipFile

        with ZipFile(dstSample, "w") as zipObj:
            zipObj.write(os.path.join(srcSample, "nwProject.nwx"), "nwProject.nwx")
            for docFile in os.listdir(os.path.join(srcSample, "content")):
                srcDoc = os.path.join(srcSample, "content", docFile)
                zipObj.write(srcDoc, "content/"+docFile)

    else:
        print("Error: Could not find sample project source directory.")
        sys.exit(1)

if len(sys.argv) == 1:
    # Nothing more to do
    sys.exit(0)

##
#  Build the Package
##

# Read content from files
with open("README.md", "r") as inFile:
    longDescription = inFile.read()

with open("requirements.txt", "r") as inFile:
    pkgRequirements = inFile.read().strip().splitlines()

setuptools.setup(
    name = "novelWriter",
    version = __version__,
    author = "Veronica Berglyd Olsen",
    author_email = "code@vkbo.net",
    description = "A markdown-like document editor for writing novels",
    long_description = longDescription,
    long_description_content_type = "text/markdown",
    license = "GNU General Public License v3",
    url = __url__,
    entry_points = {
        "console_scripts" : ["novelWriter-cli=nw:main"],
        "gui_scripts" :     ["novelWriter=nw:main"],
    },
    packages = setuptools.find_packages(exclude=["docs", "tests", "sample"]),
    include_package_data = True,
    package_data = {"": ["*.conf"]},
    project_urls = {
        "Bug Tracker": __issuesurl__,
        "Documentation": __docurl__,
        "Source Code": __sourceurl__,
    },
    classifiers = [
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Topic :: Text Editors",
    ],
    python_requires = ">=3.6",
    install_requires = pkgRequirements,
)
