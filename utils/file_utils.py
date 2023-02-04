import io
import os
import time


# 修改檔案建立時間
def modify_file_time(file_path, time_str):
    datetime_obj = time.mktime(time.strptime(time_str, "%Y.%m.%d %H:%M"))
    file_info = os.stat(file_path)
    os.utime(file_path, (file_info.st_mtime, datetime_obj))
    os.utime(file_path, (file_info.st_ctime, datetime_obj))


def modify_file_time_by_byte(bio: bytes, time_str):
    datetime_obj = time.mktime(time.strptime(time_str, "%Y.%m.%d %H:%M"))
    os.utime(bio, (datetime_obj, datetime_obj))


def get_path(formate, i, path):
    file_path = path + '/' + formate + '-' + str(i) + '.jpg'
    return file_path
