#####################
novelWriter |release|
#####################

.. only:: html

   .. image:: https://github.com/vkbo/novelWriter/workflows/python%203.8/badge.svg?branch=main
      :target: https://github.com/vkbo/novelWriter/actions
      :alt: Python Tests

   .. image:: https://codecov.io/gh/vkbo/novelWriter/branch/main/graph/badge.svg
      :target: https://codecov.io/gh/vkbo/novelWriter
      :alt: Code Coverage

   .. image:: https://readthedocs.org/projects/novelwriter/badge/?version=latest
      :target: https://novelwriter.readthedocs.io/en/latest/?badge=latest
      :alt: Documentation

   .. image:: https://img.shields.io/github/v/release/vkbo/novelwriter
      :target: https://github.com/vkbo/novelWriter/releases
      :alt: GitHub Release

   .. image:: https://img.shields.io/pypi/v/novelwriter
      :target: https://pypi.org/project/novelWriter/
      :alt: PyPI

   .. image:: https://img.shields.io/pypi/pyversions/novelwriter
      :target: https://pypi.org/project/novelWriter/
      :alt: Python Version

**Last Updated:** |today|

novelWriter is a plain text editor designed for writing novels assembled from many smaller text
documents. It uses a minimal formatting syntax inspired by Markdown, and adds a meta data syntax
for comments, synopsis, and cross-referencing. It is designed to be a simple text editor that
allows for easy organisation of text and notes, using human readable text files as storage for
robustness.

The project storage is suitable for version control software, and also well suited for file
synchronisation tools. All text is saved as plain text files with a meta data header. The core
project structure is stored in a single project XML file. Other meta data is primarily saved as
JSON files. See also the :ref:`a_storage` section for more details.

Any operating system that can run Python 3 and has the Qt 5 libraries should be able to run
novelWriter. It runs fine on Linux, Windows and macOS, and users have tested it on other platforms
too. novelWriter can be run directly from the Python source, installed from the pip tool.

You can also download a minimal archive package of novelWriter tailored for your operating system.
This package can be extracted anywhere on your computer, and a setup script can be run to create
the necessary icons and file associations. See :ref:`a_started`, or one or the setup instructions
for your operating system for further details.

.. note::
   Version 1.5 introduces a few changes that will require you to make a few minor modifications to
   some of the headings in your project. It should be fairly quick and straightforward. Please see
   the :ref:`a_prjfmt_1_3` section for more details.

**Useful Links**

* Website: https://novelwriter.io
* Documentation: https://novelwriter.readthedocs.io
* Source Code: https://github.com/vkbo/novelWriter
* Source Releases: https://github.com/vkbo/novelWriter/releases
* Issue Tracker: https://github.com/vkbo/novelWriter/issues
* Feature Discussions: https://github.com/vkbo/novelWriter/discussions
* PyPi Project: https://pypi.org/project/novelWriter


.. toctree::
   :maxdepth: 2
   :caption: Introduction

   int_introduction
   int_started
   setup_linux
   setup_mac
   setup_windows


.. toctree::
   :maxdepth: 2
   :caption: Using novelWriter

   usage_interface
   usage_format
   usage_shortcuts
   usage_typography
   usage_projectformat


.. toctree::
   :maxdepth: 2
   :caption: Organising Your Project

   project_overview
   project_structure
   project_notes
   project_export


.. toctree::
   :maxdepth: 2
   :caption: Under the Hood

   tech_storage
   tech_tests


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
