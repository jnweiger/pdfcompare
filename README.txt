pdfcompare
==========

Compare text of two PDF files, write a resulting PDF with highlighted changes.
Potential text portions that were moved around are recognized and analyzed 
for similarity with a second level diff.

Required Packages:

* pyPdf
* reportlab.pdfgen
* reportlab.lib.colors
* pygame.font'

Packages
========
DEB and RPM packages are built in
 https://build.opensuse.org/package/show/Documentation:Tools/pdfcompare
Downloads directly from the openSUSE Build Service are available in
 http://software.opensuse.org/download.html?project=Documentation%3ATools&package=pdfcompare
Stable releases are done via github
 https://github.com/jnweiger/pdfcompare/releases


Example Usage and tips
======================

Starting with two vastly differently formatted PDF files, we want to see the textual difference betweeen
GPL-3.0 and AGPL-3.0 license. Most of the text is identical, except for preamble, Paragraph 13 and the footer.

We first generate an unusually formatted (no obvious LaTeX output) version of the GPL-3.0 text

    wget http://www.tp-link.de/resources/document/GPL%20License%20Terms.pdf -O all-gpl-tplink.pdf
    pdftk all-gpl-tplink.pdf cat 18-26 output gpl-3.0-tplink.pdf

Then we download a PDF version of the Affero GNU Public License

    wget http://trac.frantovo.cz/sql-vyuka/export/29%3A4b6ab4ba1a95/licence/agpl-3.0.pdf

Now we produce an output reflecting the agpl contents and layout, with color highlights added.
Green shows text that was not in GPL-3.0 but is in AGPL-3.0
Red marks the gaps where text was removed in AGPL. Most PDF viewers can show an annotation popup when the mouse is over
the colored mark. For red marks, the annotation popup contains the word 'del: ' and the deleted text.
Yellow marks show changed text. The annotation popup contains the word 'chg:' and the original text.

    pdfcompare gpl-3.0-tplink.pdf agpl-3.0.pdf -o gpl-agpl-diff.pdf
    xdg-open gpl-agpl-diff.pdf

Pdfcompare also features text search and spellchecking (via hunspell). Search hits are marked in pink. Spellcheck errors are underlined in pink. If you get excessive spellcheck errors, try switching the language with env DICTIONARY=de_DE or study the hunspell documentation.

The option --margin 0,0,0,240 can be used with the two documents used here to ignore the page numbers introduced in agpl-3.0.pdf -- With this option, a gray bar will cover the page number and it is not marked as a change. 
