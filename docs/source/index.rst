#############################
Documentation for novelWriter
#############################

.. image:: images/novelwriter_logo.png
   :align: right
   :width: 48

| **For Release:** |release|
| **Last Updated:** |today|
|

novelWriter is an open source plain text editor designed for writing novels assembled from many
smaller text documents. It uses a minimal formatting syntax inspired by Markdown, and adds a meta
data syntax for comments, synopsis, and cross-referencing. It is designed to be a simple text
editor that allows for easy organisation of text and notes, using human readable text files as
storage for robustness.

.. figure:: images/screenshot_multi.png
   :align: center
   :width: 500

The project storage is suitable for version control software, and also well suited for file
synchronisation tools. All text is saved as plain text files with a meta data header. The core
project structure is stored in a single project XML file. Other meta data is primarily saved as
JSON files. See the :ref:`a_breakdown_storage` section for more details.

Any operating system that can run Python 3 and has the Qt 5 libraries should be able to run
novelWriter. It runs fine on Linux, Windows and macOS, and users have tested it on other platforms
as well. novelWriter can also be run directly from the Python source, or installed from packages or
the pip tool. See :ref:`a_started` for more details.

.. note::
   Version 1.3 introduced a few changes that will require you to make some minor modifications to
   some of the headings in your project. It should be fairly quick and straightforward. Please see
   the :ref:`a_prjfmt_1_3` section for more details.

**Useful Links**

* Website: https://novelwriter.io
* Documentation: https://novelwriter.readthedocs.io
* Internationalisation: https://crowdin.com/project/novelwriter
* Source Code: https://github.com/vkbo/novelWriter
* Source Releases: https://github.com/vkbo/novelWriter/releases
* Issue Tracker: https://github.com/vkbo/novelWriter/issues
* Feature Discussions: https://github.com/vkbo/novelWriter/discussions
* PyPi Project: https://pypi.org/project/novelWriter
* Social Media: https://fosstodon.org/@novelwriter

.. toctree::
   :hidden:

   Main Page <self>

.. toctree::
   :maxdepth: 1
   :caption: Introduction
   :hidden:

   int_introduction
   int_overview
   int_started
   int_source
   int_customise

.. toctree::
   :maxdepth: 1
   :caption: Using novelWriter
   :hidden:

   usage_breakdown
   usage_interface
   usage_format
   usage_shortcuts
   usage_typography
   usage_projectformat

.. toctree::
   :maxdepth: 1
   :caption: Organising Your Project
   :hidden:

   project_overview
   project_structure
   project_notes
   project_export

.. toctree::
   :maxdepth: 1
   :caption: Under the Hood
   :hidden:

   tech_locations
   tech_storage
   tech_tests
