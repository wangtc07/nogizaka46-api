import re

from flask import current_app

from utils.utils import domain_pattern


# url: /s/n46/diary/MEMBER/list?&page=0&ct=36753&cd=MEMBER
def add_domain(url):
    # check https
    if domain_pattern.match(url):
        path = re.sub("https://www.nogizaka46.com/", '', url)
    else:
        path = re.sub(r"^/", '', url)
    domain = current_app.config.get('DOMAIN')
    return domain + path


# 連接路徑
def join(base_path, name):
    first_reg = re.compile("^\\/")
    last_reg = re.compile("\\/$")

    if last_reg.search(base_path):
        if first_reg.search(name):
            return base_path + re.sub("^\\/", '', name)
        return base_path + name

    if first_reg.search(name):
        return base_path + name

    return base_path + '/' + name


def remove_dot(date):
    return re.sub("\\.", '-', date)
