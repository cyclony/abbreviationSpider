from bs4 import BeautifulSoup
import csv
import requests
import functools
from concurrent import futures
from itertools import islice
import re


# 定义命名元组
Price_Item = functools.namedtuple('Price_Item', 'date product_type buy_price sell_price')
product_url_fmt = 'http://life.cntaiping.com/pricehistory.jspx?a=1&productid={}&pageno={}'


@functools.lru_cache()
def get_soup(url):
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text)
    return soup


# 获取所有的产品id
productid_list_url = 'http://life.cntaiping.com/pricenotice.jspx'


def get_pid_list(url):
    soup = get_soup(url)
    return [(tag['value'], tag.text) for tag in soup.select('select option')]  # return 产品id 和产品名称


def iter_page_url(soup):
    rex = re.compile('\d+')
    if '下一页' in [tag.string for tag in soup.select('ul.page_gong li')]:
        raw_str = soup.select('ul.page_gong li')[2].a['onclick']  # 下一页数据的格式是：<a onclick="noticePage(2, 0, 351+1);">下一页</a>
        next_page_no = int(rex.findall(raw_str)[2]) + 1  # 模式匹配的结果例子是：['2', '0', '351', '1']
        next_page_url = product_url_fmt.format(1, next_page_no)  # to be finished!!!
        yield next_page_url
        yield from iter_page_url(get_soup(next_page_url))


    # 可以被替换
def one_page_data_gen(soup):
    for price_item_tag in soup.select('tr')[1:-1]:  # 利用切片函数islice，将第一条和最后一条过滤掉)
        date, prd_type, buy_price, sell_price, _ = (tag.text.strip() for tag in
                                                    price_item_tag.find_all('td'))  # 利用unpack将list对应元素赋值
        yield Price_Item(date, prd_type, buy_price, sell_price)

class PriceSpider:
    page_no = 1
    prd_id = 0
    prod_name = ''
    prod_url = ''
    downloaded_data = []

    def __init__(self, prod_id, prod_name):
        self.prod_name = prod_name
        self.prd_id = prod_id
        self.prod_url = product_url_fmt.format(self.prd_id, self.page_no)

    def page_soup_gen(self, init_url):
        soup = get_soup(init_url)
        for url in iter_page_url(soup):
            yield get_soup(url)

    # 获取指定产品id对应的历史数据
    def n_page_data_gen(self, init_page_url):
        if init_page_url:
            for soup in self.page_soup_gen(init_page_url):
                yield from one_page_data_gen(soup)



    # 抓取该产品的所有历史价格数据
    def download_data(self):
        for price_item in self.n_page_data_gen(self.prod_url):
            self.downloaded_data.append(price_item)
        self.save_to_file()

    def save_to_file(self):
        file_name = self.prod_name+'.csv'
        with open(file_name, 'a', encoding='utf-8-sig', newline='') as file:
            c = csv.writer(file)
            c.writerows(self.downloaded_data)


def crawl_price_data(tuple):
    crawler = PriceSpider(*tuple)
    crawler.download_data()


spider = PriceSpider(1, '太平财富投连(A款)')


def my_page_data_gen(soup):
    for tag in soup.select('tr')[1:-1]:
        yield [price_tag.string.strip() for price_tag in tag.select('td')[2:4]]

one_page_data_gen = my_page_data_gen


for t in islice(spider.n_page_data_gen(spider.prod_url), 50):
    print(t)

"""
prod_id_list = get_pid_list(productid_list_url)  # 得到产品id列表
with futures.ThreadPoolExecutor(5) as executor:
    res = executor.map(crawl_price_data, prod_id_list)
    print(len(list(res)))
"""

