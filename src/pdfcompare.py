#! /usr/bin/python3
#
# (C) 2026 jnweiger@gmail.com, unfinished rewrite....
#
# Requires:
#   apt install python3-pymupdf
#
# Limitations of pdf-viewers with popups
#   pdfcompare supports two types of popups: text-annotation (T), and higlight-info (H) and optionally highlight info with popup (Hp).
#   - Firefox displays both. The icon with H reacts to mouse over. Each T has two icons stacked. The upper one reacts.
#   - Okular with H: reacts to mouse over only in "Browse" (CTRL-1) mode, not in text or area select mode.
#     T creates an icon, that sometimes (top edge) reacts to double click in text select mode. Ocular requires Hp.
#   - xpdf (xpopple) seems to not support any popups. T creates an unclickable icon. (Same as ocular)
#   - mupdf same as xpdf. It does not even have a right click menu.
#   - sioyek: same as mupdf. It does not even have a right click menu. Always in text selection mode.
#   - zathura with zathura-pdf-poppler, same as mupdf. (zathura-pdf-mupdf from ppa:spvkgn/zathura-mupdf fails)
#   - qpdfview reacts with mousover for H when the mouse touches the paragraph. Mousover and click with T work correctly.
#   - evince: mousover T+H shows a small popup, click a larger window, that stays. The T icon looks ugly, though. H is prefered.
#   - atril: no mouseover or click with H, but perfect with T, it even honors transparency there.
#
# Example files:
#  - https://www.alldatasheet.com/datasheet-pdf/download/107089/ATMEL/ATMEGA640.html    # old processor handbook from ATMEL AVR
#  - https://ww1.microchip.com/downloads/en/DeviceDoc/ATmega640-1280-1281-2560-2561-Datasheet-DS40002211A.pdf   # new version from microchip.
#
#
# References:
#   - https://github.com/pymupdf/PyMuPDF/blob/main/docs/app1.rst#controlling-quality-of-html-output

__VERSION__ = '1.99.0'
import urllib   # used when normal encode fails.
from pprint import pprint
import sys, os, subprocess
import argparse
from difflib import SequenceMatcher
# FIXME: class Hunspell should be loaded as a module
# import HunspellPure


# Universal PyMuPDF import with fallback cascade
mu = None

for name in ["fitz", "pymupdf"]:    # not mupdf, it has a different api
    try:
        mu = __import__(name)
        break
    except ImportError:
        continue

if mu is None:
    raise ImportError("No PyMuPDF found. Install with:\n\t sudo apt install python3-pymupdf\n  OR\n\t pip install pymupdf")


def load_file(name, firstpage=0, lastpage=None):
    # Now use mu consistently
    doc = mu.open("input.pdf")
    text = []
    words = []
    fonts = []
    if lastpage == None: lastpage = doc.page_count -1
    if firstpage == None: firstpage = 0
    if lastpage >= doc.page_count:
        print(f"WARNING: lastpage={lastpage} too large. Reduced to {doc.page_count-1}")
        lastpage = doc.page_count -1
    if firstpage > doc.page_count:
        print(f"WARNING: firstpage={firstpage} too large. Reduced to {doc.page_count-1}")
        firstpage = doc.page_count -1

    for pno in range(firstpage, lastpage+1):
        text.append(doc.get_page_text(pno))
        words.append(doc[pno].get_text("words", sort=False))
        fonts.append(doc.get_page_fonts(pno))

    # print(doc[0].get_text("json"))
    # ...
    #   {
    #    "number":5, "type":0,
    #    "bbox":[ 147.6649932861328, 146.13369750976562, 464.3600769042969, 164.52369689941406 ],
    #    "lines":[ {
    #      "spans":[ {
    #        "size":15.0, "flags":4, "bidi":0, "color":0, "alpha":255,
    #        "font":"CenturyGothic", "ascender":1.00600004196167, "descender":-0.2199999988079071,
    #        "text":"AN ADVENTURE FOR CHARACTER LEVELS 1-3",
    #        "origin":[ 147.6649932861328, 161.22369384765625 ],
    #        "bbox":[ 147.6649932861328, 146.13369750976562, 464.3600769042969, 164.52369689941406 ]
    #       } ],
    #      "wmode":0, "dir":[ 1.0, 0.0 ],
    #      "bbox":[ 147.6649932861328, 146.13369750976562, 464.3600769042969, 164.52369689941406 ]
    #     } ]
    #   },
    #   {
    #    "number":6, "type":1,
    #    "bbox":[ 45.0, 171.00003051757812, 567.719970703125, 612.7454223632812 ],
    #    "width":1090, "height":921,
    #    "ext":"jpeg", "colorspace":1, "xres":96, "yres":96, "bpc":8,
    #    "transform":[ 522.719970703125, 0.0, -0.0, 441.7453918457031, 45.0, 171.00003051757812 ],
    #    "size":433851,
    #    "image":"/9j/7gAOQWRvYmUAZIAAAAAA/9sAQwACAgIDAgMDAwMDBAQEBAQFBQUFBQUHBgYGBgYHCAcICAgIBwgJCgoKC....
    print(f"✓ {name}")
    return { "doc": doc, "text": text, "words": words, "fonts": fonts }


def highlight_words_in_page(page, keywords):
    rects = []
    for k in keywords:
        rects.extend(page.search_for(k))
    print("✓ search_for")

    if rects:
        print(rects)
        highlight = page.add_highlight_annot(rects)
        highlight.set_colors(stroke=(1, 1, 0))  # yellow background
        highlight.update()
        print("✓ update")

        # Tooltip popup (mouse-over text) for ocular.
        popup_rect = highlight.rect + (10, -50, 100, -10)  # position above/beside
        highlight.set_popup(popup_rect)
        print("✓ highlight.set_popup")
        # the above is needed for ocular, but not evince.

        info = highlight.info
        print(info)
        info["content"] = f"Found keyword: {keywords}"
        info["name"] = "FishMonster"
        info["title"] = "AuthorName"
        info["subject"] = "Subject line"
        info["creationDate"] = "2026-01-27"
        info["modDate"] = "2026-01-28"
        highlight.set_info(info)
        print("✓ set_info")
        print(highlight.info)
        highlight.set_opacity(0.5)  # 1.0 = fully opaque, 0.0 = invisible
        print("✓ set_opacity")
        #highlight.set_open(False)
        #print("✓ set_open")
        highlight.update()
        print("✓ update")

        # alternate method:
        point = highlight.rect.tr  # top-right of first highlight rect
        text_annot = page.add_text_annot(point, "add_text_annot tooltip")
        text_annot.set_opacity(0.9)  # visibility: none 0..1 full
        text_annot.update()


def save_file(name, doc, no_compression=False):
    doc.save(name, garbage=4, deflate=(not no_compression))
    print("✓ save")
    doc.close()
    print(f"✓ {name} created with highlights + tooltips")


def main():
    parser = argparse.ArgumentParser(epilog="version: "+__VERSION__, description="Highlight changed/added/deleted/moved text in a PDF file.")
    parser.def_trans = 0.6
    parser.def_decrypt_key = ''
    parser.def_colors = { 'E': [1,0,1,    'pink'],        # extra
                          'A': [.3,1,.3,  'green'],       # added
                          'D': [1,.3,.3,  'red'],         # deleted
                          'C': [.9,.8,0,  'yellow'],      # changed
                          'M': [.7,1,1,   'blue'],        # moved
                          'B': [.9,.9,.9, 'gray'] }       # borders
    parser.def_output = 'output.pdf'
    parser.def_marks = 'A,D,C'
    parser.def_features = 'H,C,P,W,B'
    parser.def_margins = '0,0,0,0'
    parser.def_margins = '0,0,0,0'
    parser.def_below = False
    parser.add_argument("-c", "--compare-text", metavar="OLDFILE",
                        help="Mark added, deleted and replaced text (or see -m) with regard to OLDFILE. \
                              File formats .pdf, .xml, .txt are recognized by their suffix. \
                              The comparison works word by word.")
#    parser.add_argument("-d", "--decrypt-key", metavar="DECRYPT_KEY", default=parser.def_decrypt_key,
#                        help="Open an encrypted PDF. Default: KEY='"+parser.def_decrypt_key+"'")
#    parser.add_argument("-e", "--exclude-irrelevant-pages", default=False, action="store_true",
#                        help="With -s: show only matching pages; with -c: show only changed pages. \
#                        Default: reproduce all pages from INFILE in OUTFILE.")
    parser.add_argument("-f", "--features", metavar="FEATURES", default=parser.def_features,
                        help="Specify how to mark. Allowed values are 'highlight', 'changebar', 'popup', \
                        'navigation', 'watermark', 'margin'. Default: " + str(parser.def_features))
    parser.add_argument("-i", "--nocase", default=False, action="store_true",
                        help="Make -s case insensitive; default: case sensitive.")
    parser.add_argument("-l", "--log",  metavar="LOGFILE",
                        help="Write an python datastructure describing all the overlay objects on each page. Default none.")
    parser.add_argument("-m", "--mark", metavar="OPS", default=parser.def_marks,
                        help="Specify what to mark. Used with -c. Allowed values are 'add','delete','change','equal'. \
                              Multiple values can be listed comma-seperated; abbreviations are allowed.\
                              Default: " + str(parser.def_marks))
    parser.add_argument("-n", "--no-output", default=False, action="store_true",
                        help="Do not write an output file; print diagnostics only. Default: write output file as per -o option.")
    parser.add_argument("-o", "--output", metavar="OUTFILE", default=parser.def_output,
                        help="Write output to FILE; default: "+parser.def_output)
    parser.add_argument("-s", "--search", metavar="WORD_REGEXP",
                        help="Highlight WORD_REGEXP")
#    parser.add_argument("--spell", "--spell-check", default=False, action="store_true",
#                        help="Run the text body of the (new) pdf through hunspell. Unknown words are underlined. \
#                              Use e.g. 'env DICTIONARY=en_US ...' (or de_DE, ...) to specify the spelling dictionary, \
#                              if your system has more than one. To add new words to your private dictionary use e.g. \
#                              'echo >> ~/.hunspell_en_US ownCloud'. Check with 'hunspell -D' and study 'man hunspell'.")
    parser.add_argument("--strict", default=False, action="store_true",
                        help="Show really all differences. Default: ignore removed hyphenation; \
                              ignore character spacing inside a word.")
    parser.add_argument("-t", "--transparency", type=float, default=parser.def_trans, metavar="TRANSP",
                        help="Set transparency of the highlight; invisible: 0.0; full opaque: 1.0; \
                        default: " + str(parser.def_trans))
    parser.add_argument("-B", "--below", default=parser.def_below, action="store_true",
                        help="Paint the highlight markers below the text. Try this if the normal merge crashes. Use with care, highlights may disappear below background graphics. Default: BELOW='"+str(parser.def_below)+"'.")
    parser.add_argument("-C", "--search-color", metavar="NAME=R,G,B", action="append",
                        help="Set colors of the search highlights as an RGB triplet; R,G,B ranges are 0.0-1.0 each; valid names are 'add,'delete','change','equal','margin','all'; default name is 'equal', which is also used for -s; default colors are " +
                        " ".join(["%s=%s,%s,%s /*%s*/ " %(x_y[0],x_y[1][0],x_y[1][1],x_y[1][2],x_y[1][3]) for x_y in list(parser.def_colors.items())]))
    parser.add_argument("-D", "--debug", default=False, action="store_true",
                        help="Enable debugging. Prints more on stdout, dumps several *.xml or *.pdf files.")
    parser.add_argument("-F", "--first-page", metavar="FIRST_PAGE",
                        help="Skip some pages at start of document; see also -L option. Default: all pages.")
    parser.add_argument("-L", "--last-page", metavar="LAST_PAGE",
                        help="Limit pages processed; this counts pages starting with 0. It does not use document \
                        page numbers; see also -F; default: all pages.")
    parser.add_argument("-M", "--margins", metavar="N,E,W,S", default=parser.def_margins,
                        help="Specify margin space to ignore on each page. A margin width is expressed \
                        in units of ca. 100dpi. Specify four numbers in the order north,east,west,south. Default: "\
                        + str(parser.def_margins))
    parser.add_argument("-S", "--source-location", default=False, action="store_true",
                        help="Annotation start includes :pNX: markers where 'N' is the page number of the location \
                              in the original document and X is 't' for top, 'c' for center, or 'b' for bottom of the page. \
                              Default: Annotations start only with 'chg:', 'add:', 'del:' optionally followed by original text.")
    parser.add_argument("-V", "--version", default=False, action="store_true",
                        help="Print the version number and exit.")
    parser.add_argument("-X", "--no-compression", default=False, action="store_true",
                        help="Write uncompressed PDF. Default: FlateEncode filter compression.")
    parser.add_argument("--leftside", default=False, action="store_true",
                        help="Put changebars and navigation at the left hand side of the page. Default: right hand side.")
    parser.add_argument("infile", metavar="INFILE", help="The input file.")
    parser.add_argument("infile2", metavar="INFILE2", nargs="?", help="Optional 'newer' input file; alternate syntax to -c")

    args = parser.parse_args()      # --help is automatic
    if args.version: parser.exit(__VERSION__)
    args.transparency = 1 - args.transparency     # it is needed reversed.

    if not os.access(args.infile, os.R_OK):
        parser.exit("Cannot read input file: %s" % args.infile)
    f1 = load_file(args.infile, firstpage=args.first_page, lastpage=args.last_page)
    # f1 = { "doc": doc, "text": text, "words": words, "fonts": fonts }

    highlight_words_in_page(f1["doc"][0], ["LEVEL", "of", "the"])
    save_file(args.output, f1["doc"], args.no_compression)


if __name__ == "__main__":
    main()

