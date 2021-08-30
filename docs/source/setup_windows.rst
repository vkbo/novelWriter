.. _a_setup_win:

****************
Setup on Windows
****************

This is a brief guide to how you can get novelWriter running on a Windows computer.

Unlike other operating systems, Windows does not come prepared with an environment to run Python
applications, so you must first install Python. After that, running novelWriter is straightforward.


.. _a_setup_win_install:

Install novelWriter
===================

The recommended way to run novelWriter on Windows is to download the "Minimal Package" option from
the `main website`_, or from the GitHub_ releases page (it's the same download file).

This is a zip file containing only the files you need to run novelWriter on Windows. In order to
make it run on your system, you must first have Python installed (Step 1). Thereafter, a script
will do the rest of the job (Step 2).

.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _main website: https://novelwriter.io


Step 1: Installing Python
-------------------------

If you already have Python installed, you can skip this step. If you don't have it installed, you
can download it from the `python.org`_ website. novelWriter should work with Python 3.6 or higher,
but it is recommended that you install the latest version of Python.

Make sure you select the "Add Python to PATH" option during installation, otherwise the ``python``
command will not work in the command line window.

.. image:: images/python_win_install.png
   :width: 600

.. _python.org: https://www.python.org/downloads/windows


Step 2: Installing novelWriter
------------------------------

Extract the novelWriter zip file, and move the extracted folder to a suitable location. You should
probably not keep it on your desktop or in your downloads folder where it may be accidentally
deleted. Instead, move and rename it to for instance ``C:\novelWriter``.

After you've got the folder where you want it, open it and double-click the file named
``windows_install.bat``. This will open a command line window and run the setup script to install
dependencies, and add desktop and start menu icons.


.. _a_setup_win_update:

Update novelWriter
==================

To update novelWriter, simply replace the folder containing the old version with the extracted
folder of the new version you've downloaded. After this, you may need to run the
``windows_install.bat`` script again to update icons.

.. tip::
   As long as your system has all the dependencies installed, you can also run novelWriter directly
   from the extracted folder by double-clicking the ``novelWriter.pyw`` file.


.. _a_setup_win_uninstall:

Uninstall novelWriter
=====================

If you installed novelWriter with the method described above, you can uninstall it again by
double-clicking the file named ``windows_uninstall.bat``. This should open a command line window
and run the setup script to remove the main dependency packages and remove desktop and start menu
icons.

After that, you can simply delete the novelWriter folder.

If you want to remove Python, it has its own uninstall tool. Just keep in mind that the Python
package manager may leave some files on your system.


.. _a_setup_win_manual:

Manual Approach
===============

If you want more control of what's happening during the install process, or want to do the steps
yourself, you can run the install steps below from a command line window from inside the folder
containing either the minimal package, or the extracted full source package.

.. code-block:: console

   pip install --user -r requirements.txt
   pip install --user pywin32
   python setup.py win-install

The first command will install the three main dependencies of novelWriter using the
`Python Package Index`_ install tool. The packages are ``PyQt5`` for the GUI, ``lxml`` for handling
XML data files, and ``PyEnchant`` for spell checking.

The second command installs a Python tool for Windows that assists the setup script in installing
icons and setting a few registry keys.

The third command runs the setup script that creates the icons for your desktop and start menu, and
adds the necessary registry keys so you can also launch a project by double-clicking a novelWriter
project file from your file explorer.

The above steps can be reverted by running:

.. code-block:: console

   python setup.py win-uninstall
   pip uninstall pywin32
   pip uninstall -r requirements.txt

.. _Python Package Index: https://pypi.org/


Windows Installer
-----------------

There used to be a Windows installer, but this is no longer provided. See the `installer issue`_
for more info on why. You can still create the installer yourself if you want to. It can be
generated with the provided ``setup.py`` script. use the script's ``help`` command to get further
instructions.

.. _installer issue: https://github.com/vkbo/novelWriter/issues/640
