"""
novelWriter – Material Icon Theme
=================================

This file is a part of novelWriter
Copyright (C) 2025 Veronica Berglyd Olsen and novelWriter contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

import subprocess

from pathlib import Path

from lxml import etree

MATERIAL_REPO = "https://github.com/google/material-design-icons.git"
ICON_MAP = {
    "alert_error": "error",
    "alert_info": "info",
    "alert_question": "help",
    "alert_warn": "warning",

    "cls_archive": "archive",
    "cls_character": "group",
    "cls_custom": "label",
    "cls_entity": "apartment",
    "cls_none": "close",
    "cls_novel": "book_2",
    "cls_object": "key",
    "cls_plot": "extension",
    "cls_template": "topic",
    "cls_timeline": "hourglass_empty",
    "cls_trash": "delete",
    "cls_world": "globe",

    "prj_folder": "folder",
    "prj_document": "news",
    "prj_title": "news",
    "prj_chapter": "news",
    "prj_scene": "news",
    "prj_note": "sticky_note_2",

    "fmt_bold": "format_bold",
    "fmt_italic": "format_italic",
    "fmt_mark": "format_ink_highlighter",
    "fmt_strike": "strikethrough_s",
    "fmt_subscript": "subscript",
    "fmt_superscript": "superscript",
    "fmt_underline": "format_underlined",
    "fmt_toolbar": "text_format",

    "search": "search",
    "search_cancel": "close",
    "search_case": "match_case",
    "search_loop": "laps",
    "search_preserve": "text_fields",
    "search_project": "document_search",
    "search_regex": "regular_expression",
    "search_replace": "find_replace",
    "search_word": "match_word",

    "bullet-off": "radio_button_unchecked",
    "bullet-on": "radio_button_checked",
    "unfold-hide": "arrow_right",
    "unfold-show": "arrow_drop_down",

    "add": "add",
    "bookmarks": "bookmarks",
    "browse": "folder_open",
    "cancel": "cancel",
    "checked": "check_box",
    "chevron_down": "keyboard_arrow_down",
    "chevron_left": "arrow_back_ios",
    "chevron_right": "arrow_forward_ios",
    "chevron_up": "keyboard_arrow_up",
    "close": "close",
    "copy": "content_copy",
    "document_add": "note_add",
    "document": "docs",
    "edit": "edit",
    "exclude": "do_not_disturb_on",
    "export": "file_export",
    "filter": "filter_alt",
    "fit_height": "fit_page_height",
    "fit_width": "fit_page_width",
    "folder": "folder",
    "font": "font_download",
    "import": "tab_move",
    "language": "translate",
    "lines": "reorder",
    "list": "format_list_bulleted",
    "manuscript": "export_notes",
    "margin_bottom": "vertical_align_bottom",
    "margin_left": "keyboard_tab_rtl",
    "margin_right": "keyboard_tab",
    "margin_top": "vertical_align_top",
    "maximise": "fullscreen",
    "minimise": "fullscreen_exit",
    "more_arrow": "arrow_right",
    "more_vertical": "more_vert",
    "noncheckable": "indeterminate_check_box",
    "novel_view": "book_4_spark",
    "open": "open_in_new",
    "outline": "summarize",
    "panel": "dock_to_bottom",
    "pin": "keep",
    "project_copy": "folder_copy",
    "project_view": "bookmark_manager",
    "quote": "format_quote",
    "refresh": "refresh",
    "remove": "remove",
    "revert": "settings_backup_restore",
    "settings": "settings",
    "star": "star",
    "stats": "bar_chart",
    "text": "subject",
    "timer_off": "timer_off",
    "timer": "timer",
    "unchecked": "disabled_by_default",
    "view": "visibility",
}


def _fixXml(svg: str) -> str:
    """Clean up the SVG XML and add needed fields."""
    xSvg = etree.fromstring(svg)  # type: ignore
    xSvg.set("fill", "#000000")
    xSvg.set("height", "128")
    xSvg.set("width", "128")
    return etree.tostring(xSvg).decode()


def processMaterialIcons(workDir: Path, iconsDir: Path, jobs: dict) -> None:
    """Process material icons of a given spec and write output file."""
    srcRepo = workDir / "material-design-icons"
    if not srcRepo.is_dir():
        subprocess.call(["git", "clone", MATERIAL_REPO, "--depth", "50"], cwd=workDir)
    else:
        subprocess.call(["git", "pull"], cwd=srcRepo)

    for file, job in jobs.items():
        name: str    = job["name"]
        style: str   = job["style"]
        filled: bool = job["filled"]
        weight: int  = job["weight"]

        kind = f"wght{weight}" if weight != 400 else ""
        kind += "fill1" if filled else ""

        print("")
        print(f"Processing: {name}")
        print("")
        with open(iconsDir / f"{file}.icons", mode="w", encoding="utf-8") as icons:
            icons.write("# This file is automatically generated. Do not edit.\n\n")
            icons.write("# Meta\n")
            icons.write(f"meta:name    = {name}\n")
            icons.write("meta:author  = Google Inc\n")
            icons.write("meta:license = Apache 2.0\n")
            icons.write("\n")
            icons.write("# Icons\n")
            iconSrc = srcRepo / "symbols" / "web"
            for key, icon in ICON_MAP.items():
                if kind:
                    fileNmae = f"{icon}_{kind}_24px.svg"
                else:
                    fileNmae = f"{icon}_24px.svg"
                iconFile = iconSrc / icon / f"materialsymbols{style}" / fileNmae
                if iconFile.is_file():
                    svg = iconFile.read_text(encoding="utf-8")
                    icons.write(f"icon:{key:<15s} = {_fixXml(svg)}\n")
                    print(f"Wrote: {iconFile.stem}")
                else:
                    print(f"Not Found: {iconFile}")
