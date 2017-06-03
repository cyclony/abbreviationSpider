from bs4 import BeautifulSoup
import csv
import requests
import functools
from concurrent import futures
from itertools import islice

Price_Item = functools.namedtuple('Price_Item','product_name date product_type buy_price sell_price')
product_url_prex = 'http://life.cntaiping.com/pricehistory.jspx?a=1&productid={}&pageno={}'



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
    return [(tag['value'], tag.text) for tag in soup.select('select option')]  # return 产品id 和产品名称


class Price_Crawler:
    page_no = 1
    prd_id = 0
    prod_name = ''
    prod_url = ''
    downloaded_data = []

    def __init__(self, prod_id, prod_name):
        self.prod_name = prod_name
        self.prd_id = prod_id
        self.prod_url = product_url_prex.format(self.prd_id, self.page_no)

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
            for price_item_tag in islice(soup.select('tr'), 1, 21): #  利用切片函数（islice，将第一条和最后一条过滤掉)
                date, prd_type, buy_price, sell_price, _ = (tag.text.strip() for tag in price_item_tag.find_all('td'))#  利用unpack将list对应元素赋值
                yield date, prd_type, buy_price, sell_price
            yield from self.get_prd_his_price_data(self.next_page_url(product_url))

    def download_prices(self):
        for date, prd_type, buy_price, sell_price in self.get_prd_his_price_data(self.prod_url):
            item = Price_Item(self.prod_name, date, prd_type, buy_price, sell_price)
            print(item)
            self.downloaded_data.append(item)
        self.save_to_file()


    def save_to_file(self):
        file_name = self.prod_name+'.csv'
        with open(file_name, 'a', encoding='utf-8-sig', newline='') as file:
            c = csv.writer(file)
            c.writerows(self.downloaded_data)


def crawl_price_data(tuple):
    crawler = Price_Crawler(*tuple)
    crawler.download_prices()


prod_id_list = get_pid_list(productid_list_url)
with futures.ThreadPoolExecutor(5) as executor:
    res = executor.map(crawl_price_data, prod_id_list)
    print(len(list(res)))
