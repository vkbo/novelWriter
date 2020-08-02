#!/usr/bin/env python3
import setuptools

from nw import __version__, __url__, __docurl__, __issuesurl__, __sourceurl__

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
    packages = setuptools.find_packages(exclude=["docs","tests","sample"]),
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
