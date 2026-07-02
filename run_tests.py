#!/usr/bin/env python3
"""Run novelWriter Tests."""  # noqa: CPY001

import argparse
import os
import shlex
import subprocess
import sys

from pathlib import Path


def _genCoverageConfig(path: Path) -> None:
    """Generate a config file for coverage.py."""
    exclude = []  # ["if TYPE_CHECKING:"]
    if sys.platform != "linux":
        exclude.append(r'\s*(if|elif) sys\.platform == "linux":')
        exclude.append(r"\s*(if|elif) (CONFIG|self)\.osLinux")
    if sys.platform != "darwin":
        exclude.append(r'\s*(if|elif) sys\.platform == "darwin":')
        exclude.append(r"\s*(if|elif) (CONFIG|self)\.osDarwin")
    if sys.platform != "win32":
        exclude.append(r'\s*(if|elif) sys\.platform == "win32":')
        exclude.append(r"\s*(if|elif) (CONFIG|self)\.osWindows")

    config = [
        "[run]",
        "branch = false",
        "source = novelwriter",
        "",
        "[report]",
        "precision = 2",
        "exclude_also =",
    ]
    config.extend(f"    {ex}" for ex in exclude)

    path.write_text("\n".join(config), encoding="utf-8")


if __name__ == "__main__":
    """Parse command line options and run the commands."""
    parser = argparse.ArgumentParser(usage="run_tests.py [--flags]")
    parser.add_argument("-o", action="store_true", help="Run off screen")
    parser.add_argument("-r", action="store_true", help="Generate reports")
    parser.add_argument("-t", action="store_true", help="Generate terminal report")
    parser.add_argument("-u", action="store_true", help="Generate uncovered terminal report")
    parser.add_argument("-x", action="store_true", help="Ignore OS-specific tests in reports")
    parser.add_argument("-lf", action="store_true", help="Re-run failed tests")
    parser.add_argument("-sw", action="store_true", help="Run tests stepwise")
    parser.add_argument("-m", help="Test modules", metavar="MARKEXPR")
    parser.add_argument("-k", help="Test filters", metavar="EXPRESSION")

    args = parser.parse_args()

    env = os.environ.copy()
    env["QT_SCALE_FACTOR"] = "1.0"
    tmpConf = Path(__file__).parent / ".coveragerc"

    if args.r or args.t or args.u:
        if args.x:
            _genCoverageConfig(tmpConf)
        cmd = ["coverage", "run"]
        if args.lf or args.sw:
            cmd += ["--append"]
        cmd += ["-m"]
    else:
        cmd = [sys.executable, "-m"]

    cmd += ["pytest", "-vv"]
    if args.o:
        env["QT_QPA_PLATFORM"] = "offscreen"
    if args.lf:
        cmd += ["--last-failed"]
    if args.sw:
        cmd += ["--stepwise"]
    if args.m:
        cmd += ["-m", args.m]
    if args.k:
        cmd += ["-k", args.k]

    print("Calling:", shlex.join(cmd))
    subprocess.call(cmd, env=env)

    if args.r:
        subprocess.call(["coverage", "xml"])
        subprocess.call(["coverage", "html"])
    if args.t and not args.u:
        subprocess.call(["coverage", "report"])
    if args.u:
        subprocess.call(["coverage", "report", "--skip-covered"])

    tmpConf.unlink(missing_ok=True)
