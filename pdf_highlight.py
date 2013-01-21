#! /usr/bin/python
#
# pdf_highlight.py -- command line tool to show search or compare results in a PDF
#
# (c) 2012-2013 Juergen Weigert jw@suse.de
# Distribute under GPL-2.0 or ask
#
# 2012-03-16, V0.1 jw - initial draught: argparse, pdftohtml-xml, font.metrics
# 2012-03-20, V0.2 jw - all is there, but the coordinate systems of my overlay 
#                       does not match. Sigh.
# 2013-01-12, V0.3 jw - support encrypted files added,
#                       often unencrypted is actually encrypted with key=''
#                     - coordinate transformation from xml to pdf canvas added
#                     - refactored: xml2wordlist, xml2fontinfo, create_mark
#                     - added experimental zap_letter_spacing()
# 2013-01-13, V0.4 jw - added class DecoratedWord
#                     - option --compare works!
# 2013-01-14, V0.5 jw - added xmlfile2wordlist, textfile2wordlist. fixed -e
#                     - added option --mark A,D,C
# 2013-01-15, V0.6 jw - added anno_popup() and friends. Horrible hack.
#                     - Added option --no-anno
#                     - With -c: added line counting to xml input
#                       top/center/bottom indicator for pdf.
# 2013-01-16, V0.7 jw - minor bugfixing.
#                     - Added Changemarks by: page_watermark().
#                     - /Creator /Producer /ModDate writing.
# 2013-01-17, V0.8 jw - added opcodes_post_proc() to make replace operations 
#                       more the human friendly.
#                     - calling compressContentStreams() unless --no-compression
#                     - higher --transparency is now more transparent, not less.
#                     - delete markers at end of previous text, not start of next.
# 2013-01-18, V0.9 jw - hit statistics +-~= added
#                     - page break indicators in catwords() added
#                     - new option -F -first-page added.
#                     - line wrapping for okular popups, if over 60 chars.
#                     - added page break markers in annotations.
#                     - smaller files: we merge once, and help ourselves with /Annots.
#
# osc in devel:languages:python python-pypdf >= 1.13+20130112
#  need fix from https://bugs.launchpad.net/pypdf/+bug/242756
# osc in devel:languages:python python-reportlab
# osc in devel:languages:python python-pygame
# osc in X11:common:Factory poppler-tools 
#
# needs module difflib from python-base
#
# Feature request:
# - poppler-tools:/usr/bin/pdftohtml -xml should report a rotation angle, 
#   if text is not left-to-right. And it should report spacing adjustements 
#   within a string.
#
# TODOs: see exra file TODO.md 

__VERSION__ = '0.9'

from cStringIO import StringIO
from pyPdf import PdfFileWriter, PdfFileReader, generic as Pdf
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color

import re, time
from pprint import pprint
import xml.etree.cElementTree as ET
import sys, os, subprocess
from argparse import ArgumentParser
import pygame.font as PGF
from difflib import SequenceMatcher

# I fail to understand the standard encode() decode() methods.
# But the codecs module always does what I mean.
import codecs

# allow debug printing into less:
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
debug = False

# from pdfminer.fontmetrics import FONT_METRICS
# FONT_METRICS['Helvetica'][1]['W']
#  944

def page_changemarks(canvas, mediabox, marks, trans=0.5, cb_x=0.98,cb_w=0.007, min_w=0.01, ext_w=0.05, anno=True):
  # cb_x=0.98 changebar on right margin
  # cb_x=0.02 changebar on left margin
  # min_w=0.05: each mark is min 5% of the page width wide. If not we add extenders.

  # mediabox [0, 0, 612, 792], list of 4x float or FloatObject
  # FloatObject does not support arithmetics with float. Needs casting. Sigh.
  # marks = { h:1188, w:918, x:0, y:0, rect: [{x,y,w,h,t},...], nr:1 }
  def x2c(x):
    return (0.0+x*float(mediabox[2])/marks['w'])
  def w2c(w):
    return (0.0+w*float(mediabox[2])/marks['w'])
  def y2c(y):
    return (0.0+float(mediabox[3])-y*float(mediabox[3])/marks['h'])
  def h2c(h):
    return (0.0+h*float(mediabox[3])/marks['h'])

  def anno_popup(canv, x,y, w,h, mark):
    # We misuse linkURL() as this is the only annotation, that a) can be written with reportlab() and b)
    # works both in acroread and ocular. HACK: For acroread, we include .: at the beginning, this prevents
    # file://full_path expansion on strings that do not look like urls.
    text = mark.get('t', '.') + ':'
    if mark.has_key('o'):
      if type(mark['o']) == list:
        text += mark['o'][1]+': '+ mark['o'][0]
      else:
        text += ' '+mark['o']
    # need ascii here. anything else triggers
    # UnicodeDecodeError: 'utf16' codec can't decode bytes in position 5484-5485: illegal UTF-16 surrogate
    # from File "/usr/lib/python2.7/site-packages/pyPdf/generic.py", line 248, in createStringObject
    text = text.encode('ascii', errors='replace')
    canv.linkURL(text, (x, y, x+w, y+h), relative=0) # , Border="[ 1 1 1 ]")
  
  cb_x = (cb_x-0.5*cb_w) * marks['w']     # relative to pdf page width 
  cb_w = cb_w            * marks['w']     # relative to pdf page width 
  min_w = min_w          * float(mediabox[2])    # relative to xml page width 
  ext_w = ext_w          * float(mediabox[2])    # extenders, if needed

  canvas.setFont('Helvetica',5)
  ### a testing grid
  if debug:
    for x in range(0,13):
      for y in range(0,50):
        canvas.drawString(50*x,20*y,'.(%d,%d)' % (50*x,20*y))
  if debug: canvas.setFont('Helvetica',16)
  for m in marks['rect']:
    canvas.setFillColor(Color(m['c'][0],m['c'][1],m['c'][2], alpha=trans))
    canvas.setStrokeColor(Color(m['c'][0],m['c'][1],m['c'][2], alpha=0.5*trans))
    # m = {'h': 23, 'c': [1,0,1], 't': 'Popular', 'w': 76.56716417910448, 'x': 221.0, 'y': 299}
    (x,y,w,h) = (m['x'], m['y'], m['w'], m['h'])
    if w < min_w:
      if debug: print "min_w:%s (%s)" % (min_w, w)
      canvas.rect(x2c(x-ext_w),y2c(y+0.2*h), w2c(w+2*ext_w),h2c(0.2*h), fill=1, stroke=0)
      canvas.rect(x2c(x-ext_w),y2c(y-1.2*h), w2c(w+2*ext_w),h2c(0.2*h), fill=1, stroke=0)
      x = x - (0.5 * (min_w-w))
      canvas.rect(x2c(x),y2c(y),w2c(min_w),h2c(h*1.2), fill=1, stroke=0)
      if anno:
        anno_popup(canvas, x2c(x),y2c(y),    w2c(min_w),h2c(h*1.4), m)
    else:
      # multiply height h with 1.4 to add some top padding, similar
      # to the bottom padding that is automatically added
      # due to descenders extending across the font baseline.
      # 1.2 is often not enough to look symmetric.
      canvas.rect(x2c(x),y2c(y),    w2c(w),h2c(h*1.4), fill=1, stroke=0)
      if anno:
        anno_popup(canvas, x2c(x),y2c(y),    w2c(w),h2c(h*1.4), m)

    # change bar
    canvas.rect(x2c(cb_x),  y2c(y),w2c(cb_w),  h2c(h*1.4), fill=1, stroke=1)
    if debug:
      canvas.drawString(x2c(x),y2c(y),'.(%d,%d)%s(%d,%d)' % (x2c(x),y2c(y),m['t'],x,y))
      pprint(m)
      return      # shortcut, only the first word of the page

def page_watermark(canvas, box, argv, color=[1,0,1], trans=0.5):
  canvas.setFont('Helvetica',5)
  av = []
  for arg in argv:
    m=re.match("\S\S\S\S+(/.*?)$", arg)
    if m: arg = "..."+m.group(1)
    av.append(arg)
  text = "Changemarks by: " + " ".join(av)
  canvas.setFillColor(Color(color[0],color[1],color[2], alpha=trans))
  canvas.drawString(15,10,text)


def pdf2xml(parser, infile, key=''):
  """ read a pdf file with pdftohtml and parse the resulting xml into a dom tree
      the first parameter, parser is only used for calling exit() with proper messages.
  """
  pdftohtml_cmd = ["pdftohtml", "-q", "-i", "-nodrm", "-nomerge", "-stdout", "-xml"]
  if len(key):
    pdftohtml_cmd += ["-upw", key]
  try:
    (to_child, from_child) = os.popen2(pdftohtml_cmd + [infile])
  except Exception,e:
    parser.exit("pdftohtml -xml failed: " + str(e))

  try:
    dom = ET.parse(from_child)
  except Exception,e:
    parser.exit("pdftohtml -xml failed.\nET.parse: " + str(e) + ")\n\n" + parser.format_usage())
  print "pdf2xml done"
  return dom

class DecoratedWord(list):
  def __eq__(a,b):
    return a[0] == b[0]
  def __hash__(self):
    return hash(self[0])

def xmlfile2wordlist(fname):
  """ works well with xml from pdftohtml -xml.
      """
  wl = []
  elementcount = 0

  #tree= ET.parse(fname)
  #dom = tree.getroot()
  #for elem in dom.iter():

  ## line number counting idea from 
  ## http://bytes.com/topic/python/answers/535191-elementtree-line-numbers-iterparse
  class FileWrapperLineNo:
    def __init__(self, source):
      self.source = source
      self.lineno = 0
    def read(self, bytes):
      s = self.source.readline()
      self.lineno += 1
      return s

  f = FileWrapperLineNo(open(fname))
  for event, elem in ET.iterparse(f, events=("start", "end")):
    if event == "start":
      elementcount += 1
      ## we could grab all from the root element, 
      ## but we want to count elements.
      # t = "".join(elem.itertext())
      if elem.text:
        for w in elem.text.split():
          wl.append(DecoratedWord([w,None,None,{'e':elementcount, 'l':f.lineno}]))
  return wl

def textfile2wordlist(fname):
  """ CAUTION if you create your text files with pdftotxt, 
      things may appear in different ordering than with pdftohtml, resulting
      in an enormous diff.
      """
  wl = []
  lnr = 0
  # assume .txt files are utf8 encoded, but please survive binary garbage.
  f = codecs.open(fname, 'r', 'utf-8', errors='ignore')
  while True:
    line = f.readline()
    if len(line)==0: break
    lnr += 1
    for w in line.split():
      wl.append(DecoratedWord([w,None,None,{'l':lnr}]))
  f.close()
  return wl
  
def textline2wordlist(text, context):
  """returns a list of 4-element lists like this:
     [word, text, idx, context]
     where the word was found in the text string at offset idx.
     words are defined as any printable text delimited by whitespace.
     just as str.split() would do.
     Those 4-element lists are cast into DecoratedWord.
     The DecoratedWord type extends the list type, so that it is hashable and
     comparable using only the "word" which is the first element of the four. 
     Thus our wordlists work well as sequences with difflib, although they also
     transport all the context to compute exact page positions later.
  """

  wl = []
  idx = 0
  tl = re.split("(\s+)", text)
  while True:
    if len(tl)==0: break
    head = tl.pop(0)
    if len(head):
      wl.append(DecoratedWord([head, text, idx, context]))
    if len(tl)==0: break
    sep = tl.pop(0)
    idx += len(sep)+len(head)
  return wl
  
def xml2wordlist(dom, first_page=None, last_page=None):
  """input: a dom tree as generated by pdftohtml -xml.
     output: a wordlist with all the metadata so that the exact coordinates
             of each word can be calculated.
  """
  ## Caution: 
  # <text font="1" height="14" left="230" top="203" width="635">8-bit microcontroller based on the AVR enhanced RISC architecture. By executing powerful</text>
  # <text font="1" height="14" left="230" top="223" width="635">i n s t r u c t i o n s   i n   a   s i n g l e   c l o c k   c y c l e ,   t h e</text>
  ## pdftohtml -xml can return strings where each letter is padded with a whitespace. 
  ## zap_letter_spacing() handles this (somewhat)
  ## Seen in atmega164_324_644_1284_8272S.pdf

  if first_page is None: first_page = 0
  wl=[]
  p_nr = 0
  for p in dom.findall('page'):
    if not last_page is None:
      if p_nr >= int(last_page):
        break
    if p_nr < int(first_page):
      next
    p_nr += 1
    p_h = float(p.attrib['height'])

    for e in p.findall('text'):
      # <text font="0" height="19" left="54" top="107" width="87"><b>Features</b></text>
      x=e.attrib['left']
      y=e.attrib['top']
      w=e.attrib['width']
      h=e.attrib['height']
      f=e.attrib['font']
      text = ''
      for t in e.itertext(): text += t

      ## crude top,center,bottom location
      if   float(y) > 0.66*p_h: l = 'b'
      elif float(y) > 0.33*p_h: l = 'c'
      else:                     l = 't'
      wl += textline2wordlist(text, {'p':p_nr, 'l':l, 'x':x, 'y':y, 'w':w, 'h':h, 'f':f})
    #pprint(wl)
  print "xml2wordlist: %d pages" % (p_nr-int(first_page))
  return wl

def xml2fontinfo(dom, last_page=None):
  finfo = [None]      # each page may add (or overwrite?) some fonts
  p_finfo = {}
  p_nr = 0
  for p in dom.findall('page'):
    if not last_page is None:
      if p_nr >= int(last_page):
        break
    p_nr += 1
    p_finfo = p_finfo.copy()
    # print "----------------- page %s -----------------" % p.attrib['number']

    for fspec in p.findall('fontspec'):
      fname = fspec.attrib.get('family', 'Helvetica')
      fsize = fspec.attrib.get('size', 12)
      f_id  = fspec.attrib.get('id')
      f_file = PGF.match_font(fname)
      ######
      # On openSUSE 12.1 Beta 1 (i586,fossy) the call to PGF.Font() triggers this warning:
      # /usr/lib/python2.7/site-packages/pygame/pkgdata.py:27: UserWarning:
      # Module argparse was already imported from
      # /usr/lib/python2.7/argparse.pyc, but /usr/lib/python2.7/site-packages
      # is being added
      f = PGF.Font(f_file, int(0.5+float(fsize)))
      p_finfo[f_id] = { 'name': fname, 'size':fsize, 'file': f_file, 'font':f }
    #pprint(p_finfo)
    finfo.append(p_finfo)
  return finfo


def main():
  parser = ArgumentParser(epilog="version: "+__VERSION__, description="highlight words in a PDF file.")
  parser.def_trans = 0.5
  parser.def_decrypt_key = ''
  parser.def_sea_col = ['pink', [1,0,1]]
  parser.def_add_col = ['green',  [0.3,1,0.3]]
  parser.def_del_col = ['red',    [1,.3,.3]]
  parser.def_chg_col = ['yellow', [.9,.8,0]]
  parser.def_output = 'output.pdf'
  parser.def_mark= 'A,D,C'
  parser.add_argument("-o", "--output", metavar="OUTFILE", default=parser.def_output,
                      help="write output to FILE; default: "+parser.def_output)
  parser.add_argument("-s", "--search", metavar="WORD_REGEXP", 
                      help="highlight only WORD_REGEXP")
  parser.add_argument("-d", "--decrypt-key", metavar="DECRYPT_KEY", default=parser.def_decrypt_key,
                      help="open an encrypted PDF; default: KEY='"+parser.def_decrypt_key+"'")
  parser.add_argument("-c", "--compare-text", metavar="OLDFILE",
                      help="mark added, deleted and replaced text (or see -m) with regard to OLDFILE. \
                            File formats .pdf, .xml, .txt are recognized by their suffix. \
                            The comparison works word by word.")
  parser.add_argument("-m", "--mark", metavar="OPS", default=parser.def_mark,
                      help="specify what to mark. Used with -c. Allowed values are 'add','delete','change','equal'. \
                            Multiple values can be listed comma-seperated; abbreviations are allowed.\
                            Default: " + str(parser.def_mark))
  parser.add_argument("-e", "--exclude-irrelevant-pages", default=False, action="store_true",
                      help="with -s: show only matching pages; with -c: show only changed pages; \
                      default: reproduce all pages from INFILE in OUTFILE")
  parser.add_argument("-i", "--nocase", default=False, action="store_true",
                      help="make -s case insensitive; default: case sensitive")
  parser.add_argument("-A", "--no-anno", default=False, action="store_true",
                      help="This option prevents adding Annotations to the output PDF file. \
                      Default: annotate each Mark with 'operation:position: orignal_text'")
  parser.add_argument("-L", "--last-page", metavar="LAST_PAGE",
                      help="limit pages processed; this counts pages, it does not use document \
                      page numbers; see also -F; default: all pages")
  parser.add_argument("-F", "--first-page", metavar="FIRST_PAGE",
                      help="skip some pages at start of document; see also -L; default: all pages")
  parser.add_argument("-t", "--transparency", type=float, default=parser.def_trans, metavar="TRANSP", 
                      help="set transparency of the highlight; invisible: 0.0; full opaque: 1.0; \
                      default: " + str(parser.def_trans))
  parser.add_argument("-D", "--debug", default=False, action="store_true",
                      help="enable debugging. Prints more on stdout, dumps several *.xml or *.pdf files.")
  parser.add_argument("-V", "--version", default=False, action="store_true",
                      help="print the version number and exit")
  parser.add_argument("-X", "--no-compression", default=False, action="store_true",
                      help="write uncompressed PDF. Default: FlateEncode filter compression.")
  parser.add_argument("-C", "--search-color", default=parser.def_sea_col[1], nargs=3, metavar="N",
                      help="set color of the search highlight as an RGB triplet; default is %s: %s" 
                      % (parser.def_sea_col[0], ' '.join(map(lambda x: str(x), parser.def_sea_col[1])))
                      )
  parser.add_argument("infile", metavar="INFILE", help="the input filename")
  args = parser.parse_args()      # --help is automatic

  args.transparency = 1 - args.transparency     # it is needed reversed.

  if args.version: parser.exit(__VERSION__)
  debug = args.debug

  ## TEST this, fix or disable: they should work well together:
  # if args.search and args.compare_text:
  #   parser.exit("Usage error: -s search and -c compare are mutually exclusive, try --help")

  if args.search is None and args.compare_text is None:
    parser.exit("Oops. Nothing to do. Specify either -s or -c")

  if not os.access(args.infile, os.R_OK):
    parser.exit("Cannot read input file: %s" % args.infile)
  dom1 = pdf2xml(parser, args.infile, args.decrypt_key)
  dom2 = None
  wordlist2 = None
  if args.compare_text:
    if re.search('\.pdf$', args.compare_text, re.I):
      dom2 = pdf2xml(parser, args.compare_text, args.decrypt_key)
      wordlist2 = xml2wordlist(dom2, args.first_page, args.last_page)
    elif re.search('\.xml$', args.compare_text, re.I):
      wordlist2 = xmlfile2wordlist(args.compare_text)
    else:
      # assuming a plain text document
      wordlist2 = textfile2wordlist(args.compare_text)

  if debug:
    dom1.write(args.output + ".1.xml")
    if dom2:
      dom2.write(args.output + ".2.xml")

  PGF.init()
  # This pygame.font module is used to calculate widths of all glyphs
  # for words we need to mark. With this calculation, we can determine 
  # the exact position and length of the marks, if the marked word is 
  # only a substring (which it often is).
  # For complete strings, we get the exact positions and size from pdftohtml -xml.
  # Strings returned by pdftohtml are combinations of multiple PDF text fragments.
  # This is good, as pdftohtml reassembles words and often complete lines in a perfectly 
  # readable way. 
  # The downside of this is, that the width and position calculation may be
  # a bit off, due to uneven word-spacing or letter-spacing in the original PDF text line.
  ####
  # f = PGF.Font(PGF.match_font('Times'), 13))
  # f.metrics("Bernoulli") 
  #  [(0, 8, 0, 9, 9), (0, 7, 0, 6, 6), (-1, 5, 0, 6, 4), (-1, 6, 0, 6, 6), (0, 7, 0, 6, 7), (0, 6, 0, 6, 6), (-1, 3, 0, 9, 3), (-1, 3, 0, 9, 3), (-1, 3, 0, 9, 3)]
  # (minx, maxx, miny, maxy, advance)

  input1 = PdfFileReader(file(args.infile, "rb"))
  if input1.getIsEncrypted():
    if input1.decrypt(args.decrypt_key):
      if len(args.decrypt_key):
        print "Decrypted using key='%s'." % args.decrypt_key
    else:
      parser.exit("decrypt(key='%s') failed." % args.decrypt_key)

  last_page = input1.getNumPages()
  first_page = 0
  if args.last_page and int(args.last_page) < last_page:
    last_page = int(args.last_page)
  if args.first_page:
    first_page = int(args.first_page)
    if first_page > last_page:
      first_page = last_page
  print "input pages: %d-%d" % (first_page, last_page)

  page_marks = pdfhtml_xml_find(dom1, re_pattern=args.search, 
      wordlist=wordlist2,
      nocase=args.nocase,
      first_page=first_page,
      last_page=last_page,
      mark_ops=args.mark,
      ext={'a': {'c':parser.def_add_col[1]},
           'd': {'c':parser.def_del_col[1]},
           'c': {'c':parser.def_chg_col[1]},
           'e': {'c':args.search_color} })

  # pprint(page_marks[0])

  output = PdfFileWriter()
  # Evil hack: there is no sane way to transport DocumentInfo metadata.
  #          : This is the insane way, we duplicate this code from
  #          : PdfFileWriter.__init__()
  # FIXME: We should also copy the XMP metadata from the document.
  try:
    di = input1.getDocumentInfo()

    # update ModDate, Creator, DiffCmd
    selfcmd = " ".join(sys.argv) + ' # V' + __VERSION__ + ' ' + time.ctime()
    if not di.has_key('/Creator'):
      di[Pdf.NameObject('/Creator')] = Pdf.createStringObject(selfcmd)
    elif not di.has_key('/Producer'):
      di[Pdf.NameObject('/Producer')] = Pdf.createStringObject(selfcmd)
    di[Pdf.NameObject('/DiffCmd')] = Pdf.createStringObject(selfcmd)
    di[Pdf.NameObject('/ModDate')] = Pdf.createStringObject(time.strftime("D:%Y%m%d%H%M%S"))
    if debug:
      print "DocumentInfo():"
      pprint(di)
    output._objects.append(di)
  except Exception,e:
    print("WARNING: getDocumentInfo() failed: " + str(e) );

  output._info = Pdf.IndirectObject(len(output._objects), 0, output)

  pages_written = 0

  for i in range(first_page,last_page):
    if args.exclude_irrelevant_pages and len(page_marks[i]['rect']) == 0:
      continue
    hitdetails = {'equ':0, 'add':0, 'del':0, 'chg':0 }
    for r in page_marks[i]['rect']:
      tag = r.get('t','unk')
      if not hitdetails.has_key(tag):
        hitdetails[tag] = 0
      hitdetails[tag] += 1
    hits_fmt = ''
    for det,ch in (['add','+'], ['del','-'], ['chg','~'], ['equ','=']):
      if hitdetails[det]: hits_fmt += '%s%d' % (ch,hitdetails[det])

    print " page %d: %d hits %s" % (page_marks[i]['nr'], len(page_marks[i]['rect']), hits_fmt)
    # pprint(hitdetails)

    page = input1.getPage(i)
    box = page['/MediaBox']     # landscape look like [0, 0, 794, 595]

    ## create a canvas of correct size, 
    ## paint semi-transparent highlights on the canvas,
    ## then save the canvas to memory string as proper PDF,
    ## merge this string ontop of the original page.
    pdf_str = StringIO()
    c = canvas.Canvas(pdf_str, pagesize=(box[2],box[3]))
    page_watermark(c, box, sys.argv, color=args.search_color, trans=args.transparency)
    page_changemarks(c, box, page_marks[i], trans=args.transparency, anno=not args.no_anno)

    # c.textAnnotation('Here is a Note', Rect=[34,0,0,615], addtopage=1,Author='Test Opacity=0.1',Color=[0.7,0.8,1],Type='/Comment',Opacity=0.1)
    # c.linkURL(".: Here is a Note", (30,10,200,20), relative=0, Border="[ 1 1 1 ]")

    c.save()
    pdf_str.seek(0,0)
    if debug:
      file("canvas_%d.pdf"%i, 'w').write(pdf_str.getvalue())
      pdf_str.seek(0,0)
    input2 = PdfFileReader(pdf_str)
    highlight_page = input2.getPage(0)
    if 0:
      ## We can paint below or above the document.
      ## Below looks better, as the fonts are true black,
      ## but fails completely, if white background is drawn.
      ## Thus the highlight_page must be on top.
      ##
      highlight_page.mergePage(page)
      if not args.no_compression:
        highlight_page.compressContentStreams()
      output.addPage(highlight_page)
    else:
      page.mergePage(highlight_page)
      if highlight_page.has_key("/Annots"):
        if page.has_key("/Annots"):
          print "Warning: Original Annotations overwritten. mergePage() cannot merge them."
        page[Pdf.NameObject("/Annots")] = highlight_page["/Annots"]
      if not args.no_compression:
        page.compressContentStreams()
      output.addPage(page)
    pages_written += 1

  outputStream = file(args.output, "wb")
  output.write(outputStream)
  outputStream.close()
  print "%s (%s pages) written." % (args.output, pages_written)



def rendered_text_width(str, font=None):
  """Returns the width of str, in font units.
     If font is not specified, then len(str) is returned.
     """
  if (font is None): return len(str)
  if (len(str) == 0): return 0
  return sum(map(lambda x: x[4], font.metrics(str)))

def rendered_text_pos(string1, char_start, char_count, font=None, xoff=0, width=None):
  """Returns a tuple (xoff2,width2) where substr(string1, ch_start, ch_count) will be rendered
     in relation to string1 being rendered starting at xoff, and being width units wide.

     If font is specified, it is expected to have a metrics() method returning a tuple, where 
     the 5th element is the character width, e.g. a pygame.font.Font().
     Otherwise a monospace font is asumed, where all characters have width 1.

     If width is specified, it is used to recalculate positions so that the entire string1 fits in width.
     Otherwise the values calculated by summing up font metrics by character are used directly.
     """
  pre = string1[:char_start]
  str = string1[char_start:char_start+char_count]
  suf = string1[char_start+char_count:]

  pre_w = rendered_text_width(pre, font)
  str_w = rendered_text_width(str, font)
  suf_w = rendered_text_width(suf, font)
  ratio = 1

  if (width is not None): 
    tot_w = pre_w+str_w+suf_w
    if (tot_w == 0): tot_w = 1
    ratio = float(width)/tot_w
  #pprint([[pre,str,suf,width],[pre_w,str_w,suf_w,tot_w],ratio])
  return (xoff+pre_w*ratio, str_w*ratio)

def create_mark(text,offset,length, font, t_x, t_y, t_w, t_h, ext={}):
  #print "word: at %d is '%s'" % (offset, text[offset:offset+length]),
    
  (xoff,width) = rendered_text_pos(text, offset, length,
                          font, float(t_x), float(t_w))
  #print "  xoff=%.1f, width=%.1f" % (xoff, width)

  mark = {'x':xoff, 'y':float(t_y)+float(t_h),
          'w':width, 'h':float(t_h), 't':text[offset:offset+length]}
  for k in ext:
    mark[k] = ext[k]
  return mark

def zap_letter_spacing(text):
  ###
  # <text font="1" height="14" left="230" top="223" width="635">i n s t r u c t i o n s   i n   a   s i n g l e   c l o c k   c y c l e ,   t h e</text>
  # Does not normally match a word. But xmltohtml -xml returns such approximate renderings for block justified texts.
  # Sigh. One would need to search for c\s*l\s*o\s*c\s*k to find clock there.
  # if every second letter of a string is a whitespace, then remove these extra whitespaces.
  ###
  l = text.split(' ')
  maxw = 0
  for w in l:
    if len(w) > maxw: maxw = len(w)
  if maxw > 1: return text

  # found whitespaces padding as seen in the above example.
  # "f o o   b a r ".split(' ')
  # ['f', 'o', 'o', '', '', 'b', 'a', 'r', '']
  t = ''
  for w in l:
    if len(w) == 0: w = ' '
    t += w
  #print "zap_letter_spacing('%s') -> '%s'" % (text,t)
  return t

def pdfhtml_xml_find(dom, re_pattern=None, wordlist=None, nocase=False, ext={}, first_page=None, last_page=None, mark_ops="D,A,C"):
  """traverse the XML dom tree, (which is expected to come from pdf2html -xml)
     find all occurances of re_pattern on all pages, returning rect list for 
     each page, giving the exact coordinates of the bounding box of all 
     occurances. Font metrics are used to interpolate into the line fragments 
     found in the dom tree.
     Keys and values from ext['e'] are merged into the DecoratedWord output for pattern matches.
     If re_pattern is None, then wordlist is used instead. 
     Keys and values from ext['a'], ext['d'], or ext['c'] respectively are merged into 
     the DecoratedWord output for added, deleted, or changed texts (respectivly).
     mark_ops defines which diff operations are marked.
  """

  ######
  def markword(r_dict, wl, idx, tag, attr, fontinfo):
    w = wl[idx]
    p_nr = w[3].get('p','?')
    l = len(w[0])
    off = w[2]
    if tag == 'delete': 
      # l=0 special case:
      # very small marker length triggers extenders.
      # decrement idx if idx > 0.
      #  if decrementable (idx > 1), place the marker at the end of the previous word, 
      #  not at the beginning of this word.
      if idx > 0:
         w = wl[idx-1]
         p_nr = w[3].get('p','?')
         off = w[2]+len(w[0])
      l = 0 

    mark = create_mark(w[1], off, l,
          fontinfo[p_nr][w[3]['f']]['font'], 
          w[3]['x'],w[3]['y'],w[3]['w'],w[3]['h'], attr)
    if not r_dict.has_key(p_nr): r_dict[p_nr] = []
    r_dict[p_nr].append(mark)

  def catwords(dw, idx1, idx2):
    text = ""
    llen=0
    ypos=None
    p_nr=None
    for w in dw[idx1:idx2]:
      if p_nr is None:
        p_nr = w[3]['p']
      if ypos is None:
        ypos = w[3]['y']
      if p_nr != w[3]['p']:
        p_nr = w[3]['p']
        text += " <br> --]page:%d[--" % int(p_nr)
        llen=1000 # fallthrough
      if llen > 100 or ypos != w[3]['y']:
        # silly hack for okular. It does not do line wrapping on its own.
        # evince and acroread do it. Okular wraps the line, when I say <br>, 
        # but the others will then print out "<br>". 
        # Please fix okular, someone.
        # These URL annotations are not meant to contain html code. 
        text += " <br> "
        llen = 0
        ypos = w[3]['y']
      elif llen > 0:
        text += " "
        llen += 1
      text += w[0]
      llen += len(w[0])
    if dw[idx1][3].has_key('p'):
      page_or_elem = 'p'+str(dw[idx1][3]['p'])
    elif dw[idx1][3].has_key('e'):
      page_or_elem = 'e'+str(dw[idx1][3]['e'])
    else:
      page_or_elem = '#'
    loc_or_lineno = dw[idx1][3].get('l','')
    if type(loc_or_lineno) == int:
      loc_or_lineno = 'l'+str(loc_or_lineno)
    return [text, page_or_elem+loc_or_lineno]
  ######

  fontinfo = xml2fontinfo(dom, last_page)

  ops = {}
  for op in mark_ops.split(','):
    ops[op[0].lower()] = 1

  p_rect_dict = {}   # indexed by page numbers, then lists of marks
  if wordlist:
    # generate our wordlist too, so that we can diff against the given wordlist.
    wl_new = xml2wordlist(dom, first_page, last_page)
    s = SequenceMatcher(None, wordlist, wl_new, autojunk=False)

    def opcodes_post_proc(iter_list):
      ## Often small pieces are replaced by big pieces or vice versa.
      ## For a concept of wordlist we want to replace n words with exactly n words.
      ## Excessive or missing words should be considered an adjacent insert or delete.
      ## get_opcodes() would never do that, as it will always produce one 'equal' beween 
      ## each other operation.
      ##
      ## I now officially love generators in python.
      ##
      for tag, i1, i2, j1, j2 in iter_list:
        if tag == "replace":
          i_len = i2-i1
          j_len = j2-j1
          if i_len < j_len:
            # print "getting longer by %d" % (j_len-i_len)
            yield ('replace',  i1,i2, j1,j1+i_len)
            yield ('insert',   i2,i2, j1+i_len,j2)
          elif i_len > j_len:
            # print "getting shorter by %d" % (i_len-j_len)
            yield ('replace', i1,i1+j_len, j1, j2)
            yield ('delete',  i1+j_len,i2, j2, j2)
          else:
            # same length
            yield (tag, i1, i2, j1, j2)
        else:
          yield (tag, i1, i2, j1, j2)

    for tag, i1, i2, j1, j2 in opcodes_post_proc(s.get_opcodes()):
      if tag == "equal":
        if (ops.has_key('e')):
          attr = ext['e'].copy()
          # no need to put the old text into attr['o'], it is unchanged.
          attr['t'] = 'equ'
        else:
          continue
      elif tag == "replace":
        if (ops.has_key('c')):
          attr = ext['c'].copy()
          attr['o'] = catwords(wordlist, i1, i2)
          attr['t'] = 'chg'
        else:
          continue
      elif tag == "delete":
        if (ops.has_key('d')):
          attr = ext['d'].copy()
          attr['o'] = catwords(wordlist, i1, i2)
          attr['t'] = 'del'
          j2 = j1 + 1     # so that the create_mark loop below executes once.
        else:
          continue
      elif tag == "insert":
        if (ops.has_key('a')):
          attr = ext['a'].copy()
          attr['t'] = 'add'
        else:
          continue
      else:
        print "SequenceMatcher returned unknown tag: %s" % tag
        continue
      # print "len(wl_new)=%d, j in [%d:%d] %s" % (len(wl_new), j1, j2,tag)
      for j in range(j1,j2):
        if j >= len(wl_new):    # this happens with autojunk=False!
          print "end of wordlist reached: %d" % j
          break
        markword(p_rect_dict, wl_new, j, tag, attr, fontinfo)

  # End of wordlist code.
  # We have now p_rect_dict preloaded with the wordlist marks or empty.
  # next loop through all pages, select the correct p_rect from the dict.
  # Start or continue adding re_pattern search results while if any.
  # Finally collect all in pages_a.in pages_a.
  pages_a = []
  p_nr = 0
  for p in dom.findall('page'):
    if not last_page is None:
      if p_nr >= int(last_page):
        break
    p_nr += 1

    p_rect = p_rect_dict.get(p_nr,[])
    if re_pattern:
      for e in p.findall('text'):
        p_finfo = fontinfo[p_nr]
        text = ''
        for t in e.itertext(): text += t
        text = zap_letter_spacing(text)
  
        #pprint([e.attrib, text])
        #print "search (%s)" % re_pattern
        flags = re.UNICODE
        if (nocase): flags |= re.IGNORECASE
        l = map(lambda x:len(x), re.split('('+re_pattern+')', text, flags=flags))
        l.append(0)       # dummy to make an even number.
        # all odd indices in l are word lengths, all even ones are seperator lengths
        offset = 0
        i = 0
        while (i < len(l)):
          # print "offset=%d, i=%d, l=%s" % (offset, i, repr(l))
          offset += l[i]
          if (l[i+1] > 0):
  
            p_rect.append(create_mark(text,offset,l[i+1], 
              p_finfo[e.attrib['font']]['font'], 
              e.attrib['left'], e.attrib['top'], 
              e.attrib['width'],e.attrib['height'], ext['e']))
    
            offset += l[i+1]
          i += 2
    pages_a.append({'nr':int(p.attrib['number']), 'rect':p_rect,
                 'h':float(p.attrib['height']), 'w':float(p.attrib['width']),
                 'x':float(p.attrib['left']), 'y':float(p.attrib['top'])})
  return pages_a

if __name__ == "__main__": main()

