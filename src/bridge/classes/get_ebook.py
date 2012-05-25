#!/usr/bin/env python
import urllib2
from BeautifulSoup import BeautifulSoup as Soup

sitename='http://www.ebookshare.net/'

for x in range(1,20):
   url = sitename + 'all-' + str(x) + '.html' # write the url here
   print '#' *30
   print '#   ' + url
   print '#' *30
   print 
   usock = urllib2.urlopen(url)
   html = usock.read()
   usock.close()
   soup = Soup(html)
   for image in soup.findAll('img'):
     if 'jpg' in image['src']:
       bookname = image['alt']
       print '#' + bookname
       url2 = sitename + image.parent['href']
       print '#' + url2
       usock = urllib2.urlopen(url2)
       html2 = usock.read()
       usock.close()
       soup2 = Soup(html2)
       for link in soup2.findAll('a'):
         if 'download.php' in link['href']:
           torrent_url= sitename +  link['href']
           torrent_name= bookname.replace(' ','-') + '.torrent'
           print 'curl ' +  torrent_url + ' -o ' + torrent_name
           print
