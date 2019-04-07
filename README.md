# novelWriter

This is a reboot of my novelWriter application using Qt5 after abandoning the Gtk3 version now renamed novelWriterGtk and archived.
The first usable version is under initial development.

The application is written with Python3 and PyQt5, and developed on Linux. I will try to make sure it works on Windows as well.

**Note:** This application is designed specifically for my own needs as I work on my projects.
I will only add features as I need them. I am trying to make the application as general as possible within that limitation.

## Features

The file format for the written text is a format similar to markdown, but with a few extensions.
Project meta data is stored as XML.

Here is an overview of the core features I want to implement as a starting point:

* A simple plain text editor with a minimal set uf text decoration features based on markdown.
* In addition to markdown type headings and text emphasis, I'm adding:
  * `%` as the first character on the line to indicate a comment. That is, text that is neither counted towards the word count, nor exported when the document is converted.
  * `@` as the first character on a line to indicate name/value metadata in files. This can be used to set POV characters, locations, etc. in scene and chapter files.
* Each document can have subdocuments. The novel is intended to be broken down into Novel > Chapter > Scene, but it should be possible to split novel into chapter files, a chapter into scenes files automatically based on markdown headers of level 1 to 3.
* The files are organised in a tree view, and there is no automatic sorting of the tree. That is, the order is the order the user decides.
* Basic visualisation tools for the novel meta data if POV, locations, etc. have been set in the files.
* The file format of projects should be such that version control software can be used. That is, no binary files.

Future features that will be added:

* Export options for HTML, open document format and PDF (probably via LaTeX or Pandoc).
* Basic git integration to allow for reverting the project to a previous state while retaining the possibility to move forward again. That is, allow for automatic branching and commits.
* An automated backup to zip file on exit or request.

## Dependencies

* python3-pyqt5
* python3-appdirs
* python3-lxml
