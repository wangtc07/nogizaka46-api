import re

import requests
from bs4 import BeautifulSoup
from utils import utils


# 取得 soup
def get_soup(cur_url) -> BeautifulSoup:
    # get url response
    cur_url = utils.add_domain(cur_url)
    response = requests.get(cur_url)
    # set encode
    response.encoding = 'UTF-8'
    # get html text
    html = response.text
    # get beautiful soup
    soup = BeautifulSoup(html, 'lxml')
    return soup


def get_src(html):
    try:
        src_ = html['src']
        return src_
    except:
        pass


def get_href(html):
    try:
        href_ = html['href']
        return href_
    except:
        pass


# 過濾非圖片連結(gif)
def filter_jpg(src):
    gif_reg = re.compile(r".*\.gif")
    if src is None:
        return False
    if gif_reg.match(src):
        return False

    return True


# 過濾 dcimg 錯誤頁面
def filter_err_dcimg(url: str):
    reg = re.compile('.*dcimg.*')
    if not reg.match(str(url)):
        return False

    err_reg = re.compile(r".*img1\.php.*")

    try:
        match = err_reg.match(url)
    except:
        print('判斷錯誤', url)
        match = False
    return not match


# 依照 class 名稱取得元素 list
def get_class_list(clazz, soup):
    clazz_finder = '.' + re.sub(r" ", '.', clazz)
    print('class: ', clazz_finder)
    result: list = soup.select(clazz_finder)
    print('list size: ', len(result))
    return result
