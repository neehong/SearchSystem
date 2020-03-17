# -*- coding: utf-8 -*-
# @Time    : 2020/3/17 9:33 上午
# @Author  : Neehong
# @FileName: main.py
# @Software: PyCharm

from scrapy import cmdline

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
cmdline.execute(["scrapy","crawl","pkufu_scrapy"])