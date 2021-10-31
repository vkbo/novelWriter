# Copyright (c) 2021 Riverbank Computing Limited <info@riverbankcomputing.com>
#
# This file is part of PyQt6.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
#
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


import fnmatch
import os

# from .designer_source import DesignerSource
from .python_source import PythonSource
from .translation_file import TranslationFile
from .user import UserException


def lupdate(
    sources, translation_files, no_obsolete=False, no_summary=True, verbose=False, excludes=None
):
    """ Update a sequence of translation (.ts) files from a sequence of Python
    source (.py) files, Designer source (.ui) files or directories containing
    source files.
    """

    if excludes is None:
        excludes = ()

    # Read the .ts files.
    translations = [
        TranslationFile(ts, no_obsolete=no_obsolete, no_summary=no_summary, verbose=verbose)
        for ts in translation_files
    ]

    # Read the sources.
    source_files = []
    for source in sources:
        if os.path.isdir(source):
            for dirpath, _, filenames in os.walk(source):
                for fn in filenames:
                    # Apply any exclusion patterns.
                    for exclude in excludes:
                        if fnmatch.fnmatch(fn, exclude):
                            fn = None
                            break

                    if fn is None:
                        continue

                    filename = os.path.join(dirpath, fn)

                    if filename.endswith('.py'):
                        source_files.append(PythonSource(filename=filename, verbose=verbose))

                    # UI file support is disabled
                    # elif filename.endswith('.ui'):
                    #     source_files.append(
                    #             DesignerSource(filename=filename,
                    #                     verbose=verbose))

                    elif verbose:
                        print("Ignoring", filename)

        elif source.endswith('.py'):
            source_files.append(PythonSource(filename=source, verbose=verbose))

        # UI file support is disabled
        # elif source.endswith('.ui'):
        #     source_files.append(
        #             DesignerSource(filename=source, verbose=verbose))

        else:
            raise UserException("{0} must be a directory or a .py or a .ui file".format(source))

    # Update each translation for each source.
    for t in translations:
        for s in source_files:
            t.update(s)

        t.write()
