from bs4 import BeautifulSoup
import csv
import requests
import functools
from concurrent import futures
from itertools import islice
import re
from spider.PageSpider import PageSpider
from spider.PageSpider import get_soup


# 定义命名元组
Price_Item = functools.namedtuple('Price_Item', 'date product_type buy_price sell_price')
product_url_fmt = 'http://life.cntaiping.com/pricehistory.jspx?a=1&productid={}&pageno={}'


# 获取所有的产品id
productid_list_url = 'http://life.cntaiping.com/pricenotice.jspx'


#  需要被替换
def get_price_page_url(soup):
    rex = re.compile('\d+')
    if '下一页' in [tag.string for tag in soup.select('ul.page_gong li')]:
        raw_str = soup.select('ul.page_gong li')[2].a['onclick']  # 下一页数据的格式是：<a onclick="noticePage(2, 0, 351+1);">下一页</a>
        next_page_no = int(rex.findall(raw_str)[2]) + 1  # 模式匹配的结果例子是：['2', '0', '351', '1']
        next_page_url = product_url_fmt.format(1, next_page_no)  # to be finished!!!
        return next_page_url


# 自己定义的方法
def page_price_item_gen(soup):
    for price_item_tag in soup.select('tr')[1:-1]:  # 利用切片函数islice，将第一条和最后一条过滤掉)
        date, prd_type, buy_price, sell_price, _ = (tag.text.strip() for tag in
                                                    price_item_tag.find_all('td'))  # 利用unpack将list对应元素赋值
        yield Price_Item(date, prd_type, buy_price, sell_price)



spider = PageSpider(product_url_fmt.format(1,1))

PageSpider.one_page_data_gen = page_price_item_gen
PageSpider.get_next_page_url = get_price_page_url


for t in islice(spider.n_page_data_gen(spider.init_page_url), 50):
    print(t)

def pid_gen(url):
    soup = get_soup(url)
    return (tag['value'] for tag in soup.select('select option'))

prod_id_list = pid_gen(productid_list_url)  # 得到产品id列表
with futures.ThreadPoolExecutor(5) as executor:
    res = executor.map(crawl_price_data, prod_id_list)
    print(len(list(res)))

