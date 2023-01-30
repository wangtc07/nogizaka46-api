import os
import zipfile
from io import BytesIO

import requests
from bs4 import BeautifulSoup

from utils import utils, bs4_utils, file_utils
from utils.file_utils import modify_file_time


def download_img(path: str, soup: BeautifulSoup, cur_url=''):
    if cur_url:
        # get soup
        soup = bs4_utils.get_soup(cur_url)

    # get img link
    img_htmls = soup.select('img')
    src_list = map(bs4_utils.get_src, img_htmls)
    src_list = list(filter(bs4_utils.filter_jpg, src_list))
    print('src list: ', src_list)

    # get dcimg
    a_link = soup.select('a')
    href_list = map(bs4_utils.get_href, a_link)
    # filter error link
    dcimg_list: list = list(filter(bs4_utils.filter_err_dcimg, href_list))

    # get member name
    names = bs4_utils.get_class_list('bd--prof__name f--head', soup)
    name = names[0].get_text()

    # get date 2022.11.05 20:58
    dates = bs4_utils.get_class_list('bd--hd__date a--tx js-tdi', soup)
    date = dates[0].get_text()

    # get date
    download_blog_imgs(src_list, dcimg_list, path, name, date)
    pass


def download_blog_imgs(src_list: list, dcimg_list: list, path: str, name: str, date: str):
    utils.make_dirs(path)
    formate = utils.get_file_name(date, name)

    # api 不用查詢是否已經有檔案
    # check exists file
    # files = [f for f in os.listdir(path) if re.match(formate, f)]

    i = 1

    for src in src_list:
        # add domain
        url = utils.add_domain(src)

        file_path = file_utils.get_path(formate, i, path)

        # download
        response = requests.get(url=url)
        # response.status_code = 404

        # 下載到本地
        open(file_path, 'wb').write(response.content)

        photo: bytes = response.content

        # modify file date
        modify_file_time(file_path, date)

        i = i + 1

    for dcimg in dcimg_list:
        file_path = file_utils.get_path(formate, i, path)
        print('download dcimg: ', dcimg)

        try:
            utils.download_dcimg(file_path, dcimg)

            # modify file date
            modify_file_time(file_path, date)

            i = i + 1
        except:
            print('過期: ', dcimg)

    return None


# 下載已存在的 blog 圖片
def get_exists_blog_photo(blog_path) -> BytesIO:
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        files = [f for f in os.listdir(blog_path)]
        for file_name in files:
            file_path = blog_path + '/' + file_name
            zf.write(file_path, compress_type=zipfile.ZIP_DEFLATED, arcname=file_name)  # 壓縮種類
        zf.close()
    memory_file.seek(0)  # 改變當前讀寫位置。如果將參數設為 0，則會將讀寫位置移動到流的開頭

    return memory_file
