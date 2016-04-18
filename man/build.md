# Definition

DB="/usr/share/xml/docbook/stylesheet/nwalsh/current/"

# Creating Manpages

xsltproc $DB/manpages/docbook.xsl pdfcompare.xml

# Creating HTML

xsltproc --output pdfcompare.html $DB/xhtml/docbook.xsl pdfcompare.xml

# Creating PDF

xsltproc --output pdfcompare.fo $DB/fo/docbook.xsl pdfcompare.xml
fop pdfcompare.fo pdfcompare.pdf && rm pdfcompare.fo


