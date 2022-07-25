#!/bin/sh
#
# This script runs pdfcompare under python3
# 
# printing the usage should be enough, no?

testpy3()
{
out=$(python3 pdfcompare --help 2>&1)
py3pdf=$(echo $out | grep 'No module named pyPdf')
ver=$(echo $out | grep 'version: ')

assertTrue "testpy3 missing python3-pyPdf" '[ -z "$py3pdf" ]'
# startSkipping
assertTrue "testpy3 --help contains version" '[ -n "$ver" ]'
}

# . /usr/share/shunit2/src/shunit2
. shunit2

