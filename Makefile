all: pdfcomparetest.tar.bz2

pdfcomparetest.tar.bz2:
	tar jcvf pdfcomparetest.tar.bz2 test/concept test/*.pdf test/*.py test/*.txt test/*.xml test/*.sh test/Makefile
