<template>
  <div class="home">
    <div>
      <img src="../assets/logo.png">
    </div>
    <el-row type="flex"
            class="row-bg"
            justify="center">
      <el-col :span="12">
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
                           @click="search(state1,'0')">搜索</el-button>
              </el-col>
            </el-row>s
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
                           @click="search(state2,'1')">搜索</el-button>
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
                           @click="search(state3,'2')">搜索</el-button>
              </el-col>
            </el-row>
          </el-tab-pane>
        </el-tabs>
        <el-row justify="center"
                style="margin:100px auto 10px auto">
          <!-- 热门搜索 -->
          <el-col :span='10'>
            <ul id="hotsearch"
                :model='topn_search'>
              <li class="subtitle">热门搜索：</li>
              <li v-for="(search_words, index) in topn_search"
                  :key="index"
                  style="width: 250px;overflow: hidden;white-space: nowrap;text-overflow: ellipsis;"
                  class="tongji">
                <el-link type="primary"
                         @click="search(search_words,1)">{{ search_words }}</el-link>
              </li>
            </ul>
          </el-col>
          <!-- 我的搜索 -->
          <el-col :span='10'>
            <ul id="mysearch">
              <li class="subtitle">我的搜索：</li>
              <li v-for="(item,index) in mysearch"
                  :key="index"
                  style="width: 250px;overflow: hidden;white-space: nowrap;text-overflow: ellipsis;"
                  class="tongji">
                <a @click="search(item[0],item[1])">{{ item[0] }}</a>
              </li>
            </ul>
          </el-col>
        </el-row>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  data () {
    return {
      activeName: 'second',
      state1: '',
      state2: '',
      state3: '',
      mysearch: [['', '']],
      topn_search: []
    }
  },
  async created () {
    // 热门搜索
    var top = await this.$http.get(this.globalVar.apiConfig.index.top)
    this.topn_search = top.data.topn_search
    console.log(top.data.topn_search)
    // localStorage.removeItem('mySearch')
    if (JSON.parse(localStorage.getItem('mySearch')).length > 0) {
      this.mysearch = JSON.parse(localStorage.getItem('mySearch'))
    }
  },
  methods: {
    /**
     * 搜索建议
     * @param {String, String} s, s_type 关键字 queryString
     */

    async querySearch (queryString, cb) {
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
      console.log(title.data.suggest)
      for (let i = 0; i < title.data.suggest.length; i++) {
        var result = {}
        result['value'] = title.data.suggest[i]
        console.log(title.data.suggest[i])
        results.push(result)
      }
      // 调用 callback 返回建议列表的数据
      cb(results)
    },
    handleSelect (item) {
      var a
      if (this.activeName === 'first') {
        a = '0'
      } else if (this.activeName === 'second') {
        a = '1'
      } else {
        a = '2'
      }
      this.search(item.value, a)
    },
    handleClick (tab, event) {
      console.log(tab, event)
    },
    findMySearch (queryString) {
      for (var i = 0; i < this.mysearch.length; i++) {
        if (this.mysearch[i][0] === queryString) {
          return true
        }
      }
      return false
    },
    // 搜索-跳转至搜索列表展示页
    search (queryString, flag) {
      if (!this.findMySearch(queryString)) {
        console.log(this.mysearch.length)
        console.log(flag)
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
.tongji {
  /* float: left; */
  color: #993333;
  font-size: 16px;
  text-decoration: underline;
}
.subtitle {
  font-size: 18px;
}
</style>
