.. _a_setup_win:

****************
Setup on Windows
****************

This is a brief guide to how you can get novelWriter running on a Windows computer.

Unlike other operating systems, Windows does not come prepared with an environment to run Python
applications, so you must first install Python. After that, running novelWriter is straightforward.

.. tip::
   If you have any problems, you can always open a question on the project's discussions_ page.
   This requires a GitHub account.

.. _discussions: https://github.com/vkbo/novelWriter/discussions


.. _a_setup_win_installer:

Using the Installer
===================

The installer for Windows is no longer provided. See the `installer issue`_ for more info on why.
You can still create the installer yourself if you want to. It can be generated with the provided
``setup.py`` script. use the script's ``help`` command to get further instructions.

Please use the "Running from Source" option below instead. It has been improved and a script has
been added that does nearly the same thing.

.. _installer issue: https://github.com/vkbo/novelWriter/issues/640


.. _a_setup_win_source:

Running from Source
===================

To run novelWriter from source, download the latest source zip file from the release page on
GitHub_, or from the `main website`_. You can download the "Minimal Windows" zip file. It is a
minimal version of the source that contains only the files needed for running on Windows. You can
also download the full source if you wish.

In order to make novelWriter run on your system, you must first have Python installed (Step 1).
Thereafter, a script will do the rest of the job (Step 2). Alternatively, you can run this step
manually from the command prompt if you wish to.

.. tip::
   If your system already has all the dependencies installed, you can run novelWriter directly from
   the extracted folder by double-clicking the ``novelWriter.pyw`` file. However, running the
   script also adds start icons.

.. _GitHub: https://github.com/vkbo/novelWriter/releases
.. _main website: https://novelwriter.io


Step 1: Installing Python
-------------------------

If you already have Python installed, you can skip this step. If you don't have it installed, you
can download it from the python.org_ website. novelWriter should work with Python 3.6 or higher,
but it is recommended that you install the latest version of Python.

Make sure you select the "Add Python to PATH" option during installation, otherwise the ``python``
command will not work in the command line window.

.. image:: images/python_win_install.png
   :width: 600

.. _python.org: https://www.python.org/downloads/windows


Step 2: Dependencies and Icons
------------------------------

**Alternative A: By Script**

Open the folder where you extracted novelWriter, and double-click the file named
``windows_install.bat``. This should open a command line window and run the setup script to install
dependencies, and add desktop and start menu icons.

.. note::
   If you downloaded the full source package, the file may be in the ``setup`` subfolder.

The script will also check that it can find Python on your system and alert you if it cannot run
it. If you are sure you have installed it, but the script cannot find it, you probably didn't
install it with the "Add Python to PATH" option mentioned in Step 1.

.. note::
   If you upgrade Python to a newer version and the path to ``pythonw.exe`` has therefore changed,
   you may need to run this script again. You can also run it to upgrade dependencies to the latest
   version.

**Alternative B: Manual Installation**

The above alternative can also be run manually.

Open the windows command prompt. It can be launched by pressing the :kbd:`Win` key and typing "cmd".
The "Command Prompt" app should then be in the list of applications.

With the command prompt open, navigate to the folder where you extracted the novelWriter source,
and run the following commands:

.. code-block:: console

   pip install --user pywin32 -r requirements.txt
   python setup.py win-install

The first command will install the dependencies on your system from the `Python Package Index`_,
and the second command will create a desktop icon and a start menu icon. That should be all that
you need.

.. _Python Package Index: https://pypi.org/


Uninstalling
============

**Alternative A: By Script**

Open the folder where you keep the novelWriter files, and double-click the file named
``windows_uninstall.bat``. This should open a command line window and run the setup script to
remove the main dependency packages and remove desktop and start menu icons.

.. note::
   If you downloaded the full source package, the file may be in the ``setup`` subfolder.

If you plan to also remove Python from your system, you must run the above script first as it needs
Python in order to run.

.. note::
   Due to limitations of the ``pip`` installer, dependencies of the dependencies will not be
   removed, only the ones the setup script directly installed.

**Alternative B: Manual Uninstallation**

Like for the install process, the script just runs two commands. You can of course run them
yourself if you wish. They are:

.. code-block:: console

   python setup.py win-uninstall
   pip uninstall -r requirements.txt

There may be other packages on your system installed by ``pip``. To list all packages, run:

.. code-block:: console

   pip freeze --user
