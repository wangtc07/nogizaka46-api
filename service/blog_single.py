import base64

import re
import requests
from bs4 import BeautifulSoup
from utils import utils
from utils.file_utils import modify_file_time


def get_base64(url: str):
    response = requests.get(url=url)
    content = response.content
    data = str(base64.b64encode(content), "utf-8")
    # 轉換base64後加上前綴
    data = 'data:image/jpeg;base64,' + data
    return data


def get_photo_base64(src):
    match = utils.domain_pattern.match(src)
    if match:
        data = get_base64(src)
        return data
    else:
        download_src = utils.DOMAIN + src
        return get_base64(download_src)


def download(url):
    # 替換 domain, 移除 https://www.nogizaka46.com -> /s/n46/diary/detail/100415?ima=2618
    re_domain = utils.replace_domain(url, '')

    # 移除連結 ima 參數, 取得檔案下載位置, -> /s/n46/diary/detail/100415
    n_url = utils.re_ima_set_folder_path(re_domain)

    # 加上 .html 副檔名 -> /s/n46/diary/detail/100415.html
    html_url = utils.add_html(n_url)

    # 加 domain
    # https://www.nogizaka46.com/s/n46/diary/detail/100415?ima=2618
    domain_url = utils.add_domain(re_domain)

    # 取得回應
    response = requests.get(url=domain_url, )
    # 設定編碼格式
    response.encoding = 'UTF-8'
    # 取得 html
    origin_html = response.text

    soup = BeautifulSoup(origin_html, 'lxml')

    # # 取得所有 class
    # # clazz: bl--card js-pos a--op hv--thumb
    def get_class_list(clazz):
        clazz_finder = '.' + re.sub(r" ", '.', clazz)
        list = soup.select(clazz_finder)
        return list

    #
    def replace_class(clazz: str):
        list = get_class_list(clazz)
        for item in list:
            item['class'] = clazz + ' is-v'

    #
    def replace_class_by_list(clazz, list):
        for item in list:
            item['class'] = clazz + ' is-v'

    # 檔名及路徑
    titles = soup.select('title')
    # 日期
    date_class = 'bd--hd__date a--tx js-tdi'
    date_list = get_class_list(date_class)
    date_str = date_list[0].text

    html_url = './' + date_str + ' ' + titles[0].text + '.html'

    # 圖片
    # data-src="https://www.nogizaka46.com/images/46/445/60cae08cc551e45e9d8aa008f871c.jpg"
    # ->
    # style="background-image: url("https://www.nogizaka46.com/images/46/445/60cae08cc551e45e9d8aa008f871c.jpg");"
    data_src = soup.find_all(attrs={'data-src': True})

    for data in data_src:
        # 取得 data-src 屬性
        src: str = data['data-src']
        # utils.download_path(src)
        # 轉 base64
        base64_data = get_photo_base64(src)

        style = 'background-image: url(' + base64_data + ');'
        data['style'] = style

        # 加上 is-l
        class_list: list = data['class']
        class_list.append('is-l')
        new_class = ' '.join(class_list)
        data['class'] = new_class

    # blog 標題
    title_class = 'bd--hd__data js-pos js-tdg'
    title_list = get_class_list(title_class)
    replace_class_by_list(title_class, title_list)

    # js_new_ver <div class="b--ld" id="js-ld"> 擋住
    blds = soup.select('.b--ld')
    blds[0].decompose()

    # img
    # src="/images/46/ac5/8b0421d858a5cc0abe8d40ba31903.jpg"
    imgs = soup.select('img')
    i = 0
    for img in imgs:
        reg = re.compile('.*src.*')
        if reg.match(str(img)):
            img_url = img['src']
            # 轉 base64
            base64_data = get_photo_base64(img_url)
            # wait_download.append(img_url)
            # new_link = utils.get_data_path(img_url, path_level)
            # l_path = dc_img_paths[i]
            img['src'] = base64_data
            i = i + 1
    #
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

    js = soup.find_all('script', src=True)

    # def download_replace_same(path: str, attr: str, label):
    # download_path(path)
    # wait_download.append(path)
    # attr_path = utils.get_data_path(path, path_level)
    # label[attr] = attr_path

    # 取得 js css 檔案
    for j in js:
        # 取得網址
        path = j['src']
        reg = re.compile(r'.*vndr.*')
        if reg.match(path):
            print(path)
            vndr = open('./help/vndr.js', encoding='UTF-8')
            j.string = vndr.read()
            # src 標籤清除
            j['src'] = ''
        # download_replace_same(path, 'src', j)
    # # css
    # # <link rel="preload" href="/files/46/assets/fonts/icons.woff2" as="font" type="font/woff2" crossorigin>
    # # <link rel="preload" as="style" href="/files/46/assets/css/style2.css" onload="this.onload = null; this.rel='stylesheet';">
    link_list = soup.find_all('link',
                              attrs={
                                  "rel": ["preload", "apple-touch-icon", "icon",
                                          "manifest", "mask-icon"]})

    # 創建 style 標籤
    css = open('./help/style2.css', encoding='UTF-8')

    style_tag = soup.new_tag('style')
    style_tag.string = css.read()
    # Appending new style to html tree
    soup.html.body.append(style_tag)

    #
    # 儲存 html
    print(html_url)
    utils.download_html(html_url, soup.prettify())

    # 修改日期
    modify_file_time(html_url, date_str)
    #
    # return wait_download
