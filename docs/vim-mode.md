# Vim mode

Vim is a keyboard-centric text editor. A vim mode refers
to another editor implementing the ability to perform
a subset of vim motions. This will allow you to write,
select, edit, copy, paste, navigate, etc, efficiently
all by using your keyboard.


Vim is modal, three such modes have been implemented
in NovelWriter:
- Normal mode: this is the default mode used to navigate text
- Insert mode: where you can write text as in a 'normal' text editor
- Visual mode: for selecting text
    - Visual mode: per character selection
    - V-line mode: per line selection

## Mode switching

To switch between the various vim modes there are these
keystrokes implemented (definitions provided below):

Normal mode -> Insert mode: 
    - i, I, a, A, o, O
Insert mode -> Normal mode:
    - ESC (escape key)
Normal mode -> Visual mode:
    - v, V

You can exit visual mode back to normal mode by pressing
escape, but all visual mode commands that logically 
'terminate' the visual mode usage will return you to 
normal mode.
E.g: press "V" to enter V-line mode, select next word with "w"
press "y" to yank (copy), you are now automatically put
back in normal mode as you have completed selecting your text.

## Implemented keystrokes (vim motions)

This table shows the vim motions currently implemented in NovelWriter:

| Motion | Mode(s) | Description |
|--------|---------|-------------|
| `i` | Normal → Insert | Enter insert mode |
| `I` | Normal → Insert | Jump to first non-blank of line and enter insert |
| `v` | Normal → Visual | Enter character-wise visual mode |
| `V` | Normal → V-Line | Enter line-wise visual mode |
| `dd` | Normal | Delete (cut) current line |
| `x` | Normal | Delete character under cursor |
| `w` | Normal / Visual | Move to next word start |
| `b` | Normal / Visual | Move to previous word start |
| `e` | Normal / Visual | Move to next word end |
| `dw` | Normal | Delete from cursor to next word start |
| `yw` | Normal | Yank (copy) from cursor to next word start |
| `gg` | Normal / Visual | Jump to first line |
| `G` | Normal / Visual | Jump to last line |
| `yy` | Normal | Yank current line |
| `p` | Normal | Paste after current line |
| `P` | Normal | Paste before current line |
| `o` | Normal → Insert | Open new line below and enter insert |
| `O` | Normal → Insert | Open new line above and enter insert |
| `$` | Normal / Visual | Move to end of line |
| `a` | Normal → Insert | Enter insert after cursor |
| `A` | Normal → Insert | Enter insert at end of line |
| `u` | Normal | Undo last change |
| `zz` | Normal | Center cursor vertically |
| `h` | Normal / Visual | Move left |
| `j` | Normal / Visual | Move down |
| `k` | Normal / Visual | Move up |
| `l` | Normal / Visual | Move right |
| `d` / `x` | Visual / V-Line | Delete selection |
| `y` | Visual / V-Line | Yank selection |
| `0` | Visual | Move to start of line (extend selection) |

### Known bugs 

Currently "dd" on an empty line will no delete, but using "x" will.

vypyy" will have ypyy in command and thus not register yy.
Expected behavior would be visual mode, yank, paste, yank line.
This could be fixed by having a list of suffixes potentially.


### Useful commands not yet added:
- r, R : replace text
- c : change, delete and enter insert mode
- ciw : change in word, to "vedi", select current word, delete, then 
enter insert mode.
