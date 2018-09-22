# novelWriter

This is a reboot of my novelWriter application using Qt5 after abandoning the Gtk3 version now renamed novelWriterGtk.

As an amateur science fiction writer, I have been looking for a simple tool to organise text files into a novel.

While there are a number of tools ranging from the excellent distraction free editors to complex project organisers, there isn't anything that combines the features I am looking for.

Here is an overview of the core features I want to implement as a starting point:

* Multi-tabbed editor allowing the user to work on multiple files at the same time.
* A non-sorted tree view for easy navigation between the files. The tree view must not be sorted automatically as one wants to order the scene or chapter files in the order they should appear in the finished novel.
* Scene meta data including POV, character, location, plot and timeline information in a tag-style manner.
* Basic visualisation tools for the novel meta data.
* The file format should be such that version control software can be used for the projects. That is, no binary files.

Future features that will be added:

* Export options for HTML, open document format and PDF (probably via LaTeX or Pandoc).

## Dependencies

* python3-pyqt5
* python3-appdirs
