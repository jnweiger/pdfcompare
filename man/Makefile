#
# apt-get install xsltproc fop
#

## openSUSE:
DB=/usr/share/xml/docbook/stylesheet/nwalsh/current/
## Ubuntu:
DB=/usr/share/xml/docbook/stylesheet/nwalsh/

all: man html pdf

man:
	xsltproc $(DB)/manpages/docbook.xsl pdfcompare.xml

html:
	xsltproc --output pdfcompare.html $(DB)/xhtml/docbook.xsl pdfcompare.xml

pdf:
	xsltproc --stringparam paper.type A4 --output pdfcompare.fo $(DB)/fo/docbook.xsl pdfcompare.xml
	fop pdfcompare.fo pdfcompare.pdf && rm pdfcompare.fo
