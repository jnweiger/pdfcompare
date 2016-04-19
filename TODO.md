TODO

* Test with pyPDF2

* Test with python3

* Is a Windows installer possible?

* Test popups with Microsoft Edge Browser

* hunspell issues:
  - python-HunspellPure should be a separate module. Split it.
  - we artificially limit to [A-Z_-]+ for words. This is bad for german umlauts.
  - extend hunspell to allow a progress indicator callback.
    (counting newlines seen in response)

* testsuite
  - maybe prepare a test script that allows numbers to be off by some 
    percentage, but wants everything else precise.
    This helps with pdf source checking.

* improve --log logfile generator.
  produce a json/xml/csv/txt file describing the diffs, -s word locations 
  and --spellcheck results.

* one letter changes always become word changes.
  Either run in single character mode. Or try to trim the replaced text for 
  common suffix or common prefix.

* Normalize nonbreaking spaces to spaces.
  This is important when e.g. markdown source has a 0x20 space, but rendered
  PDF may have &nbsp; instead.



DONE:

* write compressed streams.

* catch file open errors, before ET complains about 0 elements.

* perform only same-length-replace. All other replace-ops should be replace+insert
  or replace+delete.

* place delete marker at last text end position, rather than next text start position.
  This is a tricky, implementation in markword().

* testsuite
  - a 1:1 comparison is not possible, as e.g. poppler-0.18 and poppler-0.20
    produce differences in the exact coordinates used.
  - make a fuzzy comparison against templates with python-cv, pHash, etc...
    http://stackoverflow.com/questions/1819124/image-comparison-algorithm suggests
    Scipy.  imgcmp.py does this.
  - generate several output.pdf, convert via ImageMagick to png, 
  - run pdfcompare --version.

* nicer +++---~~~== git style diagnostics per page, rather than saying '87 hits'.

* if pagebreaks are within deleted text, point this out in the baloon popup.
  
* Navigation from changebar to changebar, if there are many unchanged pages to jump over.
  - calculation, graphics done. Hack with relocated navigation done.

* popups are all in one line in okular. Need to provide linebreaks manually, sigh.

* introduce an ignore-margin for text changes. Any words there will not go into
  the compare wordlists, and will not match with --search. This is meant to skip
  over pagenumbers and other bottom or top matter, that is not considered part
  of the document contents stream.
  --feature margin shall draw the margin area as shaded gray, so that we know
  where we are.

* feature:
  pipe the wordlist through hunspell, if hunspell is available.
  use search-highlights to mark all words for which hunspell has spelling 
  suggestions. 

* feature: 
  added a trivial --log implementation

* second level diff for moved blocks.
