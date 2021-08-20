.. _a_storage:

******************
How Data is Stored
******************

This section contains details of how novelWriter stores and handles the project data.


Project Structure
=================

All novelWriter files are written with utf-8 encoding. Since Python automatically converts Unix
line endings to Windows line endings on Windows systems, novelWriter does not make any adaptations
to the formatting on Windows systems. This is handled entirely by the Python standard library.
Python also handles this fairly well when working on the same files on both Windows and Unix-based
operating systems.


Main Project File
-----------------

The project itself requires a dedicated folder for storing its files where novelWriter will create
its own "file system" where the folder and file hierarchy is described in a project XML file. This
is the main project file in the project's root folder with the name ``nwProject.nwx``. This file
also contains all the meta data required for the project, and a number of related project settings.

If this file is lost or corrupted, the structure of the project is lost, although not the text
itself. It is important to keep this file backed up, either through the built-in backup tool, or
your own backup solution.

.. tip::
   The novelWriter project folder is structured so that it can easily be added to a version control
   system like git. If you do so, you may want to add a `.gitignore` file to exclude files with the
   extensions `.json` as JSON files are used to cache the index and various run-time settings and
   are generally large files that change often. You'd also want to exclude the ``cache`` folder.

The project XML file is indent-formatted, and is suitable for diff tools and version control since
most of the file will stay static, although a timesetamp is set in the meta section on line 2, and
various meta data entries incremented, on each save.


Project Documents
=================

All the project documents are saved in a folder in the main project folder named ``content``. Each
document has a file handle taken from the first 13 characters of a SHA256 hash of the system time
when the document was first created, plus an incremented number. The documents are saved with a
filename assembled from this hash and the file extension ``.nwd``.

If you wish to find the file system location of a document in the project, you can either look it
up in the project XML file, select :guilabel:`Show File Details` from the :guilabel:`Document` menu
when having the document open, or look in the ``ToC.txt`` file in the root of the project folder.
The ``ToC.txt`` file has a list of all documents in the project, referenced by their label, and
where they are saved.

The reason for this cryptic file naming is to avoid issues with file naming conventions and
restrictions on different operating systems, and also to have a file name that does not depend on
what the user names the document within the project, or changes it to.

Each document file contains a plain text version of the text from the editor. The file can in
principle be edited in any text editor, and is suitable for diffing and version control if so
desired. Just make sure the file remains in utf-8 encoding, otherwise unicode characters may
become mangled when the file is opened in novelWriter again.

Editing these files is generally not recommended outside of special circumstances, whatever they
may be. The reason for this is that the index will not be automatically updated when doing so,
which means novelWriter doesn't know you've altered the file. If you do edit a file in this manner,
you should rebuild the index when you next open the project in novelWriter.

The first lines of the file may contain some meta data starting with the characters ``%%~``. These
lines are mainly there to restore some information if it is lost from the project file, and the
information may be helpful if you do open the file in an external editor as it contains the
document label and the document class and layout. The lines can be deleted without any consequences
to the rest of the content of the file, and will be added back the next time the document is saved
in novelWriter.


The File Saving Process
-----------------------

When saving the project file, or any of the documents, the data is first saved to a temporary file.
If successful, the old data file is then removed, and the temporary file becomes the new file. This
ensures that the previously saved data is only replaced when the new data has been successfully
saved to the storage medium.

For the project XML file, a ``.bak`` file is in addition kept, which will always contain the
previous version of the file, although when auto-save is enabled, they may have the same content.
If the opening of a project file fails, novelWriter will automatically try to open the ``.bak``
file instead.


Project Meta Data
=================

The project folder contains a subfolder named ``meta``, containing a number of files. The meta
folder contains semi-important files. That is, they can be lost with only minor impact to the
project.

If you use version control software on your project, you can exclude this folder, although you may
want to track the session log file. The JSON files within this folder can safely be ignored as they
will be automatically regenerated if lost.


The Project Index
-----------------

Between writing sessions, the project index is saved in a JSON file in ``meta/tagsIndex.json``.
This file is not critical. If it is lost, it can be rebuilt from within novelWriter from the
:guilabel:`Tools` menu.

The index is maintained and updated whenever a document or note is saved in the editor. It contains
all references and tags in documents and notes, as well as the location of all headers in the
project, and the word counts within each header section.

The integrity of the index is checked when the file is loaded. It is possible to corrupt the index
if the file is manually edited and manipulated, so the check is important to avoid sudden crashes
of novelWriter. If the file contains errors, novelWriter will automatically build it anew. If the
check somehow fails and novelWriter keeps crashing, you can delete the file manually and rebuild
the index. If this too fails, you have likely encountered a bug.


Cached GUI Options
------------------

A file named ``meta/guiOptions.json`` contains the latest state of various GUI buttons, switches,
dialog window sizes, column sizes, etc, from the GUI. These are the GUI settings that are specific
to the project. Global GUI settings are stored in the main config file.

The file is not critical, but if it is lost, all such GUI options will revert back to their default
settings.


Session Stats
-------------

The writing progress is saved in the ``meta/sessionStats.log`` file. This file records the length
and word counts of each writing session on the given project. The file is used by the
:guilabel:`Writing Statistics` tool. If this file is lost, the history it contains is also lost,
but it has otherwise no impact on the project.


Project Cache
=============

The project ``cache`` folder contains non-critical files. If these files are lost, there is no
impact on the functionality of novelWriter or the history of the project. It contains temporary
files, like the preview document in the :guilabel:`Build Novel Project` tool.

It should be excluded from version control tools if such are used.
