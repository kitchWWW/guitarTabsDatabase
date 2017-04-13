from bs4 import BeautifulSoup
import urllib2,cookielib

fd = open('g_files/songsToDo.txt','r')

for site in fd.readlines():
    site = site.strip('\n')
    hdr = {
    	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
         'Accept-Encoding': 'none',
         'Accept-Language': 'en-US,en;q=0.8',
         'Connection': 'keep-alive'
    }

    req = urllib2.Request(site, headers=hdr)

    try:
        page = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print e.fp.read()

    soup = BeautifulSoup(page.read(),"html.parser")
    print site
    tables = soup.find_all('table')
    headers = soup.find_all('div')
    pre = soup.find_all('pre')
    try:
        newSoup = pre[1]
        spans = newSoup.find_all('span')
        chords = []
        for chord in spans:
        	chords.append(str(chord).strip('<span>').strip('</span>'))
        print chords
        output = open('g_files/database.txt','a')
        output.write(site+'\t'+str(chords)+'\n')
        output.close()
    except:
        print 'whoops!'
        print site