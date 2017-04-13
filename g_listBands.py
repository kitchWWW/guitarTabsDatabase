from bs4 import BeautifulSoup
import urllib2,cookielib

sites = []
sites.append('https://www.ultimate-guitar.com/bands/a')

fd = open('g_files/bandsToDo.txt','w')
fd.seek(0)
fd.truncate()
fd.close()


for pageNumber in range(10,91):
    site = sites[0]+str(pageNumber)+'.htm'
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

    htmlpage = page.read()
    #print htmlpage
    while True:
        try:
            i = htmlpage.index('/tabs/a');
            htmlpage = htmlpage[i:]
            i = htmlpage.index('"');
            tab_url = htmlpage[:i]
            htmlpage = htmlpage[i:]
            print tab_url
            fd = open('g_files/bandsToDo.txt','a')
            fd.write(tab_url+'\n')
            fd.close
        except:
            break



