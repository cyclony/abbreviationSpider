import requests
import functools
import csv

from bs4 import BeautifulSoup
m_reviews_url = 'https://movie.douban.com/subject/6311303/reviews'
save_file = 'douban_review.csv'
Review = functools.namedtuple('Review', 'title rating author review_content')
@functools.lru_cache()
def get_soup(url):
    return BeautifulSoup(requests.get(url).text, 'lxml')

def iter_pages(url):
    if url:
        yield url
        yield from iter_pages(next_page_url(url))

def next_page_url(url):
    page_soup = get_soup(url)
    next_tag = page_soup.select_one('span.next')
    if next_tag and next_tag.a:
        return m_reviews_url + next_tag.a['href']


def get_review_content(url):
    soup = get_soup(url)
    tag = soup.select_one('div.review-content')
    if tag: return tag.text

with open(save_file, 'w', encoding='u8') as file:
    csv_file = csv.writer(file)
    for page_url in iter_pages(m_reviews_url):
        page_soup = get_soup(page_url)
        for review_item_tag in page_soup.select('div.review-item'):
            review_detail_url = review_item_tag.select_one('header h3 a')['href']
            title = review_item_tag.select_one('header h3 a').text
            author = review_item_tag.select_one('div.header-more a.author span').text
            rating = review_item_tag.select_one('div.header-more span.main-title-rating')['class'][0][-2:]
            #review_content = review_item_tag.select_one('div.main-bd div div.short-content').text.strip()
            review_content = get_review_content(review_detail_url)
            review = Review(title, rating, author, review_content)
            print(review)
            csv_file.writerow(review)
            file.flush()
