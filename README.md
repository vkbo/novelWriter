# novelWriter

[![Build Status](https://travis-ci.com/vkbo/novelWriter.svg?branch=master)](https://travis-ci.com/vkbo/novelWriter)
[![codecov](https://codecov.io/gh/vkbo/novelWriter/branch/master/graph/badge.svg)](https://codecov.io/gh/vkbo/novelWriter)

novelWriter is a markdown-like text editor designed fro writing novels and larger projects of many smaller plain text documents.

It is under initial development, but is currently usable.
The application is written with Python3 and PyQt5, and developed on Linux.
It should work fine on other operating systems as well.

**Note:** This application is designed specifically for my own needs as I work on my projects.
I will only add features as I need them. I am trying to make the application as general as possible within that limitation.

The application can be started from the source folder with the command:
```
./novelWriter.py
```

It also takes a few parameters for debugging and such, which can be listed with the switch `--help`.

There are no launcher icons yet. Consult your operating system documentation for how to make those.
I will add those later.

## Features

The file format for the written text is a format similar to markdown, but with a few extensions and a few omissions.
Project meta data is stored as XML.
The editor has syntax highlighting for the features it supports, and includes a set of different syntax highlighting themes.
The GUI also has an optional dark theme in addition to the default system theme.

Themes can easily be added to the `nw/themes` folder. Have a look in the existing folders for examples.

Open documents and the project file itself is saved regularly on a timer if they have been altered.
The status of this is indicated by two indicators in the right corner of the status bar. Unsaved changes are in yellow, and saved is indicated by green. The indicators are marked with `P` for project and `D` for document.
Latest character count, word count, and paragraph count is shown next to these indicators in the status bar.
The counts are updated regularly, but not as-you-type.

The tree view also shows the word count per file, and total counts for the folders.
Next to the count is a status flag. When an item is selected, the panel below the tree view will show more details.
A novel file can use the status to set how far along from new to draft to finished it is, and the status flag for other files can be used to indicate the importance of for instance plot elements, characters, locations, etc.
These flags are meant to be customisable, bit the interface hasn't been added yet.

Next to the colour icon is a flag that indicates the class of the file or folder, that is `N` for Novel, `C` for character, and so on. The last flag indicates file type. This is spelled out in the details pane at the bottom, and can be edited by pressing `Ctrl+E` or from the menu.

The main documentation is available in the application in the Help menu or by pressing `F1`.

The core features of novelWriter are:

* A plain text editor with a minimal set of markdown formatting features, plus a few additional features like tags and comments. Tags and comments are not counted towards word counts.
* Most features have keyboard shortcuts to speed up using the editor.
* Files are organised in a tree view with no automatic ordering. The order of the files are as you set them, and are saved in the same order.
* Files live in a set of root folders, and cannot be moved between them. These are currently `Novel`, `Character`, `Plot`, `World`, `Timeline`, `Object` and `Custom`. There can only be one of each, except for the `Custom` one.
* Within the root folders files can be organised in subfolders. The folders will have no impact on the layout of the compiled novel when I get around to adding the export feature. They are simply there for your convenience. The order of the text files in the final novel is dictated purely from the order of entries in the tree.
* Each file can have a file layout, which currently doesn't do anything other than indicate the purpose of the file. It will, however, be used to control the format and structure of the parts of the novel when the export features are added. Each chapter must have a chapter type file. The text of the chapter can be put in the same file, or in following scene files. The choice is yours. The entire book can also be written in a single file of type `Book`.
* Documents can be either opened in the editor (left pane) or in view mode (right pane). That means two documents can be opened at once, making it easier to work on one while following the other.
* When tags and references are set in the documents, a timeline window will show the relationship between the novel sections and the supporting files like character files, locations, plot elements, etc.

## Dependencies

For the apt package manager, the following Python3 packages are needed:

* `python3-pyqt5` for the GUI
* `python3-pyqt5.qtsvg` may need to be installed separately
* `python3-appdirs` for locating the system's config folder
* `python3-lxml` for writing project files

These are optional, but recommended:

* `python3-enchant` for spell checking
* `python3-pycountry` for translating language codes to language names

Alternatively, the packages can be installed with `pip` by running
```
pip install -r requirements.txt
```
in the application folder.

## Screenshot

![Screenshot 1](screenshot.png)
