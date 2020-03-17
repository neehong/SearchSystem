# -*- coding: utf-8 -*-
# @Time    : 2020/3/17 10:13 上午
# @Author  : Neehong
# @FileName: common.py
# @Software: PyCharm
import hashlib


def get_md5(url):
    if isinstance(url,str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

if __name__ == "__main__":
    print(get_md5("https://www.pkufh.com/Html/News/Articles/16617.html".encode("utf-8")))