#-*- coding:utf-8 -*-
import requests
import csv
import functools
from bs4 import BeautifulSoup

import time
import collections


# 装饰器，控制出错后重试
def retry(max_retry_times, sleep_secs):
    def retry_decorator(func):
        def func_wrapper(url):
            retry_times = 0
            while retry_times < max_retry_times:
                try:
                    return func(url)  # 被装饰的函数
                    break
                except Exception as e:
                    retry_times = retry_times + 1
                    print("encounter error: ", e)
                    time.sleep(sleep_secs)  # 停一段时间再发送数据
                    if retry_times == max_retry_times:
                        raise e  # 达到最大重复尝试次数，放弃尝试，将异常抛出，由顶层逻辑处理（将已经抓取的数据保存下来）

        return func_wrapper
    return retry_decorator

Acronyms = collections.namedtuple("Acronyms",['acronyms_name','chinese_desc','english_desc'])

"""
bar = Bar("-----------crawl data:  " + source_file_name, max=count)
with open(source_file_name, 'r', encoding='UTF-8') as file:
    for line in file:
        acronyms_name = line.strip()
        acronyms = Acronyms_cls(acronyms_name, save_file_name)
        page_url = "http://shortof.com/search/luceneapi_node/"+ urllib.parse.quote(acronyms_name)+"?f[0]=sm_field_enshort%3A"+ urllib.parse.quote(acronyms_name)
        acronyms.crawl_data(page_url)
        bar.next()
bar.finish()
"""
#--------------------------new version------------------------------------------------------#


domain = "http://shortof.com/"
source_file_name = 'acronyms1.txt'
save_file_name = "save_" + source_file_name


@functools.lru_cache()  # 缓存网页访问结果，节约网络开销
@retry(3, 1)  # decorator装饰器模式
def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text)


def next_page_url(url):
        soup = get_soup(url)
        page_tag = soup.select_one('li.pager-next')
        return domain + page_tag.a['href'] if page_tag else None


def iter_pages_url(page_url):
    if page_url:
        yield page_url
        yield from iter_pages_url(next_page_url(page_url))


def item_urls_on_page(page_url):
    current_page_soup = get_soup(page_url)
    for tag in current_page_soup.select('dt.title'):
        detail_url = domain + tag.a['href']
        yield detail_url


def item_detail_page(item_detail_url):
    soup = get_soup(item_detail_url)
    tag_list = soup.select('div.field-item')
    if tag_list:
        yield Acronyms(tag_list[0].string.strip(), tag_list[1].string.strip(), tag_list[2].string.strip())


#--------------------core process--------------------------------------------#
def iter_acronyms_items(init_url):
        for each_page_url in iter_pages_url(init_url):  # 迭代每一页数据的url
            for item_url in item_urls_on_page(each_page_url):  # 根据page url，迭代当前页item列表中每一个item的url
                yield from item_detail_page(item_url)  # 根据每一个item，获得详情页的数据 Acronyms


#----------------------main process----------------------------#
with open(source_file_name, 'r', encoding='UTF-8') as source_file, open(save_file_name, 'a', encoding='UTF-8') as save_file:
    csv_save_file = csv.writer(save_file)
    for acronyms_name in source_file:
        page_url = "http://shortof.com/search/luceneapi_node/{name}?f[0]=sm_field_enshort%3A{name}".format(name=requests.utils.quote(acronyms_name))
        #page_url = "http://shortof.com/search/luceneapi_node/"+ requests.utils.quote(acronyms_name)+"?f[0]=sm_field_enshort%3A"+ requests.utils.quote(acronyms_name)
        for acronyms in iter_acronyms_items(page_url):
            print(acronyms)
            csv_save_file.writerow(acronyms)
            save_file.flush()




