* Normalize nonbreaking spaces to spaces.
  This is important when e.g. markdown source has a 0x20 space, but rendered
  PDF may have &nbsp; instead.

* Navigation from changebar to changebar, if there are many unchanged pages to jump over.

* test on fossy: import argparse complains about already imported.

* popups are all in one line in okular. Need to provide linebreaks manually, sigh.

* catch file open errors, before ET complains about 0 elements.
