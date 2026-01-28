#! /usr/bin/python3
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
# (C) 2026 jnweiger@gmail.com

# Universal PyMuPDF import with fallback cascade
mu = None

import sys
for name in ["fitz", "pymupdf"]:
    try:
        mu = __import__(name)
        break
    except ImportError:
        continue

if mu is None:
    raise ImportError("No PyMuPDF found. Install with:\n\t sudo apt install python3-pymupdf\n  OR\n\t pip install pymupdf")


# Now use mu consistently
doc = mu.open("input.pdf")
text = []
words = []
fonts = []
for pno in range(doc.page_count):
    text.append(doc.get_page_text(pno))
    words.append(doc[pno].get_text("words"))
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

print("✓ input.pdf")
page = doc[0]
keywords = ["Daisy", "by", "the"]
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


doc.save("output.pdf", garbage=4, deflate=True)
print("✓ save")
doc.close()
print("✓ output.pdf created with highlights + tooltips")
