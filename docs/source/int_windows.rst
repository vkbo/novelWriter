.. _a_setup_win:

****************
Setup on Windows
****************

.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _main website: https://novelwriter.io
.. _zipapp: https://docs.python.org/3/library/zipapp.html
.. _Inno Setup: https://jrsoftware.org/isinfo.php
.. _python.org: https://www.python.org/downloads/windows
.. _PyPi: https://pypi.org/project/novelWriter
.. _discussions: https://github.com/vkbo/novelWriter/discussions

This is a brief guide to how you can get novelWriter running on a Windows computer.

On Windows, you have two options: You can either run from source, or install novelWriter via a
Windows installer. The latter is the simplest, but since novelWriter is a hobby project, the
installer is not signed and downloading and running the installer often triggers warning because
Windows doesn't know whether it's safe or not.

The installer contains an executable zip of novelWriter, a copy of the three libraries it depends
on, and a copy of the Python run environment. If you're uncomfortable with running this installer,
you can install the components yourself and just run novelWriter directly from the source code. The
Source code can be downloaded as a zip file directly from GitHub_.


.. _a_setup_win_installer:

Using the Installer
===================

You can install novelWriter with the Windows installer for 64-bit Windows available on the
`main website`_ and GitHub_ page. This installer bundles all that is needed for novelWriter to run,
including Python and the XML and Qt libraries. When installing novelWriter this way, you don't need
to install any of the dependencies manually. The installer is made with zipapp_ and `Inno Setup`_.


.. _a_setup_win_source:

Running from Source
===================

To run novelWriter from source, download the latest source package from the release page on
GitHub_, or if you have git running on your computer, you can also clone the repository.

The main requirement is that you have Python installed. The dependencies of novelWriter can then be
installed from the Python Package Index, PyPi_.

Step 1: Installing Python
-------------------------

If you already have Python installed, you can skip this step. If you don't have it installed, you
can download it from the python.org_ website. novelWriter should work with Python 3.6 or higher,
but it is recommended that you install the latest version of Python.

Also, make sure you select the "Add Python to PATH" option during installation, otherwise the
``python`` command will not work in the command line window.

.. image:: images/python_win_install.png
   :width: 600

Step 2: Dependencies and Icons
------------------------------

**Alternative A: By Script**

Open the folder where you extracted the novelWriter source, and double-click the file named
``win_install`` or ``win_install.bat``. This should open a command line window and run the setup
script to install dependencies and desktop and start menu icons.

**Alternative B: Command Prompt**

The above alternative can also be run manually.

Open the windows command prompt. It can be launched by pressing the :kbd:`Win` key and typing "cmd".
The "Command Prompt" app should then be in the list of applications.

With the command prompt open, navigate to the folder where you extracted the novelWriter source,
and run the following commands.

.. code-block:: console

   python setup.py pip
   python setup.py win-install

The first command will install the dependencies on your system, and the second command will create
a desktop icon and a start menu icon.

That should be all that you need. If you have any problems, you can always open a question on the
project's discussions_ page. This requires a GitHub account.
