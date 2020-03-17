# -*- coding: utf-8 -*-
from urllib import parse

import scrapy
from scrapy.http import Request

from scrapy_code.items import PkufuItem, PkufuItemLoader
from scrapy_code.utils.common import get_md5


class PkufuScrapySpider(scrapy.Spider):
    name = 'pkufu_scrapy'
    allowed_domains = ['www.pkufh.com']
    start_urls = ['https://www.pkufh.com/Html/News/Columns/93/Index.html']

    def parse(self, response):
        """
        1. 获取文章列表中的文章url并交给scrapy下载后解析
        2. 获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        """

        # 解析列表中的所有文章url并交给scrapy下载后解析

        #todo:对获取失败的url（404……）进行处理

        post_nodes = response.css("a.dy_title")
        for post_node in post_nodes:
            url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, url), callback=self.parse_detail)

        # 提取下一页交给scrapy下载
        next_url = response.css(".pagination_nextpage::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
        pass

    def parse_detail(self, response):
        # 通过item_loader加载item
        item_loader = PkufuItemLoader(item=PkufuItem(), response=response)
        item_loader.add_css("title", ".article_title font::text")
        item_loader.add_css("post_date", ".time::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        # item_loader.add_css("count", ".count span::text")
        item_loader.add_css("content", "div.article_cont")

        article_item = item_loader.load_item()

        yield article_item

