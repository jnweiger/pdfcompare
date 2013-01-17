TODO

* testsuite
  - run pdfcompare --version.
  - a 1:1 comparison is not possible, as e.g. poppler-0.18 and poppler-0.20
    produce differences in the exact coordinates used.
  - maybe prepare a test script that allows numbers to be off by some 
    percentage, but wants everything else precise.
  - generate several output.pdf, convert via ImageMagick to png, 
    make a fuzzy comparison against templates with python-cv, pHash, etc...
    http://stackoverflow.com/questions/1819124/image-comparison-algorithm suggests
    Scipy.

  
* ghostscript complains about currupt XREF table.

* nicer +++---~~~== git style diagnostics per page, rather than saying '87 hits'.

* place delete marker at last text end position, rather than next text start position.
  This is tricky, as we only care for markers, not unmarked text.
  (l=-1 code implementation started around create_mark())

* Normalize nonbreaking spaces to spaces.
  This is important when e.g. markdown source has a 0x20 space, but rendered
  PDF may have &nbsp; instead.

* Navigation from changebar to changebar, if there are many unchanged pages to jump over.

* test on fossy: import argparse complains about already imported.

* popups are all in one line in okular. Need to provide linebreaks manually, sigh.

DONE:
* write compressed streams.

* catch file open errors, before ET complains about 0 elements.

* perform only same-length-replace. All other replace-ops should be replace+insert
  or replace+delete.
