TODO

* testsuite
  - run pdfcompare --version.
  - a 1:1 comparison is not possible, as e.g. poppler-0.18 and poppler-0.20
    produce differences in the exact coordinates used.
  - maybe prepare a test script that allows numbers to be off by some 
    percentage, but wants everything else precise.
  - generate several output.pdf, convert via ImageMagick to png, 

* if pagebreaks are within deleted text, point this out in the baloon popup.
  
* ghostscript complains about currupt XREF table.

* nicer +++---~~~== git style diagnostics per page, rather than saying '87 hits'.

* one letter changes always become word changes.
  Either run in single character mode. Or try to trim the replaced text for 
  common suffix or common prefix.

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

* place delete marker at last text end position, rather than next text start position.
  This is a tricky, implementation in markword().

* testsuite (partially)
  - make a fuzzy comparison against templates with python-cv, pHash, etc...
    http://stackoverflow.com/questions/1819124/image-comparison-algorithm suggests
    Scipy.  imgcmp.py does this.
