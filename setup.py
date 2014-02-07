#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys 

from distutils.core import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


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
