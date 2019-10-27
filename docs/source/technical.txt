
Technical Information
=====================

This section contains details of how novelWriter stores and handles the project data.

How Data is Stored
^^^^^^^^^^^^^^^^^^

Main Project File
~~~~~~~~~~~~~~~~~

The project itself requires a dedicated folder for storing its files.
The main project file is stored as an XML file with the name ``nwProject.nwx``.
This file contains all the meta data unique for the project.
That includes project settings.

If this file is lost or corrupted, the structure of the project is lost.
It is important to keep this file backed up.

The project XML file is suitable for diff tools and version control, although a timesetamp is set in the meta section on line 2 each time the file is saved.

Project Documents
~~~~~~~~~~~~~~~~~

The project documents are saved in folders staring with ``data_``.
Each document has a file handle taken from the first 13 characters of a SHA256 hash of the system time.
The documents are saved with a folder and filename derived from this hash.

The reason for this is to avoid issues with file naming conventions and restrictions.
The file name set in the tree view is only saved in the project XML file.

Each document file contains a plain text version of the text from the editor.
The file can in principle be edited in any text editor, and is suitable for diffing and version control if so desired.
