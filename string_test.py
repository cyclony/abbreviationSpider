from urllib.parse import urlencode
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

xmlText = urllib.request.urlopen("http://shortof.com/search/luceneapi_node/slam?f[0]=sm_field_enshort%3ASLAM").read();
soup = BeautifulSoup(xmlText)
l = [("cyc","jane")]
l += [(tag.string, tag['href']) for tag in soup.select('dt.title > a')]

for name,url in l:
    print("acronyms name is: "+name)
    print("url is : "+ url)

