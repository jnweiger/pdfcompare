#! /usr/bin/python
#
# compare two images using Scipy
# (c) 2013 - jw@suse.de - distributer under GPL-2.0 or ask.
#
# Dependencies:
# sudo zypper in python-scipy
# sudo zypper in ImageMagick

import sys, os, re, tempfile
from pprint import pprint

import scipy as sp
from scipy.misc import imread
from scipy.signal.signaltools import correlate2d as c2d

if len(sys.argv) < 4:
  print """Usage: %s FILE1 FILE2 N.NN

        FILE1,FILE2 can be in JPEG, PNG, or PDF format.
        N.NN should be a small floating point number. It represents 
        the allowed difference in the image metrics.
        correlate2d from scipy.signal.signaltools is used to compute 
        the metrics.
  """ % sys.argv[0]
  sys.exit(0)


def load_img(fname):
     # get JPG image as Scipy array, RGB (3 layer)
     if re.search("\.pdf$", fname, re.I):
       # convert PDF to JPG
       tf = tempfile.NamedTemporaryFile(delete=True, suffix=".jpg")
       print "creating %s" % tf.name
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

im1 = load_img(sys.argv[1])
im2 = load_img(sys.argv[2])
diff_allowed = float(sys.argv[3])

#pprint([im1.shape])
#pprint([im2.shape])

c11 = c2d(im1, im1, mode='same')  # baseline
c22 = c2d(im2, im2, mode='same')  # baseline
c12 = c2d(im1, im2, mode='same')
m = [c11.max(), c12.max(), c22.max()]
# (42105.00000000259, 39898.103896795357, 16482.883608327804, 15873.465425120798)
# [7100.0000000003838, 7028.5659939232246, 7100.0000000000318]

diff_ab = 100 * (1-m[1]/m[0])
diff_ba = 100 * (1-m[1]/m[2])
print "diff a-b: %.2f%%" % (diff_ab)
print "diff b-a: %.2f%%" % (diff_ba)
fail = max(diff_ab,diff_ba) > diff_allowed
if fail: pprint([c11.max(), c12.max(), c22.max()])
print "limit: %.2f%% -> %s" % (diff_allowed, ("OK","FAIL")[fail])
if fail: sys.exit(1)
