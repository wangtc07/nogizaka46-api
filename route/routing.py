import os
import re
import time
import zipfile
from io import BytesIO

import requests
from flask import Blueprint, request, make_response, send_file, Response, jsonify

from service import blog_single, blog_single_photo

param = Blueprint('param', __name__)


@param.route('/data/appInfo/<name>', methods=['GET'])
def query_data_msg_by_name(name):
    print("type(name) : ", type(name))
    return 'String => {}'.format(name)


@param.route('/post', methods=['POST'])
def post_route():
    req: dict = request.json
    url = req.get('url')
    print(url)
    return url


@param.route('/get', methods=['GET'])
def get_route():
    url: str = request.args.get('url')
    print(url)
    return url


# 圖片直接顯示
@param.route('/img', methods=['GET'])
def down_img():
    img_data = open(os.path.join('./', 'test.jpg'), 'rb').read()
    print(type(img_data))  # bytes
    response = make_response(img_data)
    response.headers['Content-Type'] = 'image/png'
    return response


# 直接下載
@param.route('/img2', methods=['GET'])
def down_img2():
    return send_file('test.jpg', as_attachment=True,
                     download_name='test.jpg')


@param.route('/img3', methods=['GET'])
def down_img3():
    url = 'https://www.nogizaka46.com/files/46/diary/n46/MEMBER/moblog/202301/mobxi6DOY.jpg'
    response = requests.get(url=url)
    img_data: bytes = response.content
    resp = Response(img_data, mimetype="image/jpeg", direct_passthrough=True)
    return resp


@param.route('/img4', methods=['GET'])
def down_img4():
    url = 'https://www.nogizaka46.com/files/46/diary/n46/MEMBER/moblog/202301/mobxi6DOY.jpg'
    response = requests.get(url=url)
    img_data: bytes = response.content
    byio = BytesIO(img_data)

    return send_file(path_or_file=byio, as_attachment=True,
                     download_name='佐藤璃果 blog 230125-1.jpg')


@param.route('/zip', methods=['GET'])
def down_zip():
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        files = [f for f in os.listdir('./') if re.match('test.jpg', f)]
        for individualFile in files:
            zf.write(individualFile, compress_type=zipfile.ZIP_DEFLATED)  # 壓縮種類
        zf.close()
    memory_file.seek(0)  # 改變當前讀寫位置。如果將參數設為 0，則會將讀寫位置移動到流的開頭
    return send_file(memory_file, download_name='test.zip', as_attachment=True)


@param.route('/blog_single')
def blog_single_route():
    req: dict = request.json
    url = req.get('url')
    print(url)
    blog_single.download(url)
    return None


@param.route('/blog_single/photo', methods=['GET'])
def blog_single_photo_route():
    url: str = request.args.get('url')
    print(url)
    zip_rs = blog_single_photo.download(url)
    return send_file(zip_rs.zip_file, download_name=zip_rs.file_name, as_attachment=True)
