from bs4 import BeautifulSoup
import functools
import requests
import csv


@functools.lru_cache()
def get_soup(url):
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text)
    return soup


class PageSpider:
    init_page_url = ''
    prod_name = ''
    downloaded_data = []

    def next_page_url_gen(self, soup):
        next_page_url = PageSpider.get_next_page_url(soup)
        if next_page_url:
            yield next_page_url
            yield from self.next_page_url_gen(get_soup(next_page_url))

    @staticmethod
    def get_next_page_url(soup):
        return None

    @staticmethod
    # 需要被替换
    def one_page_data_gen(soup):
        yield None

    def __init__(self, init_page_url):
        self.init_page_url = init_page_url

    def page_soup_gen(self, init_url):
        soup = get_soup(init_url)
        for url in self.next_page_url_gen(soup):
            yield get_soup(url)

    # 获取指定产品id对应的历史数据
    def n_page_data_gen(self, init_page_url):
        if init_page_url:
            for soup in self.page_soup_gen(init_page_url):
                yield from PageSpider.one_page_data_gen(soup)

    # 抓取该产品的所有历史价格数据
    def download_data(self):
        for price_item in self.n_page_data_gen(self.init_page_url):
            self.downloaded_data.append(price_item)
        self.save_to_file()

    def save_to_file(self):
        file_name = self.prod_name + '.csv'
        with open(file_name, 'a', encoding='utf-8-sig', newline='') as file:
            c = csv.writer(file)
            c.writerows(self.downloaded_data)
