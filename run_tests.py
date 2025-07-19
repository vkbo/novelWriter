#!/usr/bin/env python3
"""Run novelWriter Tests."""

import argparse
import os
import subprocess
import sys

if __name__ == "__main__":
    """Parse command line options and run the commands."""
    parser = argparse.ArgumentParser(usage="run_tests.py [--flags]")
    parser.add_argument("-o", action="store_true", help="Run off screen")
    parser.add_argument("-r", action="store_true", help="Generate reports")
    parser.add_argument("-t", action="store_true", help="Generate terminal report")
    parser.add_argument("-m", help="Test modules")
    parser.add_argument("-k", help="Test filters")

    args = parser.parse_args()

    env = os.environ.copy()
    cmd = [sys.executable, "-m", "pytest", "-vv"]

    if args.o:
        env["QT_QPA_PLATFORM"] = "offscreen"
    if args.r or args.t:
        cmd += ["--cov=novelwriter"]
    if args.r:
        cmd += ["--cov-report=xml", "--cov-report=html"]
    if args.t:
        cmd += ["--cov-report=term"]
    if args.m:
        cmd += ["-m", args.m]
    if args.k:
        cmd += ["-k", args.k]

    print("Calling:", " ".join(cmd))
    subprocess.call(cmd, env=env)
