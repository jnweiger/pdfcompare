
VER=1.5
D=dist/pdfcompare-$(VER)
EXCL=--exclude \*.orig --exclude \*~

all: check tar

check test:
	cd test; make test VER=$(VER)

testrefresh refreshtest:
	cd test; make test refresh=yes

clean:
	rm -rf dist *.orig *~
	rm -rf test/*.orig test/*~

tar dist:
	rm -rf dist
	mkdir -p $D
	ln -s ../../pdf_highlight.py $D/pdfcompare.py
	ln -s ../../test $D/test
	cd dist; tar jhcvf ../pdfcompare-$(VER).tar.bz2 pdfcompare-$(VER) $(EXCL)
	rm -rf dist

