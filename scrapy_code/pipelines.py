# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy_code.models.es_types import ArticleType, VideoType


class ScrapyCodePipeline(object):
    def process_item(self, item, spider):
        return item


class ElasticsearchPipline(object):
    # 将数据写到es中
    def process_item(self, item, spider):
        # 将item装换为es的数据
        if item["type"] == "article":
            # 文章
            article = ArticleType(item)
            # article.url = item["url"]
            # article.title = item["title"]
            # article.source = item["source"]
            # article.date = item["date"]
            # article.author = item["author"]
            # article.dSource = item["dSource"]
            # article.content = remove_tags(item["content"])
            # article.meta.id = item["url_object_id"]
            article.save()
        else:
            # 视频
            video = VideoType(item)
            # video.url = item["url"]
            # video.title = item["title"]
            # video.source = item["source"]
            # video.date = item["date"]
            # video.meta.id = item["url_object_id"]
            # video.img_url = item["img_url"]
            video.save()
        return item



