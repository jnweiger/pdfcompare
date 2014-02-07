#!/usr/bin/python 
# -*- coding: utf-8 -*-

import os.path


def test_version():
         """
         Checks, if version number in last line of help output is available
         """
         import subprocess 
         L=subprocess.check_output(['./pdf_highlight.py','-h'])
         L=L.strip()
         LL=L.split("\n")
         assert 'version' in LL[-1]



def test_pdfcompare_exists():
         assert os.path.exists('pdf_highlight.py')


