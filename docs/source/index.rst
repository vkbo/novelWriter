#####################
novelWriter |release|
#####################

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

novelWriter is a markdown-like text editor designed for writing novels and larger projects of many
smaller plain text documents. It uses its own flavour of markdown that supports a meta data syntax
for comments, synopsis and cross-referencing between documents. The idea is to have a simple text
editor which allows for easy organisation of text documents and notes, built on a plain text file
project repository for robustness.

The plain text storage is suitable for version control software, and also well suited for file
synchronisation tools. The core project structure is stored in a single project XML file. Other
meta data is primarily saved as JSON files.

Any operating system that can run Python 3 and has the Qt 5 libraries should be able to run
novelWriter. It runs fine on Linux, Windows and macOS, and users have tested it on other platforms
too. novelWriter can be run directly from the Python source, or installed from the pip tool or via
the provided setup script. A setup.exe is provided for Windows. See :ref:`a_started` for further
details.

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
   :caption: Usage

   usage_interface
   usage_projects
   usage_structure
   usage_notes
   usage_export
   usage_typography


.. toctree::
   :maxdepth: 2
   :caption: Under the Hood

   tech_technical


Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
