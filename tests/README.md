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

The `--cov-report` switch generates an html report, omit it to print a coverage summary to the
terminal. The html coverage report will be available in the `htmlcov` folder.

### Test Markers (Categories)

To run with specific test markers, add the `-m` switch:
```bash
pytest-3 -v -m core
```

Available markers are:

* `base` for unit tests covering the non-gui classes of the `bw` folder..
* `core` for unit tests covering the classes in the `nw/core` folder.
* `gui` for unit and integrations tests covering the classes in the `nw/gui` folder.

## Tests

To filter specific groups of tests, use the `-k` switch.
The commands for the respective test categories are listed below.

| Type        | Test Target              | Source File(s)         | Marker    | Filter                   |
| :---------- | :----------------------- | :--------------------- | :-------- | :----------------------- |
| Unit        | Main function            | nw/\_\_init\_\_.py     | `-m base` | `-k testBaseInit`        |
| Unit        | Common functions         | nw/common.py           | `-m base` | `-k testBaseCommon`      |
| Unit        | Config class             | nw/config.py           | `-m base` | `-k testBaseConfig`      |
| Unit        | Error handlers           | nw/error.py            | `-m base` | `-k testBaseError`       |
| Unit        | Core functions           | nw/core/tools.py       | `-m core` | `-k testCoreTools`       |
| Unit        | NWDoc class              | nw/core/document.py    | `-m core` | `-k testCoreDocument`    |
| Unit        | NWIndex class            | nw/core/index.py       | `-m core` | `-k testCoreIndex`       |
| Unit        | NWItem class             | nw/core/item.py        | `-m core` | `-k testCoreItem`        |
| Unit        | NWProject class          | nw/core/project.py     | `-m core` | `-k testCoreProject`     |
| Unit        | NWSpell* classes         | nw/core/spellcheck.py  | `-m core` | `-k testCoreSpell`       |
| Unit        | NWStatus class           | nw/core/status.py      | `-m core` | `-k testCoreStatus`      |
| Unit        | NWTree class             | nw/core/tree.py        | `-m core` | `-k testCoreTree`        |
| Unit        | OptionsState class       | nw/core/options.py     | `-m core` | `-k testCoreOptions`     |
| Unit        | ToHtml class             | nw/core/tohtml.py      | `-m core` | `-k testCoreToHtml`      |
| Unit        | Tokenizer class          | nw/core/tokenizer.py   | `-m core` | `-k testCoreToken`       |
| Integration | About Dialogs            | nw/gui/about.py        | `-m gui`  | `-k testGuiAbout`        |
| Integration | Build Novel Project Tool | nw/gui/build.py        | `-m gui`  | `-k testGuiBuild`        |
| Integration | Document Editor Widget   | nw/gui/doceditor.py    | `-m gui`  | `-k testGuiEditor`       |
| Integration | Document Viewer Widget   | nw/gui/docviewer.py    | `-m gui`  | `-k testGuiViewer`       |
| Integration | Item Editor Dialog       | nw/gui/itemeditor.py   | `-m gui`  | `-k testGuiItemEditor`   |
| Integration | Menu Widgets             | nw/gui/mainmenu.py     | `-m gui`  | `-k testGuiMenu`         |
| Integration | Merge Tool               | nw/gui/docmerge.py     | `-m gui`  | `-k testGuiMergeSplit`   |
| Integration | Outline Widget           | nw/gui/outline.py      | `-m gui`  | `-k testGuiOutline`      |
| Integration | Preferences Dialog       | nw/gui/preferences.py  | `-m gui`  | `-k testGuiPreferences`  |
| Integration | Project Load Dialog      | nw/gui/projload.py     | `-m gui`  | `-k testGuiProjLoad`     |
| Integration | Project Settings Dialog  | nw/gui/projsettings.py | `-m gui`  | `-k testGuiProjSettings` |
| Integration | Project Tree Widget      | nw/gui/projtree.py     | `-m gui`  | `-k testGuiProjTree`     |
| Integration | Theme/Icon Classes       | nw/gui/theme.py        | `-m gui`  | `-k testGuiTheme`        |
| Integration | Split Tool               | nw/gui/docsplit.py     | `-m gui`  | `-k testGuiMergeSplit`   |
| Integration | Writing Stats Dialog     | nw/gui/writingstats.py | `-m gui`  | `-k testGuiWritingStats` |
| Integration | Various Dialogs          | N/A                    | `-m gui`  | `-k testGuiDialogs`      |
