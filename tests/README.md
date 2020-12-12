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
pytest-3 -v --cov=nw --cov-report=html
```

The `--cov-report` switch generates an html report, omit it to print a coverage summary to the terminal.
The html coverage report will be available in the `htmlcov` folder.

### Test Markers (Categories)

To run with specific test markers, add the `-m` switch:
```bash
pytest-3 -v -m core
```

Available markers are:

* '`core`' for unit tests covering the classes in the `nw/core` folder

## Tests

To filter specific groups of tests, use the `-k` switch.
The commands for the respective test categories are listed below.

| Type        | Test Target        | Source File(s)         | Marker    | Filter                   |
| :---------- | :----------------- | :--------------------- | :-------- | :----------------------- |
| Unit        | Main function      | nw/\_\_init\_\_.py     | `-m base` | `-k testBaseInit`        |
| Unit        | Common functions   | nw/common.py           | `-m base` | `-k testBaseCommon`      |
| Unit        | Config class       | nw/config.py           | `-m base` | `-k testBaseConfig`      |
| Unit        | Error handlers     | nw/error.py            | `-m base` | `-k testBaseError`       |
| Unit        | Core functions     | nw/core/tools.py       | `-m core` | `-k testCoreTools`       |
| Unit        | NWDoc class        | nw/core/document.py    | `-m core` | `-k testCoreDocument`    |
| Unit        | NWIndex class      | nw/core/index.py       | `-m core` | `-k testCoreIndex`       |
| Unit        | NWItem class       | nw/core/item.py        | `-m core` | `-k testCoreItem`        |
| Unit        | NWProject class    | nw/core/project.py     | `-m core` | `-k testCoreProject`     |
| Unit        | NWSpell* classes   | nw/core/spellcheck.py  | `-m core` | `-k testCoreSpell`       |
| Unit        | NWStatus class     | nw/core/status.py      | `-m core` | `-k testCoreStatus`      |
| Unit        | NWTree class       | nw/core/tree.py        | `-m core` | `-k testCoreTree`        |
| Unit        | OptionsState class | nw/core/options.py     | `-m core` | `-k testCoreOptions`     |
| Unit        | ToHtml class       | nw/core/tohtml.py      | `-m core` | `-k testCoreToHtml`      |
| Unit        | Tokenizer class    | nw/core/tokenizer.py   | `-m core` | `-k testCoreToken`       |
| Integration | Writing Stats GUI  | nw/gui/writingstats.py | `-m gui`  | `-k testGuiWritingStats` |
