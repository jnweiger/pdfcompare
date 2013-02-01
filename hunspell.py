import subprocess
import os
from pprint import pprint

class Hunspell():
    def __init__(self):
        self.cmd = ['hunspell', '-i', 'utf-8']
        try:
          self.proc = subprocess.Popen(self.cmd, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        except OSError as e:
          self.proc = "%s failed: errno=%d %s" % (self.cmd, e.errno, e.strerror)
          raise OSError(self.proc)
        self.version = self.proc.stdout.readline().rstrip()
        
    def check(self, word):
        self.proc.stdin.write(word + "\n")
        while True:
            output = self.proc.stdout.readline().rstrip()
            if len(output): break
        if output == '*': return None
        if output[0] != '&': return output
        a = output.split(': ')
        return a[1].split(', ')

 
h = Hunspell()
pprint(h.check("Radae"))
pprint(h.check("Radar"))
pprint(h.check("Haus"))
pprint(h)
