import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

SETTINGS = {
    "MACOSX_BUNDLE_COPYRIGHT": "© 2018–2022, Veronica Berglyd Olsen <code@vkbo.net>",
    "MACOSX_BUNDLE_IDENTIFIER": "io.novelwriter.novelWriter",
    "MACOSX_BUNDLE_NAME": "novelWriter",
    "MACOSX_BUNDLE_EXACUTABLE_NAME": "novelwriter",
    "MACOSX_BUNDLE_ICON_FILE": "novelwriter.icns",
    "MACOSX_BUNDLE_INFO_STRING": "novelWriter: A markdown-like text editor for planning and writing novels.",
    "MACOSX_BUNDLE_SHORT_VERSION": "2.0.1",  # Must be purely numerical
    "MACOSX_BUNDLE_VERSION": "2.0.1", # Must be purely numerical
}

if __name__ == "__main__":

    template_filename = os.path.join(SCRIPT_DIR, "Info.plist.in")
    with open(template_filename, "r") as tmfile:
        template = tmfile.read()

    plist = template.format(**SETTINGS)

    plist_filename = os.path.join(SCRIPT_DIR, "Info.plist")
    with open(plist_filename, "w") as plistfile:
        plistfile.write(plist)
