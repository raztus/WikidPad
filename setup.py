# setup.py
from distutils.core import setup
import os
from glob import glob
try:
    import py2exe
except ImportError:
    print("This setup.py file is solely made for building the Windows binary")
    print("")
    raise
from py2exe.runtime import Target


wikidpad = Target(
    # used for the versioninfo resource
    version = '2.4',
    name = 'WikidPad',
    copyright = '(C) 2005-2018 Michael Butscher, Jason Horman, Gerhard Reitmayr',
    description = 'Single user wiki notepad',
    comments='',

    # what to build
    script = 'WikidPad.py',
    icon_resources = [(0, 'icons/pwiki.ico'), (1, 'icons/pwiki.ico')]
)


excludes = ["win32api", "win32con", "win32pipe", "gadfly"]

setup(
    options = {"py2exe": {"compressed": 1,
                         "exeoptimize": 1, # Opt.mode of the exe stub
                          "optimize": 2,  # Opt.mode for compiling library.zip
                          ## "ascii": 1,
                          "excludes": excludes,
                          "dll_excludes": ["msvcp90.dll"]}},

    name='WikidPad',
    version = '2.4',
    author = 'Michael Butscher',
    author_email = 'mbutscher@gmx.de',
    url = 'http://www.mbutscher.de/software.html',
    ## scripts=['WikidPad.py'],
    windows = [wikidpad],
#     console = [wikidpad],
    package_dir = {'': 'lib'},
    packages = ['pwiki', 'pwiki.wikidata', 'pwiki.wikidata.compact_sqlite',
              'pwiki.wikidata.original_sqlite', 'pwiki.timeView',
              'pwiki.rtlibRepl'],
    # py_modules=['encodings.utf_8', 'encodings.latin_1'],
    data_files = [('icons', glob(os.path.join('icons', '*.*'))),
#                 ('lib', glob('sql_mar.*')),
          ('extensions', glob('extensions/*.*')),
          ('extensions/wikidPadParser', glob('extensions/wikidPadParser/*.*')),
          ('extensions/mediaWikiParser', glob('extensions/mediaWikiParser/*.*')),
          ('', ['sqlite3.dll', 'WikidPad.xrc', 'langlist.txt',
              'appbase.css'] + glob('WikidPad_*.po')),
          ('WikidPadHelp', glob(os.path.join('WikidPadHelp', '*.wiki'))),
          (os.path.join('WikidPadHelp', 'data'),
              glob(os.path.join('WikidPadHelp', 'data', '*.*'))),
          (os.path.join('WikidPadHelp', 'files'),
              glob(os.path.join('WikidPadHelp', 'files', '*.*'))),
          ('export', [])]
)
