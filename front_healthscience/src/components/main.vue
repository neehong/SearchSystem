<template>
  <div class="home"
       style="margin-top:0px">
    <div>
      <!-- 导航栏 -->
      <el-row class="demo-autocomplete top"
              justify="start"
              :gutter="20">
        <el-col :span='6'>
          <img src="../assets/logo.png"
               @click='goBack()'>
        </el-col>
        <!--加入导航 -->
        <el-col :span='14'>
          <el-tabs v-model="activeName"
                   @tab-click="handleClick">
            <el-tab-pane label="抗疫专线"
                         name="first">
              <el-row class="demo-autocomplete"
                      justify="center"
                      :gutter="20">
                <el-col :span="20">
                  <el-autocomplete class="inline-input"
                                   v-model="state1"
                                   :fetch-suggestions="querySearch"
                                   placeholder="请输入内容"
                                   :trigger-on-focus="false"
                                   @select="handleSelect"></el-autocomplete>
                </el-col>
                <el-col :span="4">
                  <el-button type="primary"
                             icon="el-icon-search"
                             @click="search2(state1,'0')">搜索</el-button>
                </el-col>
              </el-row>
            </el-tab-pane>
            <el-tab-pane label="健康科普"
                         name="second">
              <el-row class="demo-autocomplete"
                      justify="center"
                      :gutter="20">
                <el-col :span="20">
                  <el-autocomplete class="inline-input"
                                   v-model="state2"
                                   :fetch-suggestions="querySearch"
                                   placeholder="请输入内容"
                                   :trigger-on-focus="false"
                                   @select="handleSelect"></el-autocomplete>
                </el-col>
                <el-col :span="4">
                  <el-button type="primary"
                             icon="el-icon-search"
                             @click="search2(state2,'1')">搜索</el-button>
                </el-col>
              </el-row>
            </el-tab-pane>
            <el-tab-pane label="健康讲堂"
                         name="third">
              <el-row class="demo-autocomplete"
                      justify="center"
                      :gutter="20">
                <el-col :span="20">
                  <el-autocomplete class="inline-input"
                                   v-model="state3"
                                   :fetch-suggestions="querySearch"
                                   placeholder="请输入内容"
                                   :trigger-on-focus="false"
                                   @select="handleSelect"></el-autocomplete>
                </el-col>
                <el-col :span="4">
                  <el-button type="primary"
                             icon="el-icon-search"
                             @click="search2(state3,'2')">搜索</el-button>
                </el-col>
              </el-row>
            </el-tab-pane>
          </el-tabs>
        </el-col>
        <!-- 分割-->
      </el-row>
    </div>
    <el-row type="flex"
            class="row-bg"
            justify="center">
      <el-col :span="6"
              style="margin-top:50px">
        <!-- 数据来源 -->
        <ul id="source"
            style="margin-right: 130px;">
          <li class="subtitle">来源：</li>
          <li v-for="(source_list, index) in search_count"
              :key="index"
              class="tongji">
            <el-link type="primary"
                     @click="search(source_list.key)">{{ source_list.key }}: {{ source_list.count }}</el-link>
          </li>
        </ul>
      </el-col>
      <el-col :span='12'>
        <!-- 搜索主体 -->
        <div class="head_nums_cont_outer OP_LOG">
          <div class="nums">
            <span class="nums_text"
                  :model="total_nums">为您找到相关结果约{{total_nums}}个</span>
          </div>
        </div>
        <!-- 文章列表 -->
        <div id="content_left"
             v-if="flag_before == '1' || flag_before == '0'">
          <div :model="all_hits"
               class="result c-container"
               id="1"
               tpl="se_com_default"
               v-for="(hit,index) in all_hits"
               :key="index">
            <h3 class="t"
                style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
              <a :href="hit.url"
                 class="h3_m"
                 target="_blank"
                 v-html="hit.title"></a>
            </h3>
            <div class="c-abstract">
              <span class="newTimeFactor_before_abs m"
                    v-html="hit.content + '......'">&nbsp;&nbsp;
              </span>
            </div>
            <div class="f13">
              {{hit.date}}&nbsp;-&nbsp;相关得分：{{hit.score}}
            </div>
          </div>
        </div>
        <!--视频列表 -->
        <div id="content_left"
             v-if="flag_before == '2'">

          <div :model="all_hits"
               class="result c-container2"
               id="1"
               tpl="se_com_default"
               v-for="hit in all_hits"
               :key="hit">
            <h3 class="t"
                style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
              <a :href="hit.url"
                 target="_blank"
                 class="h3_m"
                 v-html="hit.title"></a>
            </h3>
            <div class="img_cover">
              <div>
                <img src="https://ss2.bdstatic.com/70cFvnSh_Q1YnxGkpoWK1HF6hhy/it/u=3400844705,3082504369&fm=15&gp=0.jpg"
                     height="120"
                     v-if="hit.img_url == ''" />
                <img :src="hit.img_url"
                     v-if="hit.img_url !== ''"
                     height="120">
              </div>
            </div>
            <div class="f13">
              {{hit.date}}&nbsp;-&nbsp;相关得分:{{hit.score}}
            </div>
          </div>
        </div>
        <!-- 翻页-->
        <el-pagination :model="total_nums"
                       @current-change="handleCurrentChange"
                       :current-page="currentPage"
                       :page-size="10"
                       layout="total, prev, pager, next, jumper"
                       :total="total_nums">
        </el-pagination>
      </el-col>
      <el-col :span="6">
        <!-- 热门搜索，我的搜索 -->
        <el-row style="margin-top:50px">
          <ul id="hotsearch">
            <li class="subtitle">热门搜索：</li>
            <li v-for="(search_words, index) in topn_search"
                :key="index"
                style="width: 300px;overflow: hidden;white-space: nowrap;text-overflow: ellipsis;"
                class="tongji">
              <a @click="search2(search_words,1)">{{ search_words }}</a>
            </li>
          </ul>
        </el-row>
        <el-row>
          <ul id="mysearch">
            <li class="subtitle">我的搜索：</li>
            <li v-for="(item, index) in mysearch"
                :key="index"
                style="width: 300px;overflow: hidden;white-space: nowrap;text-overflow: ellipsis;"
                class="tongji">
              <a @click="search2(item[0],item[1])">{{ item[0] }}</a>
            </li>
          </ul>
        </el-row>
      </el-col>
    </el-row>
  </div>
</template>
<script>
export default {
  data () {
    return {
      state1: '', // 搜索框
      state2: '',
      state3: '',
      activeName: 'second', // tab值
      queryString: '',
      flag: '', // 0:抗疫专题，1：健康科普，2：健康讲堂
      mysearch: [['', '']],
      results_show: [['']], // 结果列表
      topn_search: [],
      total_nums: 0,
      page_nums: 0,
      all_hits: [[]],
      hit: [],
      flag_before: '1',
      currentPage: 1,
      result_list: '',
      search_count: [[]]
    }
  },
  async created () {
    /**
     * 搜索建议
     * @param {String, String} s, s_type 关键字 queryString
     */
    // 根据queryString进行搜索
    this.queryString = this.$route.query.queryString
    this.flag_before = this.$route.query.flag
    if (this.flag_before === '0') {
      this.activeName = 'first'
      this.state1 = this.queryString
    } else if (this.flag_before === '1') {
      this.activeName = 'second'
      this.state2 = this.queryString
    } else {
      this.activeName = 'third'
      this.state3 = this.queryString
    }
    // 热门搜索
    // var top = await this.$http.get(this.globalVar.apiConfig.index.top)
    // this.topn_search = top.data.topn_search
    // localStorage.removeItem('mySearch')
    if (JSON.parse(localStorage.getItem('mySearch')).length > 0) {
      this.mysearch = JSON.parse(localStorage.getItem('mySearch'))
    }
    var showList = await this.$http.get(this.globalVar.apiConfig.index.search, { params: { q: this.queryString, p: this.currentPage, s_type: this.flag_before } })
    this.total_nums = showList.data.total_nums
    this.page_nums = showList.data.page_nums
    this.all_hits = showList.data.all_hits
    this.search_count = showList.data.search_count
    this.result_list = showList.data.result_list
    this.topn_search = showList.data.topn_search
    if (this.flag_before !== '2') {
      for (let i = 0; i < showList.data.all_hits.length; i++) {
        // this.all_hits[i].content = Html.fromHtml(this.all_hits[i].content).toString()
        if (this.all_hits[i].content.length > 200) {
          this.all_hits[i].content = this.all_hits[i].content.slice(0, 200)
        }
        // var reg = /<pre.+?>(.+)<\/pre>/g
        // var result = this.all_hits[i].match(reg)
        // this.all_hit[i].content = RegExp.$1
        // console.log(result)
      }
      // 根据queryString进行搜索
      // this.state1 = this.$route.params.queryString
      // this.flag = this.$route.params.flag
    }
  },
  methods: {
    /**
     * 搜索建议
     * @param {String, String} s, s_type 关键字 queryString
     */
    async querySearch (queryString, cb) {
      this.state1 = queryString
      var a
      if (this.activeName === 'first') {
        a = '0'
      } else if (this.activeName === 'second') {
        a = '1'
      } else {
        a = '2'
      }

      var title = await this.$http.get(this.globalVar.apiConfig.index.suggest, { params: { s: queryString, s_type: a } })
      var results = []
      for (let i = 0; i < title.data.suggest.length; i++) {
        var result = {}
        result['value'] = title.data.suggest[i]
        results.push(result)
      }
      // 调用 callback 返回建议列表的数据
      cb(results)
    },
    handleClick (tab, event) {
      console.log(tab, event)
    },
    /**
     * 搜索数据来源
     */
    search (source) {
      for (let i = 0; i < this.result_list.length; i++) {
        if (this.result_list[i].key === source) {
          this.all_hits = this.result_list[i].result
          this.total_nums = this.all_hits.length
        }
      }
    },
    /**
     * 搜索结果列表
     */
    async handleCurrentChange (val) {
      this.currentPage = val
      console.log(`当前页: ${val}`)
      var showList = await this.$http.get(this.globalVar.apiConfig.index.search, { params: { q: this.queryString, p: this.currentPage, s_type: this.flag_before } })
      console.log(showList)
      this.total_nums = showList.data.total_nums
      this.page_nums = showList.data.page_nums
      this.all_hits = showList.data.all_hits
      if (this.flag_before !== '2') {
        for (let i = 0; i < showList.data.all_hits.length; i++) {
          // this.all_hits[i].content = Html.fromHtml(this.all_hits[i].content).toString()
          if (this.all_hits[i].content.length > 200) {
            this.all_hits[i].content = this.all_hits[i].content.slice(0, 200)
          }
        }
      }
    },
    /**
     * 选择搜索提示内容item
     */
    handleSelect (item) {
      var a
      if (this.activeName === 'first') {
        a = '0'
      } else if (this.activeName === 'second') {
        a = '1'
      } else {
        a = '2'
      }
      this.search2(item.value, a)
    },
    /**
     * 返回上一次操作
     */
    goBack () {
      this.$router.push({
        name: 'index'
      })
    },
    findMySearch (queryString) {
      for (var i = 0; i < this.mysearch.length; i++) {
        if (this.mysearch[i][0] === queryString) {
          return true
        }
      }
      return false
    },
    search2 (queryString, flag) {
      if (!this.findMySearch(queryString)) {
        if (this.mysearch.length >= 5) {
          this.mysearch = this.mysearch.splice(1, 4)
        }
        this.mysearch.push([queryString, flag])
        localStorage.setItem('mySearch', JSON.stringify(this.mysearch))
      }
      this.$router.push({
        name: 'main',
        query: {
          queryString: queryString,
          flag: flag
        }
      })
      this.$router.go(0)
    }
  }
}
</script>

<style scoped>
.el-autocomplete {
  position: relative;
  display: block;
}
li {
  list-style-type: none;
}
.a,
a.m {
  color: #666;
  display: inline-block;
  text-align: left;
}
.c-abstract {
  font-size: 13px;
  text-align: left;
}
.c-abstract span {
  height: 62px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}
.c-container {
  width: 538px;
  font-size: 13px;
  line-height: 1.54;
  word-wrap: break-word;
  word-break: break-word;
}
h3 {
  display: block;
  font-size: 1.17em;
  -webkit-margin-before: 1em;
  -webkit-margin-after: 1em;
  -webkit-margin-start: 0px;
  -webkit-margin-end: 0px;
  font-weight: bold;
}
#content_left .result {
  width: 525px;
  margin-bottom: 14px;
  border-collapse: collapse;
}
.c-container {
  width: 638px;
  font-size: 13px;
  line-height: 1.54;
  word-wrap: break-word;
  word-break: break-word;
}
.result {
  width: 33.7em;
  table-layout: fixed;
}
user agent stylesheet div {
  display: block;
}
.nums {
  margin: 0 0 0 121px;
  height: 42px;
  line-height: 42px;
  font-size: 15px;
  color: #999;
}
.t {
  font-weight: 400;
  font-size: medium;
  margin-bottom: 1px;
  display: block;
  text-align: left;
}
span {
  text-align: left;
  margin-left: 0px;
}
.f13 {
  text-align: left;
  color: rgb(100, 211, 124);
}
.img_cover {
  /* float: left; */
  text-align: left;
  padding-left: 0px;
  display: inline;
}
.m >>> .keyWord {
  color: #ea0000;
}
.h3_m >>> .keyWord {
  color: #ea0000;
}
.tongji {
  /* float: left; */
  color: #993333;
  font-size: 15px;
  text-decoration: underline;
}
.subtitle {
  font-size: 18px;
}
</style>
