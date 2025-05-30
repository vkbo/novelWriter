.. _docs_technical_locations:

**************
File Locations
**************

.. _QStandardPaths: https://doc.qt.io/qt-6/qstandardpaths.html

novelWriter will create a few files on your system outside of the application folder itself. These
file locations are described in this chapter.


.. _docs_technical_locations_conf:

Configuration
=============

The general configuration of novelWriter, including everything that is in **Preferences**, is saved
in one central configuration file. The location of this file depends on your operating system. The
system paths are provided by the Qt QStandardPaths_ class and its ``ConfigLocation`` value.

The standard paths are:

* Linux: ``~/.config/novelwriter/novelwriter.conf``
* MacOS: ``~/Library/Preferences/novelwriter/novelwriter.conf``
* Windows: ``C:\Users\<USER>\AppData\Local\novelwriter\novelwriter.conf``

Here, ``~`` corresponds to the user's home directory on Linux and MacOS, and ``<USER>`` is the
user's username on Windows.

.. note::
   These are the standard operating system defined locations. If your system has been set up in a
   different way, these locations may also be different.


.. _docs_technical_locations_data:

Application Data
================

novelWriter also stores a bit of data that is generated by the user's actions. This includes the
list of recent projects form the **Welcome** dialog. Custom themes should also be saved here. The
system paths are provided by the Qt QStandardPaths_ class and its ``AppDataLocation`` value.

The standard paths are:

* Linux: ``~/.local/share/novelwriter/``
* MacOS: ``~/Library/Application Support/novelwriter/``
* Windows: ``C:\Users\<USER>\AppData\Roaming\novelwriter\``

Here, ``~`` corresponds to the user's home directory on Linux and MacOS, and ``<USER>`` is the
user's username on Windows.

.. note::
   These are the standard operating system defined locations. If your system has been set up in a
   different way, these locations may also be different.

The Application Data location also holds several folders:

``cache``
   This folder is used to save the preview data for the **Manuscript Build** tool.

``icons``, ``syntax`` and ``themes``
   These folders are empty by default, but this is where the user can store custom theme files.
   See :ref:`docs_more_custom` for more details.
