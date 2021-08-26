.. _a_pytest:

*************
Running Tests
*************

The novelWriter source code is well covered by tests. The test framework used for the development
is ``pytest`` with the use of an extension for Qt.


Dependencies
============

The dependencies for running the tests can be installed with:

.. code-block:: console

   pip install -r requirements-dev.txt

This will install a couple of extra packages for coverage and test management. The minimum
requirement is just ``pytest`` and ``pytest-qt``.


Simple Test Run
===============

To run the tests, you simply need to execute the following from the root of the source folder:

.. code-block:: console

   pytest

Since several of the tests involve opening up the novelWriter GUI, you may want to disable the GUI
for the duration of the test run. Moving your mouse while the tests are running may otherwise
interfere with the execution of some tests.

You can disable the renderring of the GUI by setting the flag ``export QT_QPA_PLATFORM=offscreen``,
or alternatively run the tests with the ``xvfb`` package, like so:

.. code-block:: console

   xvfb-run pytest


Advanced Options
================

Adding the flag ``-v`` to the ``pytest`` command will increase verbosity of the test execution.

You can also add coverage report generation. For instance to HTML:

.. code-block:: console

   xvfb-run pytest -v --cov=novelwriter --cov-report=html

Other useful report formats are ``xml``, and ``term`` for terminal output.

You can also run tests per subpackage of novelWriter with the ``-m`` command. The available
subpackage groups are ``base``, ``core``, and ``gui``. Consider for instance:

.. code-block:: console

   xvfb-run pytest -v --cov=novelwriter --cov-report=html -m core

This will only run the tests of the "core" package, that is, all the classes that deal with the
project data of a novelWriter project. The "gui" tests, likewise, will run the tests for the GUI
components, and the "base" tests cover the bits in-between.

You can also filter the tests with the ``-k`` switch. The following will do the same as
``-m core``:

.. code-block:: console

   xvfb-run pytest -v --cov=novelwriter --cov-report=html -k testCore

All tests are named in such a way that you can filter them by adding more bits of the test names.
They all start with the word "test". Then comes the group: "Core", "Base", "Dlg", "Tool", or "Gui".
Finally comes the name of the class or module, which generally corresponds to a single source code
file. For instance, running the following will run all tests for the document editor:

.. code-block:: console

   xvfb-run pytest -v --cov=novelwriter --cov-report=html -k testGuiEditor

To run a single test, simply add the full test name to the ``-k`` switch.
