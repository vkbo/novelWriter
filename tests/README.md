# novelWriter Tests

The test suite uses PyTest for testing.

## Dependencies

* `python3-pytest` for the basic framework (required)
* `python3-pytestqt` for Qt support (required)
* `python3-pytest-cov` for code coverage reports (optional)
* `python3-pytest-xvfb` for headless tests (optional)

## HowTo

### Basic Usage

To run all tests, type:
```bash
pytest-3 -v
```

The `-v` switch enables verbose mode, with one test per line.
For a more compact view, omit this switch.

### Headless

To run tests in headless mode, either use the Qt `offscreen` mode:
```bash
export QT_QPA_PLATFORM=offscreen
```

or run with `xvfb`:
```bash
xvfb-run pytest-3 -v
```

### Test Coverage

To add test coverage, run the following:
```bash
pytest-3 -v --cov=novelwriter --cov-report=html
```

The `--cov-report` switch generates an html report, omit it to print a coverage summary to the
terminal. The html coverage report will be available in the `htmlcov` folder.

### Test Markers (Categories)

To run with specific test markers, add the `-m` switch:
```bash
pytest-3 -v -m core
```

Available markers are:

* `base` for unit tests covering the non-gui classes of the `novelwriter` folder..
* `core` for unit tests covering the classes in the `novelwriter/core` folder.
* `gui` for unit and integrations tests covering the classes in the `novelwriter/gui` folder.


You can filter tests further with the `-k` switch, all the way down to a single test. You can for
instance run only dialog tests with `-k testDlg` or tools with `-k testTool`.
