import json
from django.shortcuts import render
from django.views.generic.base import View
from backend_spider_medical.backend_app.models import ArticleType
from backend_spider_medical.util.myEncoder import MyEncoder
from django.http import HttpResponse
from elasticsearch import Elasticsearch
import redis
import re
import datetime
# Create your views here.

client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis()

# 查询类别代码s_type（疫情专区：0 科普文章：1 健康讲堂（视频专区）：2）
index_map = ['article', 'article', 'video']  # s_type(元素下标)和es中index（元素值）的对应关系：例如s_type(0)对应es中的index（'article'）


# /
class IndexView(View):
    def get(self, request):
        # 统计热词Top5
        top_n_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        return render(request, "index.html", {"top_n_search": top_n_search})


# /search/?s="查询关键字"&s_type="查询类别"，其中类别代码为（疫情专区：0 科普文章：1 健康讲堂（视频专区）：2）
class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        # 获取当前选择搜索的范围
        s_type = int(float(re.search(r'\d+', request.GET.get("s_type", 1)).group()))
        s_index = index_map[s_type]

        re_data = []
        if key_words:
            response = client.search(
                index=s_index,
                body={
                    "_source": {
                        "includes": ["title"]
                    },
                    "suggest": {
                        "my_suggest": {
                            "prefix": key_words,
                            "completion": {
                                "field": "suggest",
                                "fuzzy": {
                                    "fuzziness": 2
                                },
                                "size": 10,
                                # "skip_duplicates": True
                            }
                        }
                    }
                }
            )
            suggestions = response["suggest"]["my_suggest"][0]['options']
            for match in suggestions:
                source = match['_source']
                re_data.append(source["title"])
        return HttpResponse(json.dumps(re_data), content_type="application/json")


# /search/?q="查询关键字"&p="当前页数"&s_type="查询类别"
class SearchView(View):
    def get(self, request):
        # 获取搜索关键字
        key_words = request.GET.get("q", "")
        # 获取当前选择搜索的范围
        s_type = int(float(re.search(r'\d+', request.GET.get("s_type", 1)).group()))
        s_index = index_map[s_type]

        # 搜索源统计
        search_count = []

        redis_cli.zincrby("search_keywords_set", 1, key_words)  # 该key_words的搜索记录+1
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)

        # 分页操作
        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1

        # 查询计时显示
        start_time = datetime.datetime.now()
        # 分类别在对应的es里的index进行查询
        if s_index == "article":
            response = client.search(
                index="article",
                body={
                    "query": {
                        "bool": {
                            "must": {
                                "multi_match": {
                                    "query": key_words,
                                    "type": "best_fields",
                                    "fields": ["title^100", "content^50", "author^10", "dSource^30", "source^20"],
                                    "operator": "OR"
                                }
                            }
                            # , #todo:撤销注释，分类别查询
                            # "filter": {
                            #     "term": {
                            #         "typee": s_type  # 0-疫情专区，1-科普文章
                            #     }
                            # }
                        }
                    },
                    "aggs": {
                        "my_aggs": {
                            "terms": {
                                "field": "source.keyword"  # todo:改为dSource
                            }
                        }
                    },
                    "from": (page - 1) * 10,
                    "size": 10,
                    # 对关键字进行高光标红处理
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {
                            "title": {},
                            "content": {},
                        }
                    }
                }
            )
        else:
            response = client.search(
                index="video",
                body={
                    "query": {
                        "bool": {
                            "must": {
                                "multi_match": {
                                    "query": key_words,
                                    "type": "best_fields",
                                    "fields": ["title^100", "source^20"],
                                    "operator": "OR"
                                }
                            }
                        }
                    },
                    "aggs": {
                        "my_aggs": {
                            "terms": {
                                "field": "source.keyword"
                            }
                        }
                    },
                    "from": (page - 1) * 10,
                    "size": 10,
                    # 对关键字进行高光标红处理
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {
                            "title": {},
                            "content": {},
                        }
                    }
                }
            )

        end_time = datetime.datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        total_nums = response["hits"]["total"]['value']
        search_count = response["aggregations"]["my_aggs"]["buckets"]

        # 计算总页数
        if (page % 10) > 0:
            page_nums = int(total_nums / 10) + 1
        else:
            page_nums = int(total_nums / 10)

        hit_list = []

        if s_index == "article":  # 返回article的字段内容
            for hit in response["hits"]["hits"]:
                hit_dict = {}
                if "title" in hit["highlight"]:
                    hit_dict["title"] = "".join(hit["highlight"]["title"])
                else:
                    hit_dict["title"] = hit["_source"]["title"]

                if "content" in hit["highlight"]:
                    hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]
                else:
                    hit_dict["content"] = hit["_source"]["content"][:500]
                hit_dict["date"] = hit["_source"]["date"]
                hit_dict["url"] = hit["_source"]["url"]
                hit_dict["score"] = hit["_score"]
                hit_dict["dSource"] = hit["_source"]["dSource"]
                hit_list.append(hit_dict)

        else:  # 返回video的字段内容
            for hit in response["hits"]["hits"]:
                hit_dict = {}
                if "title" in hit["highlight"]:
                    hit_dict["title"] = "".join(hit["highlight"]["title"])
                else:
                    hit_dict["title"] = hit["_source"]["title"]
                hit_dict["date"] = hit["_source"]["date"]
                hit_dict["url"] = hit["_source"]["url"]
                hit_dict["score"] = hit["_score"]
                hit_dict["source"] = hit["source"]
                hit_list.append(hit_dict)

        return HttpResponse(json.dumps({"page": page,  # 当前页数
                                               "all_hits": hit_list,  # 文章列表及详细信息：包括title、author……
                                               "key_words": key_words,  # 查询关键字
                                               "total_nums": total_nums,  # 查询到的数据总条数
                                               "page_nums": page_nums,  # 总页数
                                               "last_seconds": last_seconds,  # 查询用时
                                               "search_count": search_count,  # 搜索源统计及数据
                                               "topn_search": topn_search}, cls=MyEncoder, indent=4), content_type="application/json")   # 热门搜索的title列表

        # return render(request, "result.html", {"page": page,  # 当前页数
        #                                        "all_hits": hit_list,  # 文章列表及详细信息：包括title、author……
        #                                        "key_words": key_words,  # 查询关键字
        #                                        "total_nums": total_nums,  # 查询到的数据总条数
        #                                        "page_nums": page_nums,  # 总页数
        #                                        "last_seconds": last_seconds,  # 查询用时
        #                                        "search_count": search_count,  # 搜索源统计及数据
        #                                        "topn_search": topn_search}  # 热门搜索的title列表
        #                                        )
