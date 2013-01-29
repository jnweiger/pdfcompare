VER=1.1b
refresh=

all: test

test:
	ln -sf ../pdf_highlight.py pdfcompare
	env PATH=.:$$PATH sh ./helptest.sh $(VER)
	env PATH=.:$$PATH refresh=$(refresh) sh ./restest.sh
	rm pdfcompare

refresh:
	make test refresh=yes
