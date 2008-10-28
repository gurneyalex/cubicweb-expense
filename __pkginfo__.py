# pylint: disable-msg=W0622
"""cubicweb-expense application packaging information"""

distname = 'cubicweb-expense'

numversion = (0, 2, 4)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2008 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = 'Logilab'
author_email = 'contact@logilab.fr'

short_desc = 'cubicweb expense component'
long_desc = '''defines the expense schema plus some basic operations'''

from os import listdir as _listdir
from os.path import join, isdir

from glob import glob
scripts = glob(join('bin', 'expense-*'))

web, ftp = '', ''

pyversions = ['2.4']

#from cubicweb.devtools.pkginfo import get_distutils_datafiles
CUBES_DIR = join('share', 'cubicweb', 'cubes')
THIS_CUBE_DIR = join(CUBES_DIR, 'expense')

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')]

def include(dirname):
    return [join(THIS_CUBE_DIR, dirname),  listdir(dirname)]
    
try:
    data_files = [
        # common files
        [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],

        # client (web) files
        include('data'),
        include('i18n'),
        include('pdfgen'),
        # Note: here, you'll need to add views' subdirectories if you want
        # them to be included in the debian package
        
        # server files
        include('migration'),
        ]
except OSError:
    # we are in an installed directory
    pass

cube_eid = None # <=== FIXME if you need direct bug-subscription
__use__ = ('addressbook',)

