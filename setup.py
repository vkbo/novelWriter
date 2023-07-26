#!/usr/bin/env python3

import setuptools  # noqa: F401
import warnings  # noqa: F401

warnings.warn(
    "The setuptools style setup.py script is deprecated and will be "
    "removed in a future release. Please don't use the 'setup.py install' "
    "command, and instead use the pip and build commands.",
    DeprecationWarning
)

setuptools.setup()
