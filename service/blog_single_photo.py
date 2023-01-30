import os
import re
from io import BytesIO

from flask import current_app

from utils import down_utils, bs4_utils, path_utils, utils
from utils.path_utils import remove_dot


class blog_photo_zip:
    zip_file: BytesIO
    file_name: str


class blog_class:
    folder_path: str
    zip_name: str


def download(url: str) -> blog_photo_zip:
    # 判斷 url 是否合法
    reg = re.compile(".*s\\/n46\\/diary\\/detail.*")
    if not re.match(reg, url):
        raise RuntimeError

    return download_blog_photo(url)


def download_blog_photo(url) -> blog_photo_zip:
    # get soup
    soup = bs4_utils.get_soup(url)

    # 取得 member date blog folder path
    blog_rs = get_blog_path(soup)
    blog_path = blog_rs.folder_path

    # 檢查檔案是否已存在, base_path/{member}/{date}
    if os.path.isdir(blog_path):
        # 已存在 直接下載
        memory_zip = down_utils.get_exists_blog_photo(blog_path)
    else:
        # 不存在 下載
        down_utils.download_img(path=blog_path, soup=soup)
        memory_zip = down_utils.get_exists_blog_photo(blog_path)

    zip_rs = blog_photo_zip()
    zip_rs.zip_file = memory_zip
    zip_rs.file_name = blog_rs.zip_name + '.zip'

    return zip_rs


# 取得 member date blog folder path
def get_blog_path(soup) -> blog_class:
    # config blog photo path
    base_path = current_app.config.get('BLOG_PHOTO_PATH')
    print(base_path)
    # name, class: bd--prof__name f--head
    name_html = bs4_utils.get_class_list('bd--prof__name f--head', soup)[0]
    name = name_html.get_text()
    member_path: str = path_utils.join(base_path, name)
    # date, ex 2023.01.25 20:06
    date_html = bs4_utils.get_class_list('bd--hd__date a--tx js-tdi', soup)[0]
    date = date_html.get_text()
    # remove .
    date_str = remove_dot(date)
    blog_path = path_utils.join(member_path, date_str)

    rs = blog_class()
    rs.folder_path = blog_path
    rs.zip_name = utils.get_file_name(date, name)

    print('zip name: ' + rs.zip_name)

    return rs
