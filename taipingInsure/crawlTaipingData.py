from bs4 import BeautifulSoup
import csv
import requests




def get_data(url):
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text)
    return [[item.text.strip() for item in tag('td')] for tag in soup.select('tr')]

def get_soup(url):
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text)
    return soup

#获取所有的产品id
productid_url = 'http://life.cntaiping.com/pricenotice.jspx'
def get_pid_list(url):
    soup = get_soup(url)
    return [tag['value'] for tag in soup.select('select option')]


#save to file
with open('data2.csv','a',encoding='utf-8-sig', newline='') as file:
    c = csv.writer(file)
    c.writerows(data_list)
