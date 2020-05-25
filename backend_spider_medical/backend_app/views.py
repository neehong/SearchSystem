import json
from django.shortcuts import render
from django.views.generic.base import View
from backend_app.models import ArticleType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
import redis
import datetime
# Create your views here.

client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis()

class IndexView(View):
    def get(self, request):
        # 统计热词Top5
        top_n_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        return render(request, "index.html", {"top_n_search": top_n_search})

#todo:更改爬虫中suggest对应部分的权重，title更大一点
class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        re_data = []
        if key_words:
            response = client.search(
                index="article",
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
                                    "fuzziness": 1
                                },
                                "size": 10,
                                "skip_duplicates": True
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


# /search/?q=" "&p="page_id"&s_type=" "
class SearchView(View):
    def get(self, request):
        # 获取搜索关键字
        key_words = request.GET.get("q", "")
        # 获取当前选择搜索的范围
        # s_type = request.GET.get("s_type", "51job")

        redis_cli.zincrby("search_keywords_set", 1, key_words)  # 该key_words的搜索记录+1
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)

        # 分页操作
        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1

        # todo：从redis查看该类数据总量
        # jobbole_count = redis_cli.get("article_count").decode('utf8')

        # 查询计时显示
        start_time = datetime.now()
        # 根据关键字查找
        response = client.search(
            index="article",
            body={
                "query": {
                    "multi_match": {
                        "query": key_words,
                        "fields": ["title", "coontent"] #todo:如果是视频检索则无content
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

        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        total_nums = response["hits"]["total"]['value']
        #计算总页数
        if (page % 10) > 0:
            page_nums = int(total_nums / 10) + 1
        else:
            page_nums = int(total_nums / 10)

        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = hit["_source"]["title"]
            if "content" in hit["content"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]
            else:
                hit_dict["content"] = hit["_source"]["content"][:500]

            hit_dict["date"] = hit["_source"]["date"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = hit["_score"]
            hit_dict["source"] = hit["source"]

            hit_list.append(hit_dict)

        return render(request, "result.html", {"page": page,
                                               "all_hits": hit_list,
                                               "key_words": key_words,
                                               "total_nums": total_nums,
                                               "page_nums": page_nums,
                                               "last_seconds": last_seconds,
                                               # "article_count": article_count,
                                               "topn_search": topn_search})
