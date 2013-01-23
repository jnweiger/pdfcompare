VER=1.0

all: test

test:
	ln -sf ../pdf_highlight.py pdfcompare
	env PATH=.:$$PATH sh ./helptest.sh $(VER)
	env PATH=.:$$PATH sh ./restest.sh
	rm pdfcompare
