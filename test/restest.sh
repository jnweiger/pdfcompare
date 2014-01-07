#!/bin/sh
#
# This script compares the output pdf of a new pdfcompare version
# with a test-pdf. 
###DONE diff geht nicht->'grep -a /Annot' vergleichen, pdftotext probieren ob valides PDF
# eventuell Graphik rendern + vergleichen (wie pdf nach graphik?) 
#
## run once with refresh=yes, after you verified the test suite runs ok.
#refresh=yes

testpdf()
{
pdfcompare -o newpdf.pdf -c test1.pdf test2.pdf
newpdf=$(grep -a '/Annot$' newpdf.pdf)
oldpdf=$(grep -a '/Annot$' oldpdf.pdf)
assertEquals "Pdftest returned != 0" "$oldpdf" "$newpdf"
pdftk newpdf.pdf dump_data > /dev/null
assertTrue "Pdftest returned !=0" "[[ $? -eq 0 ]]"
python imgcmp.py oldpdf.pdf newpdf.pdf 0.5
assertTrue "Pdftest returned !=0" "[[ $? -eq 0 ]]"
test -n "$refresh" && mv newpdf.pdf oldpdf.pdf
rm -f newpdf.pdf
}

testascii()
{
pdfcompare -o newascii.pdf -c test2.txt test1.pdf
oldascii=$(grep -a -c '/Annot$' oldascii.pdf)
newascii=$(grep -a -c '/Annot$' newascii.pdf)
assertEquals "Asciitest returned !=0" "$oldascii" "$newascii"
pdftk newascii.pdf dump_data > /dev/null
assertTrue "Asciitest returned !=0" "[[ $? -eq 0 ]]"
python imgcmp.py oldascii.pdf newascii.pdf 0.5
assertTrue "Asciitest returned !=0" "[[ $? -eq 0 ]]"
test -n "$refresh" && mv newascii.pdf oldascii.pdf
rm -f newascii.pdf
}

testxml()
{
pdfcompare -o newxml.pdf -c test1.xml test2.pdf
oldxml=$(grep -a '/Annot$' oldxml.pdf)
newxml=$(grep -a '/Annot$' newxml.pdf)
assertEquals "Xmltest returned !=0" "$oldxml" "$newxml"
pdftk newxml.pdf dump_data > /dev/null
assertTrue "Xmltest returned !=0" "[[ $? -eq 0 ]]"
python imgcmp.py oldxml.pdf newxml.pdf 0.5
assertTrue "Xmltest returned !=0" "[[ $? -eq 0 ]]"
test -n "$refresh" && mv newxml.pdf oldxml.pdf
rm newxml.pdf
}

testsearch()
{
pdfcompare -o newsearch.pdf -s 'Lorem' test1.pdf
oldsearch=$(grep -a '/Annot$' oldsearch.pdf)
newsearch=$(grep -a '/Annot$' newsearch.pdf)
assertEquals "Searchtest returned !=0" "$oldsearch" "$newsearch"
pdftk newsearch.pdf dump_data > /dev/null
assertTrue "Searchtest returned !=0" "[[ $? -eq 0 ]]"
python imgcmp.py oldsearch.pdf newsearch.pdf 0.5
assertTrue "Searchtest returned !=0" "[[ $? -eq 0 ]]"
test -n "$refresh" && mv newsearch.pdf oldsearch.pdf
rm -f newsearch.pdf
}


. /usr/share/shunit2/src/shunit2

