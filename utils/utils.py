import re
import os
import requests
from bs4 import BeautifulSoup, ResultSet, Tag
import urllib.request
from utils.clazz import all_url
from utils import chorme_utils

ROOT_FOLDER = './asuka'
ROOT_PATH = '.'
EMPTY = ''
DOMAIN = 'https://www.nogizaka46.com/'
download_log = 'downloaded.log'
wait_log = 'html_wait_download.log'
domain_pattern = re.compile(r'https://www\.nogizaka46\.com/.*')

downloaded = open(download_log, encoding='UTF-8')
text_list = downloaded.read().split('\n')


# 取得所在第幾層資料夾
def get_level(url: str):
    return len(url.split('/')) - 3


# 根據 html 在第幾層，往回推
def get_data_path(path: str, level: int):
    if level == 0:
        return '.' + path

    for i in range(level):
        if i == 0:
            path = '..' + path
        else:
            path = '../' + path
    return path


# url: /s/n46/diary/MEMBER/list?&page=0&ct=36753&cd=MEMBER
def add_domain(url):
    # check https
    if domain_pattern.match(url):
        path = re.sub("https://www.nogizaka46.com/", '', url)
    else:
        path = re.sub(r"^/", '', url)
    return DOMAIN + path


# 替換 domain
def replace_domain(path, re_str):
    return re.sub(r"https://www\.nogizaka46\.com", re_str, path)


def add_root_path(url):
    return ROOT_PATH + url


def add_html(url):
    return url + '.html'


# 取得資料夾路徑
def replace_file_path(path: str):
    # 移除檔名 ./files/46/diary/n46/MEMBER/0000_11.jpeg -> ./files/46/diary/n46/MEMBER
    path = replace_reg_text(path)
    arr = path.split('/')
    reg = '/' + arr[len(arr) - 1]
    return re.sub(reg, '', path)


def replace_reg_text(path):
    return re.sub(r'\?', '', path)


# 下載 html
# path: domain + path
def download_html(path: str, data):
    print('download path: ', path)
    re_reg = replace_reg_text(path)
    remove_filename_and_make_dirs(re_reg)
    open(re_reg, 'w').write(data)


# 下載檔案
# path: ./files/46/assets/css/style2.css
def download_file(path: str, url):
    # 判斷是否已下載過
    # flag = check_downloaded(path)
    #
    # if flag:
    #   return
    # 加到陣列
    # add_downloaded(path)

    remove_filename_and_make_dirs(path)
    # 下載檔案
    response = requests.get(url=url)
    open(path, 'wb').write(response.content)


def check_downloaded(path):
    flag = False
    for text in text_list:
        reg = re.compile(text)
        if reg.match(path):
            flag = True
    return flag


def make_dirs(path):
    # 建立路徑
    if not os.path.isdir(path):
        os.makedirs(path)


def remove_filename_and_make_dirs(path):
    folder_path = replace_file_path(path)
    # 建立路徑
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)


def is_dc_page(url):
    reg = re.compile('.*dcimg.*')
    return reg.match(url)


def download_path(src: str):
    # 取得匹配結果，無法匹配返回 None
    match = domain_pattern.match(src)

    if match:
        # 有 domain -> https://www.nogizaka46.com/files/46/diary/n46/MEMBER/0000_11.jpeg
        # 下載到本機路徑
        local_path = ROOT_FOLDER + replace_domain(src, EMPTY)
        print('local_path local', local_path)
        download_file(local_path, src)
    elif is_dc_page(src):
        print('local_path dc', src)
        path = get_dc_path(src)
        download_dcimg(path, src)
    else:
        # 沒有 domain -> /files/46/assets/img/blog/none.png
        local_path = re_ima_set_folder_path(src)
        download_src = DOMAIN + src
        print('local_path', local_path)
        download_file(local_path, download_src)


dcimg_domain = 'http://dcimg.awalker.jp'


# 返回 .png 實際 path
def download_dc_page(url):
    response = requests.get(url=url)
    # 設定編碼格式
    response.encoding = 'UTF-8'
    origin_html = response.text

    soup = BeautifulSoup(origin_html, 'lxml')

    imgs = soup.select('img')
    for img in imgs:
        tag = str(img)
        print(tag)
        reg = re.compile('.*src.*')
        if reg.match(tag):
            path = img['src']
            level = get_level(path)
            n_path = get_data_path(path, level)

            # 下載圖片
            local_path = ROOT_PATH + path + '.png'
            print('dc down', local_path)
            download_src = 'http://dcimg.awalker.jp' + path
            download_dcimg(local_path, download_src)

            img['src'] = n_path + '.png'

    path = get_dc_path(url)
    html_url = add_html(path)
    # 儲存 html
    download_html(html_url, soup.prettify())

    return path + '.png'

    # js = soup.find_all('script', src=True)
    #
    # def download_replace_same(path: str, attr: str, label):
    #   # download_path(path)
    #   attr_path = get_data_path(path, path_level)
    #   label[attr] = attr_path
    #
    # for j in js:
    #   # 取得網址
    #   path = j['src']
    #   download_replace_same(path, 'src', j)


def get_dc_path(url):
    return ROOT_FOLDER + re.sub(r"http://dcimg\.awalker\.jp/v", "/i",
                                url) + '.png'


def is_err_dcimg(url):
    err_reg = re.compile(r".*img1\.php.*")
    match = False
    try:
        match = err_reg.match(url)
    except:
        print('判斷錯誤', url)
        match = False

    return match


# path: ./i/zsLXSUgLvNVFYAoZA0EXjjSYCTVNyBPfGTPDFN7gdMnURadVzPCiNpA5GqCb61xWlqqTbxnOYCc4Pqh0fzmE18tyDa5ECgYk239IBOeSulBHFVSaE2KzMWqASOr0ACcq60WhPWINdjJW5D3CVMfCA8UfgBBTbKjuQAiwPk9X1KU0DGs8fQGQFVWCzoAc9j37BL1WEfhx
# url: http://dcimg.awalker.jp/v/zsLXSUgLvNVFYAoZA0EXjjSYCTVNyBPfGTPDFN7gdMnURadVzPCiNpA5GqCb61xWlqqTbxnOYCc4Pqh0fzmE18tyDa5ECgYk239IBOeSulBHFVSaE2KzMWqASOr0ACcq60WhPWINdjJW5D3CVMfCA8UfgBBTbKjuQAiwPk9X1KU0DGs8fQGQFVWCzoAc9j37BL1WEfhx

def download_dcimg(path, url):
    return
    # http://dcimg.awalker.jp/img1.php?id=nVUBq7MT2ntqBgwlHX6nRbrRMeYVutr4K5nCGIuO4vv9JhSeslEV9A8m4PN1T7bFulHJ7eaZs2GEpjeZp7dTnIfWrl1I8tUn9AHoHIQR0mZAUHj9QTn4Y4Ha7ZvTZOpTKdsdhY3PC3934rIXoaGfYB3GVnfrLNnbH7zfyxMjxoM3MsGIKpWbbYy7XbIvBNXUP0xGBlI6
    # 失效頁面跳過
    if is_err_dcimg(url):
        print('error deimg: ', url)
        return
    browser = chorme_utils.share_browser()
    print('url', url)
    browser.get(url)
    cook = browser.get_cookie('PHPSESSID')
    print(cook)
    cookies = 'ehlkqpc8rd4vs29b166e9t9qd3'
    try:
        cookies = cook['value']
        print('cookies: ', cookies)
    except:
        cookies = 'ehlkqpc8rd4vs29b166e9t9qd3'

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'Host': 'dcimg.awalker.jp',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Cookie': 'PHPSESSID=' + cookies + '; __utmc=138832931; __utmz=138832931.1656227363.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=138832931.217461619.1656227363.1656232261.1656255927.3; __utmt=1; __utmb=138832931.2.10.1656255927'
    }

    dcimg_i = re.sub(r"/v", "/i", url)

    request = urllib.request.Request(url=dcimg_i, headers=headers)
    try:
        response = urllib.request.urlopen(request)

        p = response.read()
        remove_filename_and_make_dirs(path)
        open(
            path,
            'wb').write(p)
    except:
        return


# 寫入以下載檔案
def write_log():
    new_log = '\n'.join(text_list)
    open(download_log, 'w').write(new_log)


def add_downloaded(url):
    url = replace_reg_text(url)
    text_list.append(url)


def write_wait_download_log(html_list: list):
    new_log = '\n'.join(html_list)
    open(wait_log, 'w').write(new_log)


def re_ima_path(url):
    path = replace_domain(url, '')
    # 單篇 blog
    detail_reg = re.compile(r'.*detail/.*')
    list_reg = re.compile(r'.*MEMBER/list.*')
    new_path = path
    if detail_reg.match(path):
        new_path = re.sub(r"(ima=[\w]*&)", "", path)

    if list_reg.match(path):
        new_path = re.sub(r"(ima=[\w]*&)", "", path)

    result = re.sub(r"\?cd=MEMBER", "", new_path)
    return result


# 移除連結 ima 參數
def re_link_path(path: str, level: int):
    # 單篇 blog
    result = re_ima_path(path)

    if level == 0:
        return ROOT_FOLDER + result

    return get_data_path(result, level)


# 移除連結 ima 參數, 取得檔案下載位置
def re_ima_set_folder_path(path: str):
    # 單篇 blog
    result = re_ima_path(path)

    return ROOT_FOLDER + result

    # return get_data_path(result, level)


# 下載 html, 返回未下載連結
def download(url: str):
    # 移除 domain
    re_domain = replace_domain(url, '')
    # 移除 ima -> 檔案位置
    # ./kubo/s/n46/diary/MEMBER/list?page=9&ct=36753&cd=MEMBER
    n_url = re_ima_set_folder_path(re_domain)

    # 加附檔名
    # ./kubo/s/n46/diary/MEMBER/list?&page=0&ct=36753&cd=MEMBER.html
    html_url = add_html(n_url)

    other_domain = re.compile(r"^https")
    if other_domain.match(re_domain):
        return []

    # 加 domain
    # https://www.nogizaka46.com/s/n46/diary/MEMBER/list?&page=0&ct=36753&cd=MEMBER.html
    domain_url = add_domain(re_domain)
    # 檔案在第幾層資料夾
    path_level: int = get_level(n_url)
    # headers = {
    #   'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
    #   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    #   'Cookie': '__utmc=174951741; _ga=GA1.2.506322615.1645072246; __td_signed=true; _ts_yjad=1645072246687; WAPID=XOYHQ5FIIfOu94E1O0LNfrQl3cB8hGKJMkd; wap_last_event=showWidgetPage; wovn_uuid=kle42u84z; wovn_selected_lang=ja; S5SI=8plt3b79g2ulu8evr6id44070conk929; __utmz=174951741.1653654036.14.8.utmcsr=dlvr.it|utmccn=(not%20set)|utmcmd=twitter; _gcl_au=1.1.692994152.1653654036; 9DD31CEFD6719ABA=248fe041c8c7de9b23633326713fdc8b4698d96b; __utma=174951741.506322615.1645072246.1656607496.1656832205.43; __utmt=1; __utmb=174951741.1.10.1656832205; _gid=GA1.2.299101591.1656832205; _td=4991f6ef-bf12-4aa5-a95b-315fd89d01e8'
    # }
    # request = urllib.request.Request(url=domain_url, headers=headers)
    # response = urllib.request.urlopen(request)
    response = requests.get(url=domain_url, )
    # 設定編碼格式
    response.encoding = 'UTF-8'
    origin_html = response.text

    soup = BeautifulSoup(origin_html, 'lxml')

    # 圖片
    # data-src="https://www.nogizaka46.com/images/46/445/60cae08cc551e45e9d8aa008f871c.jpg"
    # ->
    # style="background-image: url("https://www.nogizaka46.com/images/46/445/60cae08cc551e45e9d8aa008f871c.jpg");"
    data_src = soup.find_all(attrs={'data-src': True})

    for data in data_src:
        # 取得 data-src 屬性
        src = data['data-src']
        download_path(src)
        local_path = replace_domain(src, EMPTY)
        local_path = get_data_path(local_path, path_level)
        style = 'background-image: url(' + local_path + ');'
        data['style'] = style

        # 加上 is-l

        class_list: list = data['class']
        class_list.append('is-l')
        new_class = ' '.join(class_list)
        data['class'] = new_class
        # style = 'background-image: url("' + src + '";)'
        # data['style'] = style

    # 取得所有 class
    # clazz: bl--card js-pos a--op hv--thumb
    def get_class_list(clazz):
        clazz_finder = '.' + re.sub(r" ", '.', clazz)
        list = soup.select(clazz_finder)
        return list

    def replace_class(clazz: str):
        list = get_class_list(clazz)
        for item in list:
            item['class'] = clazz + ' is-v'

    def replace_class_by_list(clazz, list):
        for item in list:
            item['class'] = clazz + ' is-v'

    # 等待下載清單: /s/n46/diary/detail/100091?ima=4435&cd=MEMBER
    wait_download = []

    def set_new_link_and_wait_download(html_list: list):
        for html in html_list:
            # 下載新頁面
            link = html['href']
            print('下載新頁面: ', link)
            wait_download.append(link)
            new_link = re_link_path(link, path_level)
            html_path = add_html(new_link)
            re_html_path = replace_reg_text(html_path)
            html['href'] = re_html_path

    # 頁面 list ------------------------------------------------------------
    # class="bl--card js-pos a--op hv--thumb"
    # ->
    # class="bl--card js-pos a--op hv--thumb is-v"
    blog_class = 'bl--card js-pos a--op hv--thumb'
    blog_list = get_class_list(blog_class)
    replace_class_by_list(blog_class, blog_list)
    # 移除連結 ima 參數，加入下載清單，替換連結
    set_new_link_and_wait_download(blog_list)

    # blog 標題
    title_class = 'bd--hd__ttl f--head a--tx js-tdi'
    title_list = get_class_list(title_class)
    replace_class_by_list(title_class, title_list)

    date_class = 'bd--hd__date a--tx js-tdi is-v'
    date_list = get_class_list(date_class)
    replace_class_by_list(date_class, date_list)

    # new entry blog
    new_entry = soup.select('.bd--ne__one__a.hv--op')
    set_new_link_and_wait_download(new_entry)
    view_new = soup.select('.bd--ne__btn__a m--fic.hv--op')
    set_new_link_and_wait_download(view_new)

    # 前の記事 bd--hn__a hv--op
    next_blog = soup.select('.bd--hn__a.hv--op')
    set_new_link_and_wait_download(next_blog)
    # BLOG底部 m--pnv__a m--fic hv--op
    footer_blog = soup.select('.m--pnv__a.m--fic.hv--op')
    set_new_link_and_wait_download(footer_blog)
    # 日曆 calender blog
    # calender_blog = soup.select('td a')
    # set_new_link_and_wait_download(calender_blog)
    # 大頭相
    header = soup.select('.bd--prof__img.m--fic.hv--op')
    set_new_link_and_wait_download(header)
    # title
    title = soup.select('.m--allhd__ja__a.hv--op')
    set_new_link_and_wait_download(title)

    # js_new_ver <div class="b--ld" id="js-ld"> 擋住
    blds: ResultSet[Tag] = soup.select('.b--ld')
    blds[0] = blds[0].decompose()

    # 替換 dcimg 到 <img>
    a_link = soup.select('a')
    dc_img_paths = []
    for link in a_link:
        reg = re.compile('.*dcimg.*')
        if reg.match(str(link)):
            # url: http://dcimg.awalker.jp/v/TBW3s78it3wcC9OXcPugfpOCfR0aALu1V5B3ezGQ5MwA1ybuj0iORLLQ7xNpv7IA724oeWQcEPcwA53gyeLTI5hrSzE38OBgpBt6yjiosCzY4rLAYqTxCnUGgzLvElzq7SzKn9QF3mmSaAWw8j5WKVStUZWdJJkkk0kLTmrW45fI4xJaACN9YlOWMTYdlPhSebpMo6gM
            # 連結失效跳過
            if is_err_dcimg(link['href']):
                link['href'] = ''
                continue
            url = link['href']
            # path = download_dc_page(url)
            wait_download.append(url)
            path = re.sub(r"http://dcimg\.awalker\.jp/v", '/i', url) + '.png'
            l_path = get_data_path(path, path_level)
            dc_img_paths.append(l_path)
            link['href'] = l_path

    # img
    # src="/images/46/ac5/8b0421d858a5cc0abe8d40ba31903.jpg"
    imgs = soup.select('img')
    i = 0
    for img in imgs:
        reg = re.compile('.*src.*')
        if reg.match(str(img)):
            img_url = img['src']
            wait_download.append(img_url)
            new_link = get_data_path(img_url, path_level)
            # l_path = dc_img_paths[i]
            img['src'] = new_link
            i = i + 1

    # 顯示
    # blog 標題
    # class="m--allhd js-pos js-tdg is-v"
    # footer
    # class="b--ft__nv js-pos js-tdg is-v"
    # class="b--ft__sns js-pos js-tdg is-v"
    # class="b--ft__sub js-pos js-tdg is-v"
    replace_class('m--allhd js-pos js-tdg')
    replace_class('b--ft__nv js-pos js-tdg')
    replace_class('b--ft__sns js-pos js-tdg')
    replace_class('b--ft__sub js-pos js-tdg')
    # 大頭 right
    # class="bd--prof js-pos a--op is-v"
    replace_class('bd--prof js-pos a--op')
    # 日曆
    # class="bd--arc js-pos a--op js-arccl is-v"
    replace_class('bd--arc js-pos a--op js-arccl')
    # 分頁 ------------------------------------------------------------
    # class="bl--pg js-pos a--op is-v"
    replace_class('bl--pg js-pos a--op')

    # 頁碼
    page_list = soup.select('.coun a')
    set_new_link_and_wait_download(page_list)

    # 下一頁
    next_page = soup.select('.next a')
    set_new_link_and_wait_download(next_page)

    # 前一頁
    prv_page = soup.select('.prev a')
    set_new_link_and_wait_download(prv_page)

    # 最前、後
    pager_page = soup.select('._pager a')
    set_new_link_and_wait_download(pager_page)

    # js
    #     <script src="/files/46/assets/js/lib.js" defer></script>
    #     <script src="/files/46/assets/js/vndr2.js" defer></script>
    #     <script src="/files/46/assets/js/app2.js" defer></script>
    js = soup.find_all('script', src=True)

    def download_replace_same(path: str, attr: str, label):
        # download_path(path)
        wait_download.append(path)
        attr_path = get_data_path(path, path_level)
        label[attr] = attr_path

    for j in js:
        # 取得網址
        path = j['src']
        download_replace_same(path, 'src', j)
    # css
    # <link rel="preload" href="/files/46/assets/fonts/icons.woff2" as="font" type="font/woff2" crossorigin>
    # <link rel="preload" as="style" href="/files/46/assets/css/style2.css" onload="this.onload = null; this.rel='stylesheet';">
    link_list = soup.find_all('link',
                              attrs={
                                  "rel": ["preload", "apple-touch-icon", "icon",
                                          "manifest", "mask-icon"]})
    for link in link_list:
        path = link['href']
        download_replace_same(path, 'href', link)

    # 儲存 html
    download_html(html_url, soup.prettify())

    return wait_download


# 區分url
def dis_urls(urls: list):
    reg = re.compile('.*cd=MEMBER|.*ima=.*')
    html_url = []
    oth_url = []
    for url in urls:
        if reg.match(url):
            html_url.append(url)
        else:
            oth_url.append(url)
    u = all_url.all_url()
    u.html = html_url
    u.oth = oth_url
    return u


# download_file('./files/46/assets/css/style2.css', 'https://www.nogizaka46.com/files/46/assets/css/style2.css')
# download_file('./files/46/diary/n46/MEMBER/0001_10.jpeg', 'https://www.nogizaka46.com/files/46/diary/n46/MEMBER/0001_10.jpeg')

# clazz_finder = '.' + re.sub(r" ", '.', 'm--allhd js-pos js-tdg')

# download_file('./files/46/diary/n46/MEMBER/0000_11.jpeg', 'https://www.nogizaka46.com/files/46/diary/n46/MEMBER/0000_11.jpeg')

# url = './files/46/diary/n46/MEMBER/0000_11.jpeg'
# arr = url.split('/')
# last = arr[len(arr) - 1]
# reg = '/' + last
# new = re.sub(reg, '', url)


# path = replace_domain(
#     'https://www.nogizaka46.com/files/46/diary/n46/MEMBER/0000_11.jpeg', '')


def get_file_name(date, name):
    # get file path: "秋元真夏 blog 221105-1"
    name_formate = re.sub(r" ", '', name)
    print('name_formate: ', name_formate)
    date_formate = date[2: 10]  # 22.11.05
    date_formate = re.sub(r"\.", '', date_formate)  # 221105
    print('date_formate: ', date_formate)
    formate = name_formate + ' blog ' + date_formate
    return formate
