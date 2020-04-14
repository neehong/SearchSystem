# -*- coding: utf-8 -*-
# @Time    : 2020/4/14 6:34 下午
# @Author  : Neehong
# @FileName: es_types.py
# @Software: PyCharm

from datetime import datetime
from elasticsearch_dsl import Document, Date, Nested, Boolean, \
    analyzer, InnerDoc, Completion, Keyword, Text
from elasticsearch_dsl import connections
from elasticsearch_dsl.analysis import CustomAnalyzer
from w3lib.html import remove_tags


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

es = connections.create_connection(hosts=["127.0.0.1"])


def gen_suggests(index, info_tuple):
    # 根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text,weight in info_tuple:
        if text:
            #调用es的analyze接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word",params={"filter": ["lowercase"]}, body=text)
            anylyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = anylyzed_words - used_words
        else:
            new_words = set()
        if new_words:
            suggests.append({'input': list(new_words), 'weight': weight})
        return suggests


class ArticleType(Document):
    class Index:
        name = 'article'
        # settings = {
        #     "number_of_shards": 2,
        #     "number_of_replicas": 1
        # }

    # 文章和视频通用
    url = Keyword
    url_object_id = Keyword()
    title = Text(analyzer="ik_max_word")
    source = Text(analyzer="ik_max_word")
    date = Date()
    # 文章特有
    author = Text()
    dSource = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    suggest = Completion(analyzer=ik_analyzer)  # 搜索建议

    def __init__(self, item):
        super(ArticleType, self).__init__()
        self.assign(item)

    def assign(self, item):
        keys = ["url", "title", "source", "date", "author", "dSource", "content", "url_object_id"]
        for key in keys:
            try:
                item[key]
            except:
                item[key] = ""
        self.url = item["url"]
        self.title = item["title"]
        self.source = item["source"]
        self.date = item["date"]
        self.author = item["author"]
        self.dSource = item["dSource"]
        self.content = remove_tags(item["content"])
        self.meta.id = item["url_object_id"]
        self.suggest = gen_suggests(ArticleType.Index, ((self.title, 10), (self.author, 3), (self.dSource, 4)))


class VideoType(Document):
    class Index:
        name = 'video'
        # settings = {
        #     "number_of_shards": 2,
        #     "number_of_replicas": 1
        # }

    # 文章和视频通用
    url = Keyword
    url_object_id = Keyword()
    title = Text(analyzer="ik_max_word")
    source = Text(analyzer="ik_max_word")
    date = Date()
    # 视频特有
    img_url = Keyword()
    suggest = Completion(analyzer=ik_analyzer)  # 搜索建议

    def __init__(self, item):
        super(VideoType, self).__init__()
        self.assign(item)

    def assign(self, item):
        keys = ["url", "title", "source", "date", "url_object_id", "img_url"]
        for key in keys:
            try:
                item[key]
            except:
                item[key] = ""
        self.url = item["url"]
        self.title = item["title"]
        self.source = item["source"]
        self.date = item["date"]
        self.meta.id = item["url_object_id"]
        self.img_url = item["img_url"]
        self.suggest = gen_suggests(VideoType.Index, ((self.title, 10), (self.source, 2)))


if "__name__" == "__main__":
    # 插入article数据
    ArticleType.init()
    VideoType.init()


