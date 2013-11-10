#!/usr/bin/python

from bs4 import BeautifulSoup
import codecs
import htmlentitydefs
import lxml
import os
import re
import time
import urllib2

OUTPUT_FILE = 'corpus.txt'

def request_url(url):
  req = urllib2.Request(url, None, {'User-agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'})
  try:
    handle = urllib2.urlopen(req)
    return handle.read()
  except urllib2.HTTPError, e:
    return e.read()

def strip_comments(data):
  """removes text in brackets and parenthesis"""
  p = re.compile(r'(\[[^\]]*\]|\([^\)]*\))')
  return p.sub('', data)

def unescape(text):
    """
        Converts HTML character codes to Unicode code points.
        
        @param text the HTML (or XML) source text in any encoding.
        @return The plain text, as a Unicode string, if necessary.
        """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text
    return re.sub("&#?\w+;", fixup, text)

if __name__ == "__main__":
  if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)
  output = codecs.open(OUTPUT_FILE, 'a', 'utf-8')

  with open('urls.txt', 'r') as f: 
    lines = f.readlines()

  for line in lines:
    url = line.split(',')[1]
    html = request_url(url)
    soup = BeautifulSoup(html, "lxml")
    content = ''
    if not soup.find('pre'):
      continue
    content = soup.find('pre').encode_contents()
    content = strip_comments(content)
    content = unescape(unicode(content, 'utf-8'))
    output.write(content)
    # Don't piss off a sysadmin
    time.sleep(.01)

  output.close()
