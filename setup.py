#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup, Command


class PyTest(Command):
    description=""" Test command for pytest """
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys, subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(name='pdfcompare',
      version='1.0',
      description='Compare two PDF files',
      author='Jürgen Weigert',
      author_email='jw@suse.de',
      url='https://github.com/jnweiger/pdfcompare',
      scripts=['pdf_highlight.py', 'imgcmp.py'],
      license='GPL-2.0',
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Environment :: Console',
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
                  ],
      cmdclass={'test': PyTest},
      long_description="".join(open('README.txt').readlines()),
      tests_require=['pytest', 'scipy'],
      #packages=['pyPdf','reportlab.pdfgen','reportlab.lib.colors','pygame.font' ],
# 
     )
