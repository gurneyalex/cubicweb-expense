# pylint: disable-msg=W0622
"""cubicweb-expense application packaging information"""

modname = 'expense'
distname = 'cubicweb-expense'

numversion = (0, 6, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2008-2010 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''

author = 'Logilab'
author_email = 'contact@logilab.fr'

short_desc = 'expense component for the CubicWeb framework'
long_desc = '''This CubicWeb component models expenses (usable to implement
expense tracking application).

CubicWeb is a semantic web application framework, see http://www.cubicweb.org
'''

ftp = ''
web = 'http://www.cubicweb.org/project/%s' % distname

pyversions = ['2.4']

classifiers = [
           'Environment :: Web Environment',
           'Framework :: CubicWeb',
           'Programming Language :: Python',
           'Programming Language :: JavaScript',
]

__depends_cubes__ = {'addressbook': None}
__depends__ = {'cubicweb': '>= 3.6.0'}
for key, value in __depends_cubes__.items():
    __depends__['cubicweb-'+key] = value
__use__ = tuple(__depends_cubes__)
__recommend__ = ()

from glob import glob
from os import listdir as _listdir
from os.path import join, isdir

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
