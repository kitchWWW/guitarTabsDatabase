#for each band and all their listings, puts the url of the pages with tabs into songsToDo

from bs4 import BeautifulSoup
import urllib2,cookielib

sites='https://www.ultimate-guitar.com'

fd = open('g_files/bandsToDo.txt','r')
lines = fd.readlines()
for l in lines:
    site = sites+l.strip('\n')
    hdr = {
    	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'
    }
    print 'site:',site
    req = urllib2.Request(site, headers=hdr)

    try:
        page = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print e.fp.read()
    
    soup = BeautifulSoup(page.read(),"html.parser")
    for link in soup.find_all('a'):
        l = link.get('href')
        #print l
        if l.startswith('https://tabs.ultimate-guitar.com/') and l.endswith('crd.htm'):
            print l
            h = open('g_files/songsToDo.txt','a')
            h.write(l+'\n')
            h.close()
        #print BeautifulSoup(tr,"html.parser").find('a')

