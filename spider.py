import urllib.request
import sys
import time
from bs4 import BeautifulSoup
from progress.bar import Bar

#这是一个decorator方法定义，为业务逻辑加上重试的逻辑，避免不同维度的代码逻辑相互干扰
def retry(max_retry_times, sleep_secs):
    def retry_decorator(func):
        def func_wrapper(self):
            retry_times = 0;
            while retry_times < max_retry_times:
                try:
                    func(self);#业务执行的核心逻辑
                    break;
                except Exception as e:
                    retry_times =+ 1;
                    print("encount error: ", e)
                    time.sleep(sleep_secs)#停一段时间再发送数据
                    if retry_times == max_retry_times:
                        raise e;#达到最大重复尝试次数，放弃尝试，将异常抛出，由顶层逻辑处理（将已经抓取的数据保存下来）

        return func_wrapper
    return retry_decorator

def progress_decorator(func):
    def func_wrapper(self):
        bar = Bar("extracting " + self.sub_category_name, max=int(self.max_page_no))
        for i in range(int(self.max_page_no)):#遍历每一页
            func(self)
            bar.next();
        bar.finish();
    return func_wrapper

class SubCategoryItem:
    subCategoryName = ""
    subCategoryURL = ""

    def __init__(self, subCategoryName, subCategoryURL):
        self.subCategoryName = subCategoryName
        self.subCategoryURL = subCategoryURL


class Acronyms:
    sub_category_name = ""
    acronyms_name = ""
    acronyms_desc = ""

    def __init__(self, sub_category_name, acronyms_name, acronyms_desc):
        self.sub_category_name = sub_category_name
        self.acronyms_name = acronyms_name
        self.acronyms_desc = acronyms_desc

class Sub_Category:
    category_name = ""
    max_page_no = ""
    sub_category_name = "";
    sub_category_url = "";

    def __init__(self, category_name, sub_category_name, sub_category_url):
        self.category_name = category_name
        self.sub_category_name = sub_category_name
        self.sub_category_url = sub_category_url

    #得到分页的页数
    def get_max_page_number(self):
        print("get "+ self.sub_category_url +" page number")
        itemsPage = urllib.request.urlopen(self.sub_category_url)
        itemsHtml = itemsPage.read()
        soup = BeautifulSoup(itemsHtml)
        #找到页面底部的翻页区域
        pageSection = soup.find('div',{'class':'pager'})
        pageNumberList = pageSection.find_all('a');
        #倒数第二个a标签的数字表示最大的页数
        maxPageNumber = pageNumberList[len(pageNumberList)-2].string;
        return maxPageNumber

    @progress_decorator #使用progress进度条decorator
    def crawl_acronyms_data(self):
        acronymsItemList = [];
        #获得当前子分类的分页数
        self.max_page_no = self.get_max_page_number()
        #循环遍历每一个分页，获取指定分页的详细数据列表
        #这里使用了进度条process bar插件，帮助用户了解抓取进度
        bar = Bar("extracting " + self.sub_category_name, max=int(self.max_page_no))
        for i in range(int(self.max_page_no)):#遍历每一页
            #获得每一页的数据
            current_page = Page(self.sub_category_name, self.sub_category_url);
            current_page.crawl_data();
            #将当前页数据保存到
            current_page.save_to_file(self.category_name)
            bar.next();
        bar.finish();



class Page:
    sub_category_name = ""
    url = ""
    acronyms_list = []

    def __init__(self, sub_category_name, url):
        self.url = url
        self.sub_category_name = sub_category_name

    @retry(5, 1)#decorator 装饰器，尝试重复次数和重试前暂停时间（秒）作为输入参数
    def crawl_data(self):
        html_text = urllib.request.urlopen(url).read();
        soup = BeautifulSoup(html_text);
        for item_tag in soup.find_all('tr'):
            acronyms_name = item_tag.td.string;
            acronyms_desc = item_tag.td.next_sibling.string;
            self.acronyms_list.append(Acronyms(self.sub_category_name, acronyms_name, acronyms_desc))

    def save_to_file(self, category_name):
        file_name = "./"+category_name+".cvs"
        with open(file_name,'a',encoding='utf-8') as file:
            for acronyms in self.acronyms_list:
                str = ""
                if(acronyms.sub_category_name is None):
                    acronyms.sub_category_name = ""
                if(acronyms.acronyms_name is None):
                    acronyms.acronyms_name = ""
                if(acronyms.acronyms_desc is None):
                    acronyms.acronyms_desc = ""
                str = acronyms.sub_category_name + "," + acronyms.acronyms_name + "," + acronyms.acronyms_desc + "\n"
                file.write(str)
                file.flush()

#抓取子分类的分类名称列表
def getSubCategoryList():
    subCategoryList = []
    tables = soup.find_all('div', {'class': "tdata-ext col-sm-12"})
    subCategorySoupList = tables[0].find_all("tr")
    for i in subCategorySoupList:
        subCategoryItem = SubCategoryItem(i.td.a.string, domain + i.td.a['href']);
        subCategoryList.append(subCategoryItem);
    #应该返回一个结构数据列表，包括名称和url对
    return subCategoryList


#全局变量
url = "http://www.abbreviations.com/category/"
domain = "http://www.abbreviations.com"
soup = None
startFromHere = True
param1 = ""#启动参数，指定具体的分类名称
param2 = ""#启动参数，指定子分类的名称（用于断点重启）
#main process start here

#启动输入参数应该是子分类的名字，人工控制程序从该子分类开始重新抓取数据（类似于人工断点重启）

#-------------通过启动参数判断是否要从特定的子分类开始------------------------------------
paramLength = len(sys.argv)
param1 = sys.argv[1]
if paramLength>2:
    param2 = sys.argv[2]
    startFromHere = False
try:#一旦网络异常，则放弃当前的分类处理并退出
    page = urllib.request.urlopen(url + param1)
    html = page.read();
    soup = BeautifulSoup(html)
except:
    print("url can't be opened: " + url + param1)
    exit();
print("------------"+ param1 +"----------------------")

#得到子分类的详细数据（子分类名字 + 详细页URL）
subCategoryList = getSubCategoryList()
for i in subCategoryList:
    #如果输入参数是某一个子分类的名字，说明需要从该子分类开始重新抓取数据；否则跳过
    if param2 == i.subCategoryName:
        startFromHere = True
    if startFromHere == True:
        sub_category = Sub_Category(param1,i.subCategoryName, i.subCategoryURL)
        sub_category.crawl_acronyms_data()








