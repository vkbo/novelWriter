Name:           novelwriter
Version:        2.7
Release:        %autorelease
Summary:        Plain text editor designed for writing novels

# Code is GPL-3.0-or-later, icons are CC-BY-SA-4.0
License:        GPL-3.0-or-later AND CC-BY-SA-4.0 
URL:            https://novelwriter.io/
Source:         https://github.com/vkbo/novelwriter/archive/v%{version}/novelwriter-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  adobe-source-sans-pro-fonts
BuildRequires:  hunspell-en
BuildRequires:  hunspell-en-GB
BuildRequires:  hunspell-en-US
BuildRequires:  enchant2-devel
BuildRequires:  hunspell-devel
BuildRequires:  libreoffice
BuildRequires:  python3-enchant
BuildRequires:  python3-zlib-ng
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  python3-devel

BuildRequires: libappstream-glib
BuildRequires: desktop-file-utils

# Test requirements
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(pytest-qt)
BuildRequires:  python3dist(pytest-xvfb)
# Documentation requirements
BuildRequires:  python3dist(docutils)
BuildRequires:  python3dist(sphinx)
# Generate DocBook for internal documentation
BuildRequires:  python3-sphinx-design
BuildRequires:  python3-sphinx-copybutton
BuildRequires:  texinfo
# Needed for directory ownership
Requires:       hicolor-icon-theme

%description
novelWriter is a plain text editor designed for writing novels assembled from
many smaller text documents. It uses a minimal formatting syntax inspired by
Markdown, and adds a meta data syntax for comments, synopsis, and
cross-referencing. It's designed to be a simple text editor that allows for
easy organization of text and notes, using human readable text files as
storage for robustness.

The project storage is suitable for version control software, and also well
suited for file synchronization tools. All text is saved as plain text files
with a meta data header. The core project structure is stored in a single
project XML file. Other meta data is primarily saved as JSON files.

%package doc
Summary: Documentation for novelWriter

BuildArch:  noarch

%description doc
Documentation for novelWriter in docbook format. 

%prep
%autosetup -n novelWriter-%{version} -p1
# https://github.com/vkbo/novelWriter/issues/2276
sed -i 's/self.spellLanguage = "en"/self.spellLanguage = "en_US"/g' novelwriter/config.py
sed -i 's/spellcheck = en/spellcheck = en_US/g' tests/reference/baseConfig_novelwriter.conf
# Use Fedora specific variant for qt6
sed -i 's/"lrelease"/"lrelease-qt6"/g' utils/assets.py

%generate_buildrequires
%pyproject_buildrequires

%build
# Build translations
%python3 pkgutils.py qtlrelease
# Build sample
%python3 pkgutils.py sample
# Build documentation
pushd docs
sphinx-build source texinfo -b texinfo
pushd texinfo
makeinfo --docbook novelwriter.texi
popd
popd
# Build package
%pyproject_wheel

%install
%pyproject_install
# Do not include this for now as .qm language files are not automatically marked
#pyproject_save_files novelwriter

desktop-file-install --dir=%{buildroot}%{_datadir}/applications setup/data/novelwriter.desktop
mkdir -p %{buildroot}%{_metainfodir}/
install -m644 setup/novelwriter.appdata.xml %{buildroot}%{_metainfodir}/
mkdir -p %{buildroot}%{_datadir}/icons
cp -r -p setup/data/hicolor %{buildroot}%{_datadir}/icons/
install -pDm0644 docs/texinfo/novelwriter.xml \
  %{buildroot}%{_datadir}/help/en/novelwriter/novelwriter.xml
for file in docs/texinfo/novelwriter-figures/*.*
do
  install -pDm0644 $file \
  %{buildroot}%{_datadir}/help/en/novelwriter/novelwriter-figures/$(basename $file)
done

%find_lang nw --with-qt

%check
QT_QPA_PLATFORM=offscreen %pytest
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/novelwriter.appdata.xml

# Include once qm files get marked as language files
#files -n novelwriter -f %%{pyproject_files} -f nw.lang
%files -n novelwriter -f nw.lang
%license LICENSE.md
%doc README.md
%{_bindir}/novelwriter
%{python3_sitelib}/novelwriter-%{version}.dist-info/
%dir %{python3_sitelib}/novelwriter
%dir %{python3_sitelib}/novelwriter/assets
%dir %{python3_sitelib}/novelwriter/assets/i18n
%{python3_sitelib}/novelwriter/assets/i18n/*.json
%{python3_sitelib}/novelwriter/assets/icons/
%{python3_sitelib}/novelwriter/assets/images/
%{python3_sitelib}/novelwriter/assets/sample.zip
%{python3_sitelib}/novelwriter/assets/syntax/
%{python3_sitelib}/novelwriter/assets/text/
%{python3_sitelib}/novelwriter/assets/themes/
%pycached %{python3_sitelib}/novelwriter/*.py
%dir  %{python3_sitelib}/novelwriter/__pycache__
%{python3_sitelib}/novelwriter/core/
%{python3_sitelib}/novelwriter/dialogs/
%{python3_sitelib}/novelwriter/extensions/
%{python3_sitelib}/novelwriter/formats/
%{python3_sitelib}/novelwriter/gui/
%{python3_sitelib}/novelwriter/text/
%{python3_sitelib}/novelwriter/tools/
%{_datadir}/applications/novelwriter.desktop
%{_metainfodir}/novelwriter.appdata.xml
%{_datadir}/icons/hicolor/*/apps/*.png
%{_datadir}/icons/hicolor/*/mimetypes/*.png
%{_datadir}/icons/hicolor/*/apps/*.svg
%{_datadir}/icons/hicolor/*/mimetypes/*.svg

%files doc
%license LICENSE.md
%dir  %{_datadir}/help/en
%lang(en) %{_datadir}/help/en/novelwriter

%changelog
%autochangelog
