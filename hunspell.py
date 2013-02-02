# hunspell.py -- a wrapper class for hunspell
#
# (c) 2013 Juergen Weigert jw@suse.de
# Distribute under GPL-2.0 or ask
#
# 2013-01-31, V0.1 jw - initial draught: word by word I/O
# 2013-02-01, V0.1 jw - added own _readline() to use buffering. Pythons readline()
#                       does single byte read()s, which is slow.
# 2013-02-02, V0.2 jw - check_words() now remembers a wordlist, pushes all out 
#                       with an extra thread, reads back async, and reassembles.
#                       This is much more efficient
#
import os,subprocess,re

__VERSION__ = '0.2'

class Hunspell():
    """A pure python module to interface with hunspell.
       It was written as a replacement for the hunspell module from
       http://code.google.com/p/pyhunspell/, which appears to be in unmaintained.
       and more difficult to use, due to lack of examples and documentation.
    """
    def __init__(self, dicts=['en_US']):
        self.cmd = ['hunspell', '-i', 'utf-8', '-a']
        self.dicts = dicts
        self.proc = None
        self.attr = None
        self.buffer = ''

    def _start(self):
        cmd = self.cmd
        if self.dicts is not None and len(self.dicts): 
            cmd += ['-d', ','.join(self.dicts)]
        try:
            self.proc = subprocess.Popen(cmd, shell=False, 
                stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except OSError as e:
            self.proc = "%s failed: errno=%d %s" % (cmd, e.errno, e.strerror)
            raise OSError(self.proc)
        header = ''
        while True:
            more = self.proc.stdout.readline().rstrip()
            if len(more) > 5 and more[0:5] == '@(#) ':    # version line with -a
                self.version = more[5:]
                break
            elif len(more) > 9 and more[0:9] == 'Hunspell ': # version line w/o -a
                self.version = more
                break
            else:
                header += more  # stderr should be collected here. It does not work
        if len(header): self.header = header
        self.buffer = ''
        
    def _readline(self):
        # python readline() is horribly stupid on this pipe. It reads single
        # byte, just like java did in the 1980ies. Sorry, this is not
        # acceptable in 2013.
        if self.proc is None:
            raise Error("Hunspell_readline before _start")
        while True:
            idx = self.buffer.find('\n')
            if idx < 0:
                more = self.proc.stdout.read()
                if not len(more):
                    r = self.buffer
                    self.buffer = ''
                    return r
                self.buffer += more
            else:
                break
        r = self.buffer[0:idx+1]
        self.buffer = self.buffer[idx+1:]
        return r

    def _load_attr(self):
        try:
            p = subprocess.Popen(self.cmd + ['-D'], shell=False, 
                stdin=open('/dev/null'), stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        except OSError as e:
            raise OSError("%s failed: errno=%d %s" % (self.cmd + ['-D'], e.errno, e.strerror))
        self.attr = {}
        header=''
        while True:
            line = p.stdout.readline().rstrip()
            if not len(line):
                break
            # AVAILABLE DICTIONARIES (path is not mandatory for -d option):
            m = re.match('([A-Z]+\s[A-Z]+).*:$', line)
            if m:
                header = m.group(1)
                self.attr[header] = []
            elif len(header):
                self.attr[header].append(line)
        return self.attr
 
    def dicts(self,dicts=None):
        """returns or sets the dictionaries that hunspell shall try to use"""
        if dicts is not None:
            self.dicts = dicts
        return self.dicts

    def list_dicts(self):
        """query hunspell about the available dictionaries.
           Returns a key value dict where keys are short names, and values 
           are path names. You can pick some or all of the returned keys,
           and use the list (or one) as an argument to 
           the next Hunspell() instance, or as an argument 
           to the dicts() method.
        """
        if self.attr is None: self._load_attr()
        r = {}
        for d in self.attr['AVAILABLE DICTIONARIES']:
            words = d.split('/')
            r[words[-1]] = d
        return r
 
    def dict_search_path(self):
        """returns a list of pathnames, actually used by hunspell to load 
           spelling dictionaries from.
        """
        if self.attr is None: self._load_attr()
        r = []
        for d in self.attr['SEARCH PATH']:
            r += d.split(':')
        return r
 
    def dicts_loaded(self):
        """query the spelling dictionaries that will actually be used for 
           the next check_words() call.
        """
        if self.attr is None: self._load_attr()
        return self.attr['LOADED DICTIONARY']
 
    def check_words(self, words):
        """takes a list of words as parameter, and checks them against the 
           loaded spelling dictionaries. A key value dict is returned, where
           every key represents a word that was not found in the 
           spelling dictionaries. Values are lists of correction suggestions.
           check_words() is implemented by calling the hunspell binary in pipe mode.
           This is fairly robust, but not optimized for efficiency.
        """
        if self.proc is None:
            self._start()
        childpid = os.fork()
        if childpid == 0:
            for w in words:
                self.proc.stdin.write(("^"+w+"\n").encode('utf8'))
            os._exit(0)
        self.proc.stdin.close()
        bad_words = {}
 
        while True:
            line = self._readline()
            if len(line) == 0:
                break
            line = line.rstrip()
            if not len(line) or line[0] in '*+-': continue
 
            if line[0] == '#': 
                car = line.split(' ')
                bad_words[car[1]] = []          # no suggestions
            elif line[0] != '&': 
                print "hunspell protocoll error: '%s'" % line
                continue        # unknown stuff
            # '& Radae 7 0: Radar, Ramada, Estrada, Prada, Rad, Roadie, Readable\n'
            a = line.split(': ')
            car = a[0].split(' ')
            cdr = a[1].split(', ')
            bad_words[car[1]] = cdr
        self.proc = None
        return bad_words

 
if __name__ == "__main__": 
    from pprint import pprint
    h = Hunspell()
    pprint(h.list_dicts())
    pprint(h.dict_search_path())
    pprint(h.check_words(["ppppp", '123', '', 'gorkicht', 'gemank', 'haus', '']))
    pprint(h.check_words(["Radae", 'blood', 'mensch', 'green', 'blea', 'fork']))
    pprint(h.version)
