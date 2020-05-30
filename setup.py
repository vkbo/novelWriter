#!/usr/bin/env python3
import setuptools

with open("README.md", "r") as inFile:
    long_description = inFile.read()

setuptools.setup(
    name = "novelWriter",
    version = "0.7",
    author = "Veronica Berglyd Olsen",
    author_email = "code@vkbo.net",
    description = "A markdown-like document editor for writing novels",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    license = "GNU General Public License v3",
    url = "https://github.com/vkbo/novelWriter",
    entry_points = {
        "console_scripts" : ["novelWriter-cli=nw:main"],
        "gui_scripts" :     ["novelWriter=nw:main"],
    },
    packages = setuptools.find_packages(exclude=["docs","tests","sample"]),
    include_package_data = True,
    package_data = {"": ["*.conf"]},
    project_urls = {
        "Bug Tracker": "https://github.com/vkbo/novelWriter/issues",
        "Documentation": "https://novelwriter.readthedocs.io/",
        "Source Code": "https://github.com/vkbo/novelWriter",
    },
    classifiers = [
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Topic :: Text Editors",
    ],
    python_requires = ">=3.6",
    install_requires = [
        "pyqt5>=5.2.1",
        "lxml>=4.2.0",
        "pyenchant>=3.0.0",
    ],
)
