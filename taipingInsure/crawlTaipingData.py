from bs4 import BeautifulSoup
import csv
import requests
import functools


Price_Item = functools.namedtuple('Price_Item','product_name date product_type buy_price sell_price')

def get_data(url):
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text)
    return [[item.text.strip() for item in tag('td')] for tag in soup.select('tr')]

@functools.lru_cache()
def get_soup(url):
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text)
    return soup

#获取所有的产品id
productid_list_url = 'http://life.cntaiping.com/pricenotice.jspx'
def get_pid_list(url):
    soup = get_soup(url)
    return [(tag['value'], tag.text) for tag in soup.select('select option')]



product_url_prex = 'http://life.cntaiping.com/pricehistory.jspx?a=1&productid={}&pageno={}'

class Price_Crawler:
    page_no = 1
    prd_id = 0
    def __init__(self):
        return

    def next_page_url(self, url):
        soup = get_soup(url)
        if '下一页' in (tag.string for tag in soup.select('li')):
            self.page_no += 1
            return product_url_prex.format(self.prd_id, self.page_no)
        else: return None

    #获取指定产品id对应的历史数据
    def get_prd_his_price_data(self, product_url):
        if product_url:
            soup = get_soup(product_url)
            for price_item_tag in soup.select('tr'):
                if price_item_tag.text == '':
                    continue
                date, prd_type, buy_price, sell_price, _ = (tag.text.strip() for tag in price_item_tag.find_all('td'))
                yield date, prd_type, buy_price, sell_price
            yield from self.get_prd_his_price_data(self.next_page_url(product_url))


    def crawl_price_data(self):
        for prd_id, prd_name in get_pid_list(productid_list_url):
            self.prd_id = prd_id
            self.page_no = 1
            product_url = product_url_prex.format(self.prd_id, self.page_no)
            for date, prd_type, buy_price, sell_price in self.get_prd_his_price_data(product_url):
                yield Price_Item(prd_name, date, prd_type, buy_price, sell_price)


#save to file
with open('data2.csv', 'a', encoding='utf-8-sig', newline='') as file:
    c = csv.writer(file)
    spider = Price_Crawler()
    for price_item in spider.crawl_price_data():
        print(price_item)
        c.writerow(price_item)
        file.flush()
