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


class ScrapyCodeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class PkufuItemLoader(ItemLoader):
    # 自定义ItemLoader
    default_output_processor = TakeFirst()


def date_convert(value):
    match_re = re.match(".*(\d*-\d*-\d*)$", value)
    if match_re:
        date_str = match_re.group(1)
    try:
        post_date = datetime.datetime.striptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        post_date = datetime.datetime.now().date()
    return post_date


class PkufuItem(scrapy.Item):
    title = scrapy.Field()
    post_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    # count = scrapy.Field()  浏览次数js，无法获取
    content = scrapy.Field()

