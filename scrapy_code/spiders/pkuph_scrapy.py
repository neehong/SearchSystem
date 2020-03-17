# -*- coding: utf-8 -*-
# @Time    : 2020/3/17 5:26 下午
# @Author  : Neehong
# @FileName: pkuph_scrapy.py
# @Software: PyCharm

from urllib import parse

import scrapy
from scrapy.http import Request

from scrapy_code.items import PkufuItemLoader, PkufuItem
from scrapy_code.utils.common import get_md5



class PkuphScrapySpider(scrapy.Spider):
    """
    爬取"北京大学人民医院"中的"健康传播"（文章）、"健康视频"（视频）栏目内容
    1.由于文章列表和视频列表的css结构部分一致，所以将2个url都加入到start_urls中，同时进行爬取
    2.根据列表类型：健康新闻 or 健康视频 进入对应的detail_parser，获取相应的字段
    """

    name = 'pkuph_scrapy'
    allowed_domains = ['www.pkuph.cn']
    start_urls = ['https://www.pkuph.cn/Health_news.html', 'https://www.pkuph.cn/Health_video.html']

    def parse(self, response):
        # type-标记获取的下一页列表是新闻 还是 视频，再交由不同的parser进行detail处理
        type = response.meta.get("type", response.css("h1.pageTitle::text").extract_first(""))
        post_nodes = response.css(".newsList a")
        if type == "健康新闻":
            for post_node in post_nodes:
                url = post_node.css("::attr(href)").extract_first("")
                yield Request(url=parse.urljoin(response.url, url), callback=self.parse_article_detail)

            # 提取下一页列表给scrapy
            next_url = response.css(".page-box li:nth-last-child(2) a::attr(href)").extract_first("")
            if next_url:
                yield Request(url=parse.urljoin(response.url, next_url), meta={"type": type}, callback=self.parse)
        else:
            for post_node in post_nodes:
                url = post_nodes.css("::attr(href)").extract_first("")
                yield Request(url=parse.urljoin(response.url, url), callback=self.parse_video_detail)

            # 提取下一页给scrapy
            next_url = response.css(".page-box li:nth-last-child(2) a::attr(href)").extract_first("")
            if next_url:
                yield Request(url=parse.urljoin(response.url, next_url), meta={"type": type}, callback=self.parse)

    # 解析文章栏目
    def parse_article_detail(self,response):
        # 通过item_loader加载item
        item_loader = PkufuItemLoader(item=PkufuItem(), response=response)
        item_loader.add_css("title", ".l h1::text")
        item_loader.add_css("post_date", ".time::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_img_url", [])
        item_loader.add_css("content", ".content.xq")

        article_item = item_loader.load_item()
        yield article_item

    # 解析视频栏目
    def parse_video_detail(self, response):
        item_loader = PkufuItemLoader(item=PkufuItem(), response=response)
        item_loader.add_css("title", ".videoShow h1::text")
        item_loader.add_css("post_date", ".fl::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_img_url", [])
        item_loader.add_value("content", "")

        video_item = item_loader.load_item()
        yield video_item





