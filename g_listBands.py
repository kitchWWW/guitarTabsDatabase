#traverses the 'bands starting with <letter>' pages
#lists all bands in the 'bandsToDo'


from bs4 import BeautifulSoup
import urllib2,cookielib,sys

sites = []

letter = sys.argv[1]

siteBase = 'https://www.ultimate-guitar.com/bands/'+letter

pageNumber = -1
while True:
    pageNumber +=1
    site = siteBase+str(pageNumber)+'.htm'
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

    print site

    added = False
    while True:
        try:
            i = htmlpage.index('/tabs/'+letter);
            htmlpage = htmlpage[i:]
            i = htmlpage.index('"');
            tab_url = htmlpage[:i]
            htmlpage = htmlpage[i:]
            print tab_url
            fd = open('g_files/bandsToDo.txt','a')
            fd.write(tab_url+'\n')
            fd.close
            added = True
        except:
            break
    if not added:
        break



