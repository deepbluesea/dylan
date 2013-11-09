# Scraping library based on NYTimes scraper by David Xia (davidxia.com)
#  - Updated for BeautifulSoup 4
#  - Strip NYT ads and datelines 
#  - Better regex for stripping HTML tags

import os
import urllib2 as ul2
import cookielib
import re
import htmlentitydefs
import codecs
import time
from bs4 import BeautifulSoup

URL_REQUEST_DELAY = 1
BASE = 'http://www.nytimes.com'
TXDATA = None
TXHEADERS = {'User-agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
OUTPUT_FILE = 'nyt_top_stories.txt'

def request_url(url, txdata, txheaders):
    """Gets a webpage's HTML."""
    # Install cookie jar in opener for fetching URL
    cookiejar = cookielib.LWPCookieJar()
    opener = ul2.build_opener(ul2.HTTPCookieProcessor(cookiejar))
    ul2.install_opener(opener)
    req = ul2.Request(url, txdata, txheaders)
    handle = ul2.urlopen(req)
    html = handle.read()
    return html

def remove_html_tags(data):
    """Removes HTML tags"""
    p = re.compile(r'<[^>]*>')
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

def get_urls(soup):
    urls = []
    for story in soup.find_all('div', {'class': 'story'}):
        for hTag in story.find_all({'h2': True, 'h3': True, 'h5': True},
                                  recursive=False):
            if hTag.find('a'):
                urls.append(hTag.find('a')['href'])
# Removes URLs that aren't news articles.
# Create a copy of list b/c you can't modify a list while iterating over it.
    for url in urls[:]:
        if not url.startswith(BASE):
            urls.remove(url)
    return urls

def get_soup(url, data, headers):
    html = request_url(url, data, headers)
    return BeautifulSoup(html)

def scrape_text(url):
    content = ''
    soup = get_soup(url, TXDATA, TXHEADERS)
    # Gets HTML from single page link if article is > 1 page
    if soup.find('li', {'class': 'singlePage'}):
        single = soup.find('li', {'class': 'singlePage'})
        html = request_url(BASE + single.find('a')['href'], TXDATA, TXHEADERS)
        html = unicode(html, 'utf-8')
        soup = BeautifulSoup(html)
    
    if not soup.find('nyt_headline'):
        return content
    headline = soup.find('nyt_headline').encode_contents()
    print headline
    output.write(unicode(headline, 'utf-8'))
   
#    byline = soup.find('nyt_byline').find('h6').encode_contents()
#    byline = remove_html_tags(byline)
#    output.write(unicode(byline + "\n", 'utf-8'))
   
#    dateline = soup.find('h6', {'class': 'dateline'}).encode_contents()
#    output.write(unicode(dateline, 'utf-8'))
    
    for p in soup.find_all('p', {'class': None, 'style': None}):
        # Removes potential ad at the bottom of the page.
        if p.find_parents('div', {'class': 'singleAd'}):
            continue
        # Prevents contents of nested <p> tags from being printed twice.
        if p.find_parents('div', {'class': 'authorIdentification'}):
            continue
        if p.find_parents('div', {'class': 'dh-half'}):
            continue
        content = content + "\n\n" + p.encode_contents().strip()
    content = remove_html_tags(content)
    content = re.sub(" +", " ", content)
    content = unescape(unicode(content, 'utf-8'))
    return content + "\n\n\n\n"

if __name__ == "__main__":
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    output = codecs.open(OUTPUT_FILE, 'a', 'utf-8')

    soup = get_soup('http://international.nytimes.com/', TXDATA, TXHEADERS)
    urls = get_urls(soup)

    for url in urls:
        output.write(scrape_text(url))
        time.sleep(URL_REQUEST_DELAY)

    output.close()
