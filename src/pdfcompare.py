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
#   - https://pymupdf.readthedocs.io/en/latest/recipes-annotations.html

__VERSION__ = '1.99.4'
import urllib   # used when normal encode fails.
from pprint import pprint
import sys, os, subprocess, json
import argparse
import difflib
# FIXME: class Hunspell should be loaded as a module
# import HunspellPure


debug = 1   # 0, 1, 2 incremented by -D

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

    if name.lower().endswith(".pdf"):
        return load_file_pdf(name, firstpage, lastpage)

    if name.lower().endswith(".txt") or name.lower().endswith(".text"):
        return load_file_text(name)

    print("ERROR: input file name must end with .pdf or .txt, saw:", name)
    sys.exit(1)


def load_file_text(name):
    words = []
    with open(name) as fp:
        for line in fp:
            for word in line.split():
                words.append([ 0, 0, 0, 0, word, 0, 0, 0])
    return { "doc": [], "text": [], "words": [ words ] , "fonts": [] }


def load_file_pdf(name, firstpage=0, lastpage=None):
    # Now use mu consistently
    doc = mu.open(name)
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
        # text.append(doc.get_page_text(pno))
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

    # words= [
    #   [
    #     [516.18017578125, 705.237548828125, 575.9652709960938, 712.1975708007812, "2549A–AVR–03/05", 0, 0, 0],
    #     [36.0, 70.448486328125, 94.30778503417969, 84.42848205566406, "Features", 1, 0, 0],
    #     [36.0, 70.448486328125, 94.30778503417969, 84.42848205566406, "More", 1, 0, 0],
    #   ], [
    #     [36.0, 87.24887084960938, 39.486000061035156, 97.20886993408203, "•", 1, 1, 0],
    #     [45.119998931884766, 87.99403381347656, 65.07029724121094, 96.99403381347656, "Low", 1, 1, 1],
    #     [67.55159759521484, 87.99403381347656, 124.70878601074219, 96.99403381347656, "Performance,", 1, 1, 2],
    #   ]
    # ]
    if debug >1:
        print(f"load_file_pdf({name})")
    return { "doc": doc, "text": text, "words": words, "fonts": fonts }


# flatten while keeping original records
def flatten(pages):
    flat = []
    for p_idx, page in enumerate(pages):
        for r_idx, rec in enumerate(page):
            flat.append((p_idx, r_idx, rec))
    return flat


def log_opcodes(fp, old, new, opcodes):
    for op, i1,i2, j1,j2 in opcodes:
        if op == 'delete':
            print("-", old[i1:i2], file=fp)
        if op == 'insert':
            print("+", new[j1:j2], file=fp)
        if op == 'replace':
            print("-/+", old[i1:i2], file=fp)
            print("  :", new[j1:j2], file=fp)


def mark_opcodes(doc, old, new, opcodes, hide_pop=False):
    for op, i1,i2, j1,j2 in opcodes:
        # all of the deleted words in one, even if they span multiple pages.
        #   old pagination is irrelevant, it may differ from new pagination anyway.
        delwords = [w[2][4] for w in old[i1:i2]]
        if op == 'delete':
            page_nr = new[j1][0]
            if debug:
                point = tuple(int(x) for x in new[j1][2][:2])
                print(f"-- page={page_nr}:", point, delwords)  # just a starting point here
            page = doc[new[j1][0]]
            del_marker(page, new[j1][2], delwords, hide_pop=hide_pop)

        if op == 'insert' or op == 'replace':
            page_rects = split_into_pages(new[j1:j2])
            if debug and op == 'replace':
                point = tuple(int(x) for x in page_rects[0][1][0][:2])
                print(f"/- page={page_rects[0][0]}:", point, delwords)  # just take the first page...
            for page_nr,rects,words in page_rects:
                page = doc[page_nr]
                if op == 'insert':
                    if debug:
                        point = tuple(int(x) for x in rects[0][:2])
                        print(f"++ page={page_nr}:", point, words)
                    ins_marker(page, rects, words, hide_pop=hide_pop)
                else:
                    if debug:
                        point = tuple(int(x) for x in rects[0][:2])
                        print(f"\\+ page={page_nr}:", point, words)
                    chg_marker(page, rects, delwords, hide_pop=hide_pop)


def split_into_pages(ops):
    # ops = [(0, 71, (508,279,539,293, 'pariatur', 7,0,15)), (0, 72, (130,291,175,305, 'consectetur', 7,1,0)), ...]
    #
    # returns: [(0, [rect,rect,...], ["word", "word", ...]), (1, [rect,...], ["word", ...]), (2, ...), ...]
    # (the third element (list of words) is only used for diagnostics prints.)
    r = [ ( ops[0][0], [], []) ]
    for op in ops:
        if op[0] != r[-1][0]:    # new page
            r.append((op[0], [], []))
        r[-1][1].append((op[2][:4]))    # rect
        r[-1][2].append((op[2][4]))     # "word"
    return r


def text_rects2polygon(rects, pad=0):
    # pass in a list of rectangles.
    # we construct a polygon, that contains all rectangles, but does not contain unnecessary corner areas.
    # Primitive algorithm: we only check the very first and very last rect if indented.
    xmin, ymin, xmax, ymax = r_bbox(rects)
    if debug > 1:
        print("text_rects2polygon: r_bbox=", r_bbox(rects))
    xmin -= pad
    ymin -= pad
    xmax += pad
    ymax += pad

    if rects[0][0] > xmin+pad:
        if rects[-1][2] < xmax-pad:
            # both ends need an indent
            return [(xmin, rects[0][3]-pad), (rects[0][0]-pad, rects[0][3]-pad), (rects[0][0]-pad, ymin),
                    (xmax, ymin), (xmax, rects[-1][1]+pad), (rects[-1][2]+pad, rects[-1][1]+pad),
                    (rects[-1][2]+pad, ymax), (xmin, ymax)]
        else:
            # start needs an indent
            return [(xmin, rects[0][3]-pad), (rects[0][0]-pad, rects[0][3]-pad), (rects[0][0]-pad, ymin),
                    (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    else:
        if rects[-1][2] < xmax-pad:
            # trailing end needs an indent
            return [(xmin, ymin), (xmax, ymin), (xmax, rects[-1][1]+pad), (rects[-1][2]+pad, rects[-1][1]+pad),
                    (rects[-1][2]+pad, ymax), (xmin, ymax)]
        else:
            # simple rectangle
            if debug > 1:
                print("text_rects2polygon: simple")
            return [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]


def ins_marker(page, rect, words, color=(0,1,0), hide_pop=False):
    chg_marker(page, rect, words, label="add", color=color, hide_pop=hide_pop)


def chg_marker(page, rect, words, label="chg", color=(0,1,1), hide_pop=False):
    ht = "[" + label + "] " + ' '.join(words)
    tt = '' if hide_pop else ht
    poly = text_rects2polygon(rect, pad=1)
    add_annotation(page, text=tt, rect=poly, mode='P', fill_c=None, color=color, href=ht)


def del_marker(page, rect, words, hide_pop=False):
    x = rect[0]
    y1 = rect[1]-2  # keep some space, so that ins or chg markers fit inside.
    y2 = rect[3]+2
    w = 2*(y2-y1)
    m=1
    poly = [ (x-w, y1), (x-w-m, y1-m), (x+w+m, y1-m), (x+w, y1),
             (x+1, y1), (x+1, y2),
             (x+w, y2), (x+w+m, y2+m), (x-w-m, y2+m), (x-w,y2),
             (x-1, y2), (x-1, y1) ]
    ht = '[del] ' + ' '.join(words)
    tt = '' if hide_pop else ht
    add_annotation(page, text=tt, rect=poly, mode='P', color=(1,0,0), fill_c=(1,0,0), href=ht)


# see https://pymupdf.readthedocs.io/en/latest/recipes-annotations.html
def add_annotation(page, text='', rect=(200, 500, 280, 520), mode="H", color=(1, 0, 0), fill_c=(0.9, 0.9, 0.9), transparent=0.2, href=None, goto=None):
    # mode letters:
    #   H: highlight with mouse over    Okular: Hervorhebung mit Kommentar
    #   U:  Underline_annot
    #   X: strikethrough line
    #   S: squiggly curly line
    #   T: text annotaiton.             Okular: Notiz (immer gelb)
    #   F: free text annotation.        Okular: notiz, mit font spec und ohne icon
    #   P: polygon. instead of the usueal (x0, y0, x1, y1) use rect=[(x0,y0), (x1,y1), (x2,y2), ...]
    #
    # modifiers to combine with the main mode letters:
    #   +: define a popup position
    #   I: Add title to info structure  (default on)
    #
    # href=str: add a clickable link to a URL
    # goto=(n, x, y): add a clickable link to page n position (x,y)
    # goto=n: same as goto=(n, 0, 0)

    opac = 1.0 - transparent
    annot = None

    if "H" in mode:
        annot = page.add_highlight_annot(rect)
        annot.set_colors(stroke=color)
        annot.set_opacity(opac)

    if "U" in mode:
        annot = page.add_underline_annot(rect)
        annot.set_colors(stroke=color)
        annot.set_opacity(opac)

    if "X" in mode:
        annot = page.add_strikeout_annot(rect)
        annot.set_colors(stroke=color)
        annot.set_opacity(opac)

    if "S" in mode:
        annot = page.add_squiggly_annot(rect)
        annot.set_colors(stroke=color)
        annot.set_opacity(opac)

    if "T" in mode:
        # alternate method: an icon
        # point = rect[:2]  # top-left of highlight rect
        point = [rect[1], rect[2]] # top-right of highlight rect
        annot = page.add_text_annot(point, text, text_color=color, fill_color=fill_c, opacity=opac)

    if "P" in mode:
        # rect here is a point list to form a polygon (instead of a simle rect)
        if debug>1:
            print("add_polygon_annot: ", rect)
        annot = page.add_polygon_annot(rect)
        annot.set_colors(stroke=color, fill=fill_c)
        annot.set_opacity(opac)

    if "F" in mode:
        annot = page.add_freetext_annot(rect, text, fontsize=14, fontname="helv",
                                text_color=color, fill_color=fill_c, opacity=opac)

    if "+" in mode:
        if annot:
            # Tooltip popup (mouse-over text) for ocular.
            popup_rect = annot.rect + (10, -50, 100, -10)  # position above/beside
            annot.set_popup(popup_rect)
            # the above is needed for ocular, but not for evince.
            # FIXME: or maybe it has no effect at all?
        else:
            print("ERROR: Need one of the mode letters H U X S T F togehter with P")

    if len(text):
        info = annot.info
        info["title"] = "pdfcompare"    # Okular: displayed as "Autor: pdfcompare"
        # info["subject"] = "Insert"    # Okular: only visible when "open Note"
        info["content"] = text          # have to repeat the text here, else it is removed.
        annot.set_info(info)
    else:
        hide_annotation_popup(page, annot)

    if href:
        # in case of polygon, we need to compute the boundig box of the rect object, which is actually a polygon.
        page.insert_link({"kind": mu.LINK_URI, "from": annot.rect, "uri": href})

    if goto:
        # in case of polygon, we need to compute the boundig box of the rect object, which is actually a polygon.
        point = (100,100)
        if type(goto) == type([]):
            point = (goto[1], goto[2])
            goto = goto[0]
        page.insert_link({"kind": mu.LINK_GOTO, "from": annot.rect, "to": point, "page": page})

    annot.update()


def hide_annotation_popup(page, a):
    # try to hide the popup
    a.set_info(title="", content="", subject="")    # all strings empty? does not work in okular
    a.set_popup(mu.Rect(0,0,0,0))                   # zero size? does not work in okular

    for a in page.annots():
        print("hide? ", a, a.type)
        if a.type[0] == "Popup" and a.parent == annot:
            print(" ... yes.")
            a.delete()


def r_bbox(rects):
    p = rects[:]
    for r in rects:
        p.append((r[2], r[3]))
    return bbox(p)


def bbox(points):
    xmin = points[0][0]
    xmax = points[0][0]
    ymin = points[0][1]
    ymax = points[0][1]
    for p in points:
        if p[0] < xmin: xmin = p[0]
        if p[0] > xmax: xmax = p[0]
        if p[1] < ymin: ymin = p[1]
        if p[1] > ymax: ymax = p[1]
    return (xmin, ymin, xmax, ymax)


def highlight_words_in_page(page, keywords):
    rects = []
    for k in keywords:
        rects.extend(page.search_for(k))
    if debug:
        print("✓ search_for")

    if rects:
        if debug:
            print(rects)
        highlight = page.add_highlight_annot(rects)
        highlight.set_colors(stroke=(1, 1, 0))  # yellow background
        highlight.update()
        if debug:
            print("✓ update")

        # Tooltip popup (mouse-over text) for ocular.
        popup_rect = highlight.rect + (10, -50, 100, -10)  # position above/beside
        highlight.set_popup(popup_rect)
        if debug:
            print("✓ highlight.set_popup")
        # the above is needed for ocular, but not evince.

        info = highlight.info
        if debug:
            print(info)
        info["content"] = f"Found keyword: {keywords}"
        info["name"] = "FishMonster"
        info["title"] = "AuthorName"
        info["subject"] = "Subject line"
        info["creationDate"] = "2026-01-27"
        info["modDate"] = "2026-01-28"
        highlight.set_info(info)
        if debug:
            print("✓ set_info")
        if debug:
            print(highlight.info)
        highlight.set_opacity(0.5)  # 1.0 = fully opaque, 0.0 = invisible
        if debug:
            print("✓ set_opacity")
        #highlight.set_open(False)
        #print("✓ set_open")
        highlight.update()
        if debug:
            print("✓ update")

        # alternate method:
        point = highlight.rect.tr  # top-right of first highlight rect
        text_annot = page.add_text_annot(point, "add_text_annot tooltip")
        text_annot.set_opacity(0.9)  # visibility: none 0..1 full
        text_annot.update()


def save_file(name, doc, no_compression=False):
    doc.save(name, garbage=4, deflate=(not no_compression))
    doc.close()
    if debug:
        print(f"{name} created with highlights + tooltips")



def main():
    global debug
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
    parser.add_argument("--dump-words", metavar="DUMPFILE",
                        help="only dump a wordlist, similar to pdf2text.")
    parser.add_argument("-l", "--log",  metavar="LOGFILE",
                        help="Write an python datastructure describing all the overlay objects on each page. Default none.")
    parser.add_argument("-m", "--mark", metavar="OPS", default=parser.def_marks,
                        help="Specify what to mark. Used with -c. Allowed values are 'add','delete','change','equal'. \
                              Multiple values can be listed comma-seperated; abbreviations are allowed.\
                              Default: " + str(parser.def_marks))
    parser.add_argument("-n", "--no-op", "--no-output", default=False, action="store_true",
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
#    parser.add_argument("--strict", default=False, action="store_true", help="Show really all differences. Default: ignore removed hyphenation; ignore character spacing inside a word.")
    parser.add_argument("-t", "--transparency", type=float, default=parser.def_trans, metavar="TRANSP",
                        help="Set transparency of the highlight; invisible: 0.0; full opaque: 1.0; \
                        default: " + str(parser.def_trans))
#    parser.add_argument("-B", "--below", default=parser.def_below, action="store_true",
#                        help="Paint the highlight markers below the text. Try this if the normal merge crashes. Use with care, highlights may disappear below background graphics. Default: BELOW='"+str(parser.def_below)+"'.")
#    parser.add_argument("-C", "--search-color", metavar="NAME=R,G,B", action="append",
#                        help="Set colors of the search highlights as an RGB triplet; R,G,B ranges are 0.0-1.0 each; valid names are 'add,'delete','change','equal','margin','all'; default name is 'equal', which is also used for -s; default colors are " +
#                        " ".join(["%s=%s,%s,%s /*%s*/ " %(x_y[0],x_y[1][0],x_y[1][1],x_y[1][2],x_y[1][3]) for x_y in list(parser.def_colors.items())]))
    parser.add_argument("-D", "--debug", default=False, action="store_true",
                        help="Enable debugging. Print more on stdout. See also --log.")
    parser.add_argument("-Q", "--quiet", default=False, action="store_true",
                        help="Be quiet. Print nothing on stdout, unless there is an error.")
    parser.add_argument("-F", "--first-page", metavar="FIRST_PAGE",
                        help="Skip some pages at start of document; see also -L option. Default: all pages.")
    parser.add_argument("-L", "--last-page", metavar="LAST_PAGE",
                        help="Limit pages processed; this counts pages starting with 0. It does not use document \
                        page numbers; see also -F; default: all pages.")
#    parser.add_argument("-M", "--margins", metavar="N,E,W,S", default=parser.def_margins,
#                        help="Specify margin space to ignore on each page. A margin width is expressed \
#                        in units of ca. 100dpi. Specify four numbers in the order north,east,west,south. Default: "\
#                        + str(parser.def_margins))
#    parser.add_argument("-S", "--source-location", default=False, action="store_true",
#                        help="Annotation start includes :pNX: markers where 'N' is the page number of the location \
#                              in the original document and X is 't' for top, 'c' for center, or 'b' for bottom of the page. \
#                              Default: Annotations start only with 'chg:', 'add:', 'del:' optionally followed by original text.")
    parser.add_argument("-V", "--version", default=False, action="store_true",
                        help="Print the version number and exit.")
    parser.add_argument("-H", "--hide-popups", default=False, action="store_true",
                        help="Try to hide annotation popups. Does not work in okular.")
    parser.add_argument("-X", "--no-compression", default=False, action="store_true",
                        help="Write uncompressed PDF. Default: FlateEncode filter compression.")
    parser.add_argument("--leftside", default=False, action="store_true",
                        help="Put changebars and navigation at the left hand side of the page. Default: right hand side.")
    parser.add_argument("infile", metavar="INFILE", help="The input file.")
    parser.add_argument("infile2", metavar="INFILE2", nargs="?", help="Optional 'newer' input file; alternate syntax to -c")

    args = parser.parse_args()      # --help is automatic
    if args.version: parser.exit(__VERSION__)
    if args.debug: debug += 1
    if args.quiet: debug = 0
    args.transparency = 1 - args.transparency     # it is needed reversed.

    if args.dump_words:
        f1 = load_file(args.infile, firstpage=args.first_page, lastpage=args.last_page)
        flat = flatten(f1['words'])
        with open(args.dump_words, mode="w", encoding='utf-8') as fp:
            for page,idx,rec in flat:
                print(rec[4], file=fp)
        sys.exit(0)

    if args.infile2 and args.compare_text:
        parser.exit("Specify either -c and one file, or specify two files and no -c.")

    if args.compare_text:
        args.infile2 = args.infile
        args.infile = args.compare_text

    if not args.infile2:
        parser.exit("Need a second file to compare with")

    if not os.access(args.infile, os.R_OK):
        parser.exit("Cannot read input file: %s" % args.infile)

    if debug > 1:
        print(args.infile, args.infile2)

    # f1 = { "doc": doc, "text": text, "words": words, "fonts": fonts }
    f1 = load_file(args.infile, firstpage=args.first_page, lastpage=args.last_page)
    f2 = load_file(args.infile2, firstpage=args.first_page, lastpage=args.last_page)

    old_flat = flatten(f1['words'])
    new_flat = flatten(f2['words'])

    if args.log:
        with open(args.log, mode="w", encoding='utf-8') as fp:
            json.dump(old_flat, fp, indent=2)
            fp.write("\n# -----------------------\n")
        with open(args.log, mode="a", encoding='utf-8') as fp:
            json.dump(new_flat, fp, indent=2)

    old_strings = [rec[4] for _, _, rec in old_flat]
    new_strings = [rec[4] for _, _, rec in new_flat]

    if debug:
        print("SequenceMatcher(len=%d, len=%d) ... " % (len(old_strings), len(new_strings)))
    seqmatch = difflib.SequenceMatcher(None, old_strings, new_strings, autojunk=False)
    if debug > 1:
        print(" ... get_matching_blocks() ...")
    seqmatch.get_matching_blocks()
    if debug > 1:
        print(" ... get_opcodes() ...")
    seqmatch.get_opcodes()
    if debug:
        print(" ... done: found %d opcodes" % len(seqmatch.opcodes))

    if args.log:
        with open(args.log, mode="a", encoding='utf-8') as fp:
            print("\n# -----------------------", file=fp)
            log_opcodes(fp, old_flat, new_flat, seqmatch.opcodes)

    if not args.no_op:
        if False:
            # highlight_words_in_page(f1["doc"][0], ["LEVEL", "of", "the"])
            # add_annotation(f2['doc'][0], "Hello, world!", (200, 500, 280, 520), color=(1, 0, 0))
            add_annotation(f2['doc'][0], "mode=S red", (200, 100, 280, 120), mode='S', color=(1, 0, 0))
            add_annotation(f2['doc'][0], "mode=HP green", (200, 150, 280, 170), mode='H+', color=(0, 1, 0))
            add_annotation(f2['doc'][0], "m=F cyan", (200, 200, 280, 220), mode='F', color=(1,0,1))

            rects = [
                    (508, 279, 539, 293), (130, 291, 175, 302), (178, 291, 221, 305), (224,291,237,305), (239, 291, 242, 305),
                ]
            for r in rects:
                add_annotation(f2['doc'][0], rect=[(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])], text="rect", mode='P')
            add_annotation(f2['doc'][0], rect=text_rects2polygon(rects, pad=2), mode='P', fill_c=None)
        else:
            mark_opcodes(f2["doc"], old_flat, new_flat, seqmatch.opcodes, args.hide_popups)
        save_file(args.output, f2["doc"], args.no_compression)


if __name__ == "__main__":
    main()

