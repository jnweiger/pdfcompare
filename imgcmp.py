#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# compare two images using Scipy
# (c) 2013 - jw@suse.de - distributer under GPL-2.0 or ask.
#
# Dependencies:
# sudo zypper in python-scipy
# sudo zypper in ImageMagick
#
# See also python-pHash, and python-opencv
# http://stackoverflow.com/questions/13379909/compare-similarity-of-images-using-opencv-with-python

from __future__ import print_function, division

import sys, os, re, tempfile
from pprint import pprint

import scipy as sp
from scipy.misc import imread
from scipy.signal.signaltools import correlate2d as c2d


class CompareImageException(Exception):
     """
     Exception class for comparing two files 
     """
     def __init__(self, c11, c12, c22):
         self.c11=c11
         self.c12=c12
         self.c22=c22
     def __repr__(self):
          return "(%.2f %.2f %.2f)" % (self.c11, self.c12, self.c22)
     __str__=__repr__


def load_img(fname):
     """
     Load and convert images
     """
     # get JPG image as Scipy array, RGB (3 layer)
     if re.search("\.pdf$", fname, re.I):
       # convert PDF to JPG
       tf = tempfile.NamedTemporaryFile(delete=True, suffix=".jpg")
       print("creating %s" % tf.name)
       os.system("convert '%s[0]' -geometry 100x100 '%s'" % (fname, tf.name))
       data = imread(tf.name)
       tf.close()
     else:
       data = imread(fname)
     # convert to grey-scale using W3C luminance calc
     ## pprint([data])
     ## ValueError: matrices are not aligned, if alpha channel...
     lum = [299, 587, 114]
     if len(data[0][0]) > 3:
       lum.append(0)
     data = sp.inner(data, lum) / 1000.0
     # normalize per http://en.wikipedia.org/wiki/Cross-correlation
     return (data - data.mean()) / data.std()


def compare(file1, file2, diff):
     """
     Compares two files (JPEG, PNG or PDF) 
     """
     im1 = load_img(file1)
     im2 = load_img(file2)
     c11 = c2d(im1, im1, mode='same')  # baseline
     c22 = c2d(im2, im2, mode='same')  # baseline
     c12 = c2d(im1, im2, mode='same')
     m = [c11.max(), c12.max(), c22.max()]
     diff_ab = 100 * (1-m[1]/m[0])
     diff_ba = 100 * (1-m[1]/m[2])
     
     fail=max(diff_ab,diff_ba) > diff

     if fail:
          raise CompareImageException(c11.max(), c12.max(), c22.max())

     return fail

def main():
     """
     Compares two files (JPEG, PNG or PDF)
     """
  if len(sys.argv) < 4:
    print("""Usage: %s FILE1 FILE2 N.NN

        FILE1,FILE2 can be in JPEG, PNG, or PDF format.
        N.NN should be a small floating point number. It represents 
        the allowed difference in the image metrics.
        correlate2d from scipy.signal.signaltools is used to compute 
        the metrics.
    """ % sys.argv[0])
    sys.exit(0)
    diff_allowed=float(sys.argv[3])
    try:
         fail=compare(sys.argv[1],sys.argv[2],diff_allowed)
    except CompareImageException as i:
         print("error: %s" % i)
    

    print("limit: %.2f%% -> %s" % (diff_allowed, ("OK","FAIL")[fail]))
    if fail: sys.exit(1)


if __name__ == "__main__":
       main()

