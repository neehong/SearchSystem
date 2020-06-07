# 介绍
基于各大医院以及健康资讯网站的爬取数据，构建的一个”健康知识搜索引擎“

# Vue+Django框架搭建
## 一、安装vue

### 设置镜像
```
lemonqueendeMacBook-Pro:front_spider_medical lemon$ sudo npm install -g cnpm --registry=https://registry.npm.taobao.org
/usr/local/bin/cnpm -> /usr/local/lib/node_modules/cnpm/bin/cnpm
+ cnpm@6.1.1
added 685 packages from 957 contributors in 26.586s
```

### 确认cnpm安装成功
```
lemonqueendeMacBook-Pro:front_spider_medical lemon$ cnpm -v
cnpm@6.1.1 (/usr/local/lib/node_modules/cnpm/lib/parse_argv.js)
npm@6.14.5 (/usr/local/lib/node_modules/cnpm/node_modules/npm/lib/npm.js)
node@12.17.0 (/usr/local/bin/node)
npminstall@3.27.0 (/usr/local/lib/node_modules/cnpm/node_modules/npminstall/lib/index.js)
prefix=/usr/local 
darwin x64 18.7.0 
registry=https://r.npm.taobao.org
```

### 安装vue脚手架
```
lemonqueendeMacBook-Pro:front_spider_medical lemon$ sudo cnpm install -g @vue/cli
```

### vue安装成功
```
lemonqueendeMacBook-Pro:front_spider_medical lemon$ vue --version
@vue/cli 4.4.1

lemonqueendeMacBook-Pro:front_spider_medical lemon$ cd front_healthscience
cnpm install
cnpm install  vue-resource
cnpm install element-ui
pip install django-cors-headers
npm run dev
```

## 二、启动整个项目

```
1. 打开/Users/lemon/Documents/biancheng/elasticsearch-7.6.0/bin/elasticsearch
2. 运行Django（保证index和本地index名称一样）
lemonqueendeMacBook-Pro:front_spider_medical lemon$ python3 manage.py runserver 0.0.0.0:8000
3. 新建命令行运行vue
lemonqueendeMacBook-Pro:front_spider_medical lemon$ cd front_healthscience
npm run dev
```
# 前端Vue开发
详细见front_healthscience文件夹

# 后端Django开发
详细见backend_spider_medical文件夹
### 接口说明

1. 搜索提示：
* 对应功能点：搜索提示
* 请求方法：get
* 请求路径和参数：```/suggest/?s="搜索关键字"&s_type="搜索类型"）```
(参数说明：
搜索类型：0-疫情专区；1-科普文章；2-视频专区)
* 返回结果：json
```json
{
	"suggest":[……]
}
```

示例见```（新）SearchView返回结果.txt```文件

2.搜索关键字：
* 对应功能点：关键字搜索、热门搜索、结果列表展示+高亮关键字、信息源统计及分组展示、结果分页管理
* 请求方法：get
* 请求路径和参数：```/search/?q="搜索关键字"&s_type="搜索类型"&p="当前页数"）``` 
(参数说明：
搜索类型：0-疫情专区；1-科普文章；2-视频专区
当前页数：用于分页请求)
* 返回结果：
示例见```（新）SearchView返回结果.txt```文件


### 接口开发
1. “搜索提示”接口

第一版采用es的suggestor进行查询，但是由于前期在爬取数据前没有考虑周到，所以导致后期需要使用context suggestor时，要对原有es上的mapping和数据字段进行重建，耗时过久，所以最终采用了第二版

第二版采用如下的es查询语句：
```python
response = client.search(
                index=s_index,
                body={
                    "_source": {
                        "includes": ["title"]
                    },
                    "query": {
                          "bool": {
                            "must": {
                              "multi_match": {
                                "query": key_words,
                                "type": "phrase_prefix",
                                "fields": ["title^100000", "content"],
                                "operator": "OR"
                                }
                            },
                            "filter": {
                              "term": {
                                 "typee": s_type
                                  }
                              }
                          }
                    }
                }
            )
```
2. “搜索关键字”接口

采用如下的es查询语句：
```python
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
                            },
                            "filter": {
                                "term": {
                                    "typee": s_type  # 0-疫情专区，1-科普文章
                                }
                            }
                        }
                    },
                    "aggs": {
                        "my_aggs": {
                            "terms": {
                                "field": "source.keyword"  # todo:改为dSource
                            },
                            "aggs": {
                             "my": {
                               "top_hits": {
                                 "_source": ["title", "content", "date", "url"],
                                 "size": 100
                               }
                             }
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
```

3. 接口测试

* 启动es和kibana
* 在kibana上对对应接口的（search; suggest……）语句进行测试，直到返回结果正确
* 根据在kibana上测试好的语句完善view.py中的接口
* 启动Django项目，使用postman对后端接口进行测试


# 前后端测试
1. es数据准备

1）根据scrapy_code爬虫项目，往elasticsearch中存入数据，对应的index为aindex 和 vindex，详细字段说明如下：

**文章aindex**：包含”疫情专区"文章和普通“科普文章”
```python
	title = Text(analyzer="ik_max_word") #标题
    date = Date() #发布日期
    content = Text(analyzer="ik_max_word") #内容
    url = Keyword() #url
    dSource = Text(analyzer="ik_max_word") #来源
    source = Text(analyzer="ik_max_word") #网站
    author = Keyword()#作者
    typee = Integer()# 0疫情专区 1科普文章
    suggest = Completion(analyzer=ik_analyzer)  # 搜索建议，后已弃用
```
**视频vindex**：
```python
	title = Text(analyzer="ik_max_word") #标题
    date = Date()  # 发布日期
    url = Keyword() #url
    img_url = Keyword()
    source = Text(analyzer="ik_max_word") #网站
    suggest = Completion(analyzer=ik_analyzer)  # 搜索建议，后已弃用
```

2. 前后端跨域问题

修改`backend_spider_medical\backend_spider_medical\settings.py`文件

```
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
```

3. 后端测试接口

1）启动es
2）启动Django项目：python manage.py runserver
3）根据`backend_spider_medical\backend_app\views.py`文件提供的接口，使用postman测试

4. 前端测试后端接口

1）启动es
2）启动Django项目：python manage.py runserver
3）前端调用接口

# 其他说明
## 不停服修改es的mapping

见```不停服修改mapping.txt```文件

主要是在es上的已有数据量不多的情况下，且在不停掉爬虫和es下，修改现有的index的mapping，便于后续的es查询操作。
比如使用es的聚合(aggs)功能就需要声明聚合的字段为keyword类型
