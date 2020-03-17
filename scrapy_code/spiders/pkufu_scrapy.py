# -*- coding: utf-8 -*-
from urllib import parse

import scrapy
from scrapy.http import Request

from scrapy_code.items import PkufuItem, PkufuItemLoader
from scrapy_code.utils.common import get_md5


class PkufuScrapySpider(scrapy.Spider):
    name = 'pkufu_scrapy'
    allowed_domains = ['www.pkufh.com']
    start_urls = ['https://www.pkufh.com/Html/News/Columns/1306/Index.html/']

    def parse(self, response):
        # 科普文章入口url
        article_url = response.css("#249::attr(href)").extract_first("")
        yield Request(url=parse.urljoin(response.url, article_url), callback=self.parse_article)

        # 科普视频入口url
        video_url = response.css("#250::attr(href)").extract_first("")
        yield Request(url=parse.urljoin(response.url, video_url), callback=self.parse_video)
        pass

    # 解析科普文章列表
    def parse_article(self, response):
        # 解析列表中的所有文章url并交给scrapy下载后解析
        # todo:对获取失败的url（404……）进行处理
        post_nodes = response.css(".dy_title")
        for post_node in post_nodes:
            url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, url), callback=self.parse_article_detail)

        # 提取下一页交给scrapy下载
        next_url = response.css(".pagination_nextpage::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse_article)
        pass

    # 解析科普视频列表
    def parse_video(self, response):
        # 解析列表中的所有url并交给scrapy下载后解析
        # todo:对获取失败的url（404……）进行处理
        post_nodes = response.css(".img_video")
        for post_node in post_nodes:
            img_url = post_node.css("a.video_img img::attr(src)").extract_first("")
            post_url = post_node.css("a.video_btn::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_img_url": img_url},
                          callback=self.parse_video_detail)

        # 提取下一页交给scrapy下载
        next_url = response.css(".pagination_nextpage::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse_video)
        pass

    # 解析科普文章内容
    def parse_article_detail(self, response):
        # 通过item_loader加载item
        item_loader = PkufuItemLoader(item=PkufuItem(), response=response)
        item_loader.add_css("title", ".article_title font::text")
        item_loader.add_css("post_date", ".time::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_img_url", [])
        # item_loader.add_css("count", ".count span::text")
        item_loader.add_css("content", "div.article_cont")

        article_item = item_loader.load_item()

        yield article_item


    # 解析科普视频内容
    def parse_video_detail(self, response):
        front_img_url = response.meta.get("front_img_url", "") #视频封面图
        item_loader = PkufuItemLoader(item=PkufuItem(), response=response)
        item_loader.add_css("title", ".sp_title font::text")
        item_loader.add_css("post_date", ".sub_sptit span::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_img_url", [front_img_url])
        item_loader.add_value("content", "")

        video_item = item_loader.load_item()

        yield video_item


