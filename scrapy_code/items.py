# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from w3lib.html import remove_tags


class ScrapyCodeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class SelfItemLoader(ItemLoader):
    # 自定义ItemLoader
    default_output_processor = TakeFirst()

def date_convert(value):
    match_re = re.match("(.*?)(\d{4}-\d{2}-\d{2}).*", value)
    if match_re:
        date_str = match_re.group(2)
    try:
        post_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        post_date = datetime.datetime.now().date()
    return post_date

def get_author(value):
    # 若无作者信息
    if value == "":
        return value
    # 有作者信息，需要提取
    match_re = re.match("(.*?)来源：(.*) 来源.*", value)
    if match_re:
        author = match_re.group(2).strip()
    else:
        return ""
    return author

def get_dSource(value):
    # 若无来源信息
    if value == "":
        return value
    # 有来源信息，进行提取
    match_re = re.match(".*来源：(.*?)($|\d.*)", value)
    if match_re:
        d_source = match_re.group(1).strip()
    else:
        return ""
    return d_source


def get_content(value):
    # 去除前后的空格,以及html标签
    result = str.strip(remove_tags(value))
    return result


def return_value(value):
    return value


class SelfItem(scrapy.Item):
    type = scrapy.Field()  # 标记是文章or视频
    # 文章和视频通用
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    source = scrapy.Field()
    date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    # 文章特有
    author = scrapy.Field(
        input_processor=MapCompose(get_author)
    )
    dSource = scrapy.Field(
        input_processor=MapCompose(get_dSource)
    )
    content = scrapy.Field(
        input_processor=MapCompose(get_content)
    )
    # 视频特有
    img_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
